// =================== CONFIGURATION ===================
const API_BASE = 'http://localhost:8000';

// État de l'application
const state = {
    nodes: [],
    edges: [],
    constraints: [],
    selectedNodes: [],
    mode: 'view',
    highlightedPath: [],
    zoom: 1,
    offset: { x: 0, y: 0 }
};

// =================== INITIALISATION ===================
document.addEventListener('DOMContentLoaded', () => {
    initializeEventListeners();
    loadGraph();
    loadConstraints();
});

// =================== EVENT LISTENERS ===================
function initializeEventListeners() {
    // Boutons d'édition
    document.getElementById('addNodeBtn').addEventListener('click', () => setMode('addNode'));
    document.getElementById('addEdgeBtn').addEventListener('click', () => setMode('addEdge'));
    document.getElementById('deleteNodeBtn').addEventListener('click', deleteNode); // UN SEUL bouton
    document.getElementById('clearGraphBtn').addEventListener('click', clearGraph);
    
    // Algorithmes
    document.getElementById('dijkstraBtn').addEventListener('click', runDijkstra);
    document.getElementById('coloringBtn').addEventListener('click', runColoring);
    
    // Contraintes
    document.getElementById('showConstraintsBtn').addEventListener('click', showConstraintsModal);
    document.getElementById('addConstraintBtn').addEventListener('click', showAddConstraintModal);
    document.getElementById('testConstraintBtn').addEventListener('click', showTestConstraintModal);
    document.getElementById('saveConstraintBtn').addEventListener('click', saveConstraint);
    document.getElementById('runTestConstraintBtn').addEventListener('click', runTestConstraint);
    
    // Historique
    document.getElementById('showHistoryBtn').addEventListener('click', showHistoryModal);
    
    // Canvas
    document.getElementById('graphCanvas').addEventListener('click', handleCanvasClick);
    
    // Zoom
    document.getElementById('zoomInBtn').addEventListener('click', () => zoom(1.2));
    document.getElementById('zoomOutBtn').addEventListener('click', () => zoom(0.8));
    document.getElementById('resetViewBtn').addEventListener('click', resetView);
}

// =================== MODE MANAGEMENT ===================
function setMode(newMode) {
    state.mode = newMode;
    state.selectedNodes = [];
    
    const modeIndicator = document.getElementById('modeIndicator');
    const modeTexts = {
        'view': 'Mode: Visualisation',
        'addNode': '➕ Mode: Ajouter un nœud (cliquez sur le canvas)',
        'addEdge': '🔗 Mode: Relier deux nœuds (sélectionnez 2 nœuds)'
    };
    
    modeIndicator.textContent = modeTexts[newMode] || 'Mode: Visualisation';
    modeIndicator.style.background = newMode === 'view' ? '#e3f2fd' : '#fff3cd';
    
    renderGraph();
}

// =================== API CALLS ===================
async function apiCall(endpoint, method = 'GET', body = null) {
    try {
        const options = {
            method,
            headers: { 'Content-Type': 'application/json' }
        };
        
        if (body) {
            options.body = JSON.stringify(body);
        }
        
        const response = await fetch(`${API_BASE}${endpoint}`, options);
        const data = await response.json();
        
        if (!response.ok) {
            throw new Error(data.error || 'Erreur API');
        }
        
        return data;
    } catch (error) {
        showToast(error.message, 'error');
        throw error;
    }
}

// =================== LOAD DATA ===================
async function loadGraph() {
    try {
        const data = await apiCall('/graph');
        state.nodes = data.nodes || [];
        state.edges = data.edges || [];
        
        updateStats();
        updateSelects();
        renderGraph();
    } catch (error) {
        console.error('Erreur chargement graphe:', error);
    }
}

async function loadConstraints() {
    try {
        const data = await apiCall('/constraints');
        state.constraints = data || [];
        updateStats();
    } catch (error) {
        console.error('Erreur chargement contraintes:', error);
    }
}

// =================== STATS ===================
function updateStats() {
    document.getElementById('nodeCount').textContent = state.nodes.length;
    document.getElementById('edgeCount').textContent = state.edges.length;
    document.getElementById('constraintCount').textContent = state.constraints.length;
}

