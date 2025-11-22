def dijkstra(graph_adj, source, destination):
    """
    Algorithme de Dijkstra avec support des contraintes
    
    Args:
        graph_adj: dict {node: [(voisin, poids, contrainte), ...]}
        source: Nœud de départ
        destination: Nœud d'arrivée
    
    Returns:
        tuple: (chemin, distance) ou (None, inf) si impossible
    """
    # Vérifications
    if source not in graph_adj:
        raise ValueError(f"Le nœud source '{source}' n'existe pas !")
    if destination not in graph_adj:
        raise ValueError(f"Le nœud destination '{destination}' n'existe pas !")
    
    # Initialisation
    dist = {node: float('inf') for node in graph_adj}
    dist[source] = 0
    parent = {node: None for node in graph_adj}
    unvisited = set(graph_adj.keys())

    while unvisited:
        # Trouver le nœud non visité le plus proche
        current = None
        for node in unvisited:
            if current is None or dist[node] < dist[current]:
                current = node

        # Si on ne peut plus avancer
        if dist[current] == float('inf'):
            break
        
        unvisited.remove(current)

        # Explorer les voisins
        for neighbor, weight, constraint in graph_adj[current]:
            # Coût total = poids de base + contrainte
            total_cost = weight + constraint
            new_dist = dist[current] + total_cost
            
            if new_dist < dist[neighbor]:
                dist[neighbor] = new_dist
                parent[neighbor] = current

    # Vérifier si destination atteignable
    if dist[destination] == float('inf'):
        return None, float('inf')
    
    # Reconstruire le chemin
    path = []
    current = destination
    while current is not None:
        path.append(current)
        current = parent[current]
    path.reverse()
    
    return path, dist[destination]