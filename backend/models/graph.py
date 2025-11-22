from .node import Node
from .edge import Edge
class Graph:
    """Représente le graphe complet (en mémoire)"""
    
    def __init__(self):
        self.nodes = {}  # {id: Node}
        self.edges = {}  # {node_id: [Edge, Edge, ...]}
    
    def add_node(self, node):
        """Ajoute un objet Node"""
        if not isinstance(node, Node):
            raise TypeError("Doit être une instance de Node")
        
        self.nodes[node.id] = node
        if node.id not in self.edges:
            self.edges[node.id] = []
    
    def add_edge(self, edge):
        """Ajoute un objet Edge (non-orienté)"""
        if not isinstance(edge, Edge):
            raise TypeError("Doit être une instance de Edge")
        
        # Vérifier que les nœuds existent
        if edge.source not in self.nodes or edge.target not in self.nodes:
            raise ValueError("Les nœuds source/target doivent exister")
        
        # Ajouter dans les deux sens
        self.edges[edge.source].append(edge)
        reverse_edge = Edge(edge.target, edge.source, edge.weight, edge.constraint_value)
        self.edges[edge.target].append(reverse_edge)
    
    def get_adjacency_list(self, custom_constraints=None):
        """
        Format pour Dijkstra avec contraintes optionnelles
        
        Args:
            custom_constraints: dict {"A-B": 5, "C-D": 2} (contraintes temporaires)
        
        Returns:
            dict: {node: [(voisin, poids, contrainte), ...]}
        """
        custom_constraints = custom_constraints or {}
        adj = {}
        
        for node_id, edges in self.edges.items():
            adj[node_id] = []
            for e in edges:
                # Clé pour chercher la contrainte custom
                edge_key = f"{e.source}-{e.target}"
                
                # Utiliser contrainte custom si elle existe, sinon la BDD
                constraint = custom_constraints.get(edge_key, e.constraint_value)
                
                adj[node_id].append((e.target, e.weight, constraint))
        
        return adj
    
    def get_edge(self, source, target):
        """Récupérer une arête spécifique"""
        if source in self.edges:
            for edge in self.edges[source]:
                if edge.target == target:
                    return edge
        return None
    
    def update_edge_constraint(self, source, target, new_constraint):
        """Mettre à jour la contrainte d'une arête (dans les 2 sens)"""
        # Mise à jour source → target
        edge = self.get_edge(source, target)
        if edge:
            edge.constraint_value = new_constraint
        
        # Mise à jour target → source (graphe non-orienté)
        reverse_edge = self.get_edge(target, source)
        if reverse_edge:
            reverse_edge.constraint_value = new_constraint
    
    def to_dict(self):
        """Export JSON (sans doublons d'arêtes)"""
        nodes_list = [node.to_dict() for node in self.nodes.values()]
        
        edges_list = []
        seen = set()
        
        for node_id, edge_list in self.edges.items():
            for edge in edge_list:
                edge_key = tuple(sorted([edge.source, edge.target]))
                if edge_key not in seen:
                    edges_list.append(edge.to_dict())
                    seen.add(edge_key)
        
        return {
            'nodes': nodes_list,
            'edges': edges_list
        }