function updateSelects() {
    const sourceSelect = document.getElementById('sourceSelect');
    const destSelect = document.getElementById('destSelect');
    const constraintSource = document.getElementById('constraintSource');
    const constraintTarget = document.getElementById('constraintTarget');
    
    const options = state.nodes.map(n => `<option value="${n.id}">${n.id}</option>`).join('');
    
    sourceSelect.innerHTML = '<option value="">-- Sélectionnez --</option>' + options;
    destSelect.innerHTML = '<option value="">-- Sélectionnez --</option>' + options;
    constraintSource.innerHTML = '<option value="">-- Sélectionnez --</option>' + options;
    constraintTarget.innerHTML = '<option value="">-- Sélectionnez --</option>' + options;
}

// =================== CANVAS INTERACTION ===================
function handleCanvasClick(e) {
    const svg = document.getElementById('graphCanvas');
    const rect = svg.getBoundingClientRect();
    const x = e.clientX - rect.left;
    const y = e.clientY - rect.top;
    
    if (state.mode === 'addNode') {
        addNodeAtPosition(x, y);
    }
}

async function addNodeAtPosition(x, y) {
    const nodeId = document.getElementById('nodeIdInput').value.trim();
    
    if (!nodeId) {
        showToast('Veuillez entrer un ID de nœud', 'warning');
        return;
    }
    
    try {
        // Capacité fixée à 0 par défaut (non exposée à l'utilisateur)
        await apiCall('/graph/node', 'POST', { id: nodeId, x, y, capacity: 0 });
        showToast(`Nœud ${nodeId} créé !`, 'success');
        document.getElementById('nodeIdInput').value = '';
        await loadGraph();
        setMode('view');
    } catch (error) {
        console.error('Erreur création nœud:', error);
    }
}

function handleNodeClick(nodeId) {
    if (state.mode === 'addEdge') {
        if (state.selectedNodes.includes(nodeId)) {
            state.selectedNodes = state.selectedNodes.filter(id => id !== nodeId);
        } else {
            state.selectedNodes.push(nodeId);
        }
        
        if (state.selectedNodes.length === 2) {
            createEdgeBetweenNodes(state.selectedNodes[0], state.selectedNodes[1]);
        } else {
            renderGraph();
        }
    }
}

async function createEdgeBetweenNodes(source, target) {
    const weight = prompt(`Distance entre ${source} et ${target} (km):`, '2.5');
    
    if (weight === null || weight === '') {
        state.selectedNodes = [];
        setMode('view');
        return;
    }
    
    try {
        await apiCall('/graph/edge', 'POST', { 
            source, 
            target, 
            weight: parseFloat(weight) 
        });
        showToast(`Arête ${source}-${target} créée !`, 'success');
        await loadGraph();
        setMode('view');
    } catch (error) {
        console.error('Erreur création arête:', error);
        state.selectedNodes = [];
        setMode('view');
    }
}

// =================== DELETE NODE (SMART PAR DÉFAUT) ===================
async function deleteNode() {
    const nodeId = prompt('ID du nœud à supprimer:');
    if (!nodeId) return;
    
    if (!confirm(`Supprimer le nœud ${nodeId} ?\n(Les raccourcis seront créés automatiquement pour préserver l'optimalité)`)) {
        return;
    }
    
    try {
        // Appel SMART par défaut
        const result = await apiCall(`/node/${nodeId}/smart`, 'DELETE');
        showToast(result.message, 'success');
        
        if (result.shortcuts_created > 0 || result.shortcuts_updated > 0) {
            showToast(`${result.total_shortcuts} raccourci(s) créé(s)/amélioré(s)`, 'info');
        }
        
        await loadGraph();
    } catch (error) {
        console.error('Erreur suppression:', error);
    }
}

async function clearGraph() {
    if (!confirm('Êtes-vous sûr de vouloir vider tout le graphe ?')) {
        return;
    }
    
    try {
        await apiCall('/graph', 'DELETE');
        showToast('Graphe vidé', 'success');
        await loadGraph();
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// =================== ALGORITHMS ===================
async function runDijkstra() {
    const source = document.getElementById('sourceSelect').value;
    const dest = document.getElementById('destSelect').value;
    
    if (!source || !dest) {
        showToast('Sélectionnez source et destination', 'warning');
        return;
    }
    
    try {
        const result = await apiCall(`/algo/dijkstra?src=${source}&dst=${dest}`);
        
        // Réinitialiser les couleurs de coloriage
        state.nodes.forEach(node => {
            delete node.color;
        });
        
        state.highlightedPath = result.path;
        renderGraph();
        
        const pathDisplay = document.getElementById('pathDisplay');
        const distanceDisplay = document.getElementById('distanceDisplay');
        const pathResult = document.getElementById('pathResult');
        
        pathDisplay.innerHTML = `<strong>Chemin:</strong> ${result.path.join(' → ')}`;
        distanceDisplay.innerHTML = `<strong>Distance:</strong> ${result.distance.toFixed(2)} km`;
        pathResult.style.display = 'block';
        
        // Cacher le résultat du coloriage
        document.getElementById('coloringResult').style.display = 'none';
        
        showToast('Chemin optimal calculé !', 'success');
    } catch (error) {
        console.error('Erreur Dijkstra:', error);
    }
}

async function runColoring() {
    try {
        // IMPORTANT : Réinitialiser le chemin surligné
        state.highlightedPath = [];
        
        const result = await apiCall('/algo/coloring');
        
        // Colorier les nœuds
        state.nodes.forEach(node => {
            node.color = result.coloring[node.id];
        });
        
        renderGraph();
        
        const coloringDisplay = document.getElementById('coloringDisplay');
        const coloringResult = document.getElementById('coloringResult');
        
        const colors = ['🔴', '🟢', '🟡', '🔵', '🟣', '🟠', '⚫', '⚪'];
        let html = `<strong>Nombre chromatique:</strong> ${result.chromatic_number} couleurs<br><br>`;
        
        for (let color in result.stats) {
            html += `${colors[color] || '⭕'} Couleur ${color}: ${result.stats[color]} nœuds<br>`;
        }
        
        coloringDisplay.innerHTML = html;
        coloringResult.style.display = 'block';
        
        // Cacher le résultat de Dijkstra
        document.getElementById('pathResult').style.display = 'none';
        
        showToast(`Graphe colorié avec ${result.chromatic_number} couleurs`, 'success');
    } catch (error) {
        console.error('Erreur coloriage:', error);
    }
}

// =================== CONSTRAINTS ===================
async function showConstraintsModal() {
    try {
        const constraints = await apiCall('/constraints/all');
        
        const constraintsList = document.getElementById('constraintsList');
        
        if (constraints.length === 0) {
            constraintsList.innerHTML = '<p class="info-text">Aucune contrainte définie</p>';
        } else {
            constraintsList.innerHTML = constraints.map(c => `
                <div class="constraint-card ${!c.is_active ? 'inactive' : ''}">
                    <div class="constraint-header">
                        <div class="constraint-route">${c.source} → ${c.target}</div>
                        <div class="constraint-value">+${c.constraint_value} km</div>
                    </div>
                    <div class="constraint-info">
                        <span>${c.reason || 'Sans raison'}</span>
                        <span>•</span>
                        <span>${c.expiry_days ? `Expire dans ${c.expiry_days}j` : 'Permanent'}</span>
                        <span>•</span>
                        <span>${c.is_active ? '✅ Active' : '❌ Inactive'}</span>
                    </div>
                    ${c.expires_at ? `<div style="font-size: 0.8rem; color: #666;">Expire le: ${new Date(c.expires_at).toLocaleDateString()}</div>` : ''}
                    <div class="constraint-actions">
                        <button class="btn btn-${c.is_active ? 'warning' : 'success'} btn-small" 
                                onclick="toggleConstraint(${c.id}, ${!c.is_active})">
                            ${c.is_active ? '⏸️ Désactiver' : '▶️ Activer'}
                        </button>
                    </div>
                </div>
            `).join('');
        }
        
        openModal('constraintsModal');
    } catch (error) {
        console.error('Erreur:', error);
    }
}

function showAddConstraintModal() {
    updateSelects();
    openModal('addConstraintModal');
}

async function saveConstraint() {
    const source = document.getElementById('constraintSource').value;
    const target = document.getElementById('constraintTarget').value;
    const value = parseFloat(document.getElementById('constraintValue').value);
    const reason = document.getElementById('constraintReason').value;
    const expiry = parseInt(document.getElementById('constraintExpiry').value) || null;
    
    if (!source || !target || !value) {
        showToast('Remplissez tous les champs requis', 'warning');
        return;
    }
    
    try {
        await apiCall('/constraints', 'POST', {
            source,
            target,
            constraint_value: value,
            reason: reason || null,
            expiry_days: expiry
        });
        
        showToast('Contrainte créée !', 'success');
        closeModal('addConstraintModal');
        await loadConstraints();
        await loadGraph();
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function toggleConstraint(constraintId, newState) {
    try {
        await apiCall(`/constraints/${constraintId}/toggle`, 'PUT', {
            is_active: newState
        });
        
        showToast(`Contrainte ${newState ? 'activée' : 'désactivée'}`, 'success');
        await showConstraintsModal();
        await loadConstraints();
        await loadGraph();
    } catch (error) {
        console.error('Erreur:', error);
    }
}

function showTestConstraintModal() {
    openModal('testConstraintModal');
}

async function runTestConstraint() {
    const edge = document.getElementById('tempConstraintEdge').value.trim();
    const value = parseFloat(document.getElementById('tempConstraintValue').value);
    const source = document.getElementById('sourceSelect').value;
    const dest = document.getElementById('destSelect').value;
    
    if (!edge || !value || !source || !dest) {
        showToast('Remplissez tous les champs', 'warning');
        return;
    }
    
    try {
        const constraints = { [edge]: value };
        const constraintsJson = encodeURIComponent(JSON.stringify(constraints));
        
        const result = await apiCall(`/algo/dijkstra?src=${source}&dst=${dest}&constraints=${constraintsJson}&save=false`);
        
        const testResult = document.getElementById('testResult');
        testResult.innerHTML = `
            <strong>Résultat du test :</strong><br>
            Chemin: ${result.path.join(' → ')}<br>
            Distance: ${result.distance.toFixed(2)} km<br>
            <br>
            <em>Cette contrainte est temporaire et n'a pas été sauvegardée</em>
        `;
        testResult.style.display = 'block';
        
        showToast('Test effectué !', 'info');
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// =================== HISTORY ===================
async function showHistoryModal() {
    try {
        const history = await apiCall('/history/paths?limit=20');
        
        const historyList = document.getElementById('historyList');
        
        if (history.length === 0) {
            historyList.innerHTML = '<p class="info-text">Aucun calcul dans l\'historique</p>';
        } else {
            historyList.innerHTML = history.map(h => `
                <div class="history-card">
                    <div class="history-header">
                        <div class="history-route">${h.source} → ${h.destination}</div>
                        <div class="history-date">${new Date(h.calculated_at).toLocaleString()}</div>
                    </div>
                    <div class="history-path">${h.path.join(' → ')}</div>
                    <div class="history-distance">Distance: ${h.distance.toFixed(2)} km</div>
                    ${h.user_notes ? `<div style="font-size: 0.85rem; color: #666; margin-top: 0.5rem;">📝 ${h.user_notes}</div>` : ''}
                    <button class="btn btn-info btn-small" onclick="replayCalculation(${h.id})" style="margin-top: 0.75rem;">
                        🔄 Recalculer
                    </button>
                </div>
            `).join('');
        }
        
        openModal('historyModal');
    } catch (error) {
        console.error('Erreur:', error);
    }
}

async function replayCalculation(historyId) {
    try {
        const result = await apiCall(`/history/paths/${historyId}/replay`);
        
        showToast(`Calcul #${historyId} recalculé`, 'success');
        
        // Réinitialiser les couleurs
        state.nodes.forEach(node => {
            delete node.color;
        });
        
        state.highlightedPath = result.path;
        renderGraph();
        
        closeModal('historyModal');
        
        const pathDisplay = document.getElementById('pathDisplay');
        const distanceDisplay = document.getElementById('distanceDisplay');
        const pathResult = document.getElementById('pathResult');
        
        pathDisplay.innerHTML = `<strong>Chemin (replay):</strong> ${result.path.join(' → ')}`;
        distanceDisplay.innerHTML = `<strong>Distance:</strong> ${result.distance.toFixed(2)} km`;
        pathResult.style.display = 'block';
        
        document.getElementById('coloringResult').style.display = 'none';
    } catch (error) {
        console.error('Erreur:', error);
    }
}

// =================== RENDER GRAPH ===================
function renderGraph() {
    const nodesGroup = document.getElementById('nodesGroup');
    const edgesGroup = document.getElementById('edgesGroup');
    const labelsGroup = document.getElementById('labelsGroup');
    
    nodesGroup.innerHTML = '';
    edgesGroup.innerHTML = '';
    labelsGroup.innerHTML = '';
    
    // Dessiner les arêtes
    state.edges.forEach(edge => {
        const sourceNode = state.nodes.find(n => n.id === edge.source);
        const targetNode = state.nodes.find(n => n.id === edge.target);
        
        if (!sourceNode || !targetNode) return;
        
        const isHighlighted = isEdgeInPath(edge.source, edge.target);
        
        const line = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        line.setAttribute('x1', sourceNode.x);
        line.setAttribute('y1', sourceNode.y);
        line.setAttribute('x2', targetNode.x);
        line.setAttribute('y2', targetNode.y);
        line.setAttribute('class', isHighlighted ? 'edge highlighted' : 'edge');
        
        if (isHighlighted) {
            line.setAttribute('stroke-dasharray', '10 5');
        }
        
        edgesGroup.appendChild(line);
        
        // Label de l'arête
        const midX = (sourceNode.x + targetNode.x) / 2;
        const midY = (sourceNode.y + targetNode.y) / 2;
        
        const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        label.setAttribute('x', midX);
        label.setAttribute('y', midY - 5);
        label.setAttribute('text-anchor', 'middle');
        label.setAttribute('class', 'edge-label');
        label.textContent = edge.weight.toFixed(1);
        
        labelsGroup.appendChild(label);
    });
    
    // Dessiner les nœuds
    state.nodes.forEach(node => {
        const isSelected = state.selectedNodes.includes(node.id);
        const isInPath = state.highlightedPath.includes(node.id);
        
        const g = document.createElementNS('http://www.w3.org/2000/svg', 'g');
        g.setAttribute('class', `node ${isSelected ? 'selected' : ''} ${isInPath ? 'highlighted' : ''}`);
        g.setAttribute('data-id', node.id);
        g.style.cursor = state.mode === 'addEdge' ? 'pointer' : 'default';
        
        // Cercle du nœud
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', node.x);
        circle.setAttribute('cy', node.y);
        circle.setAttribute('r', 20);
        
        // Couleur ROUGE/VERT selon coloriage ou défaut
        const colors = ['#F44336', '#4CAF50', '#FF9800', '#2196F3', '#9C27B0', '#00BCD4', '#795548', '#607D8B'];
        const fillColor = node.color !== undefined ? colors[node.color % colors.length] : '#2196F3';
        
        circle.setAttribute('fill', fillColor);
        circle.setAttribute('stroke', '#fff');
        circle.setAttribute('stroke-width', '2');
        
        g.appendChild(circle);
        
        // Label du nœud
        const text = document.createElementNS('http://www.w3.org/2000/svg', 'text');
        text.setAttribute('x', node.x);
        text.setAttribute('y', node.y + 5);
        text.setAttribute('text-anchor', 'middle');
        text.setAttribute('class', 'node-label');
        text.setAttribute('fill', 'white');
        text.textContent = node.id;
        
        g.appendChild(text);
        
        // Event listener
        g.addEventListener('click', (e) => {
            e.stopPropagation();
            handleNodeClick(node.id);
        });
        
        nodesGroup.appendChild(g);
    });
}

function isEdgeInPath(source, target) {
    const path = state.highlightedPath;
    for (let i = 0; i < path.length - 1; i++) {
        if ((path[i] === source && path[i + 1] === target) || 
            (path[i] === target && path[i + 1] === source)) {
            return true;
        }
    }
    return false;
}

// =================== ZOOM & PAN ===================
function zoom(factor) {
    state.zoom *= factor;
    showToast(`Zoom: ${(state.zoom * 100).toFixed(0)}%`, 'info');
}

function resetView() {
    state.zoom = 1;
    state.offset = { x: 0, y: 0 };
    showToast('Vue réinitialisée', 'info');
}

// =================== MODALS ===================
function openModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.add('show');
}

function closeModal(modalId) {
    const modal = document.getElementById(modalId);
    modal.classList.remove('show');
}

document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        document.querySelectorAll('.modal.show').forEach(modal => {
            modal.classList.remove('show');
        });
    }
});

// =================== TOAST NOTIFICATIONS ===================
function showToast(message, type = 'info') {
    const container = document.getElementById('toastContainer');
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
        success: '✅',
        error: '❌',
        warning: '⚠️',
        info: 'ℹ️'
    };
    
    toast.innerHTML = `
        <div class="toast-icon">${icons[type] || 'ℹ️'}</div>
        <div class="toast-message">${message}</div>
    `;
    
    container.appendChild(toast);
    
    setTimeout(() => {
        toast.style.animation = 'slideInRight 0.3s reverse';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}