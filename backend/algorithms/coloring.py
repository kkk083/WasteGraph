def graph_coloring(graph_adj):
    """
    Algorithme de coloriage glouton
    
    Args:
        graph_adj: dict {node: [(voisin, poids, contrainte), ...]}
    
    Returns:
        dict: {node: couleur} où couleur est un entier
    """
    color_assignment = {}
    available_colors = list(range(20))  # Jusqu'à 20 couleurs
    
    for node in graph_adj:
        # Récupérer les voisins
        neighbors = [neighbor for neighbor, _, _ in graph_adj[node]]
        
        # Couleurs utilisées par les voisins
        neighbor_colors = {
            color_assignment[neighbor] 
            for neighbor in neighbors 
            if neighbor in color_assignment
        }
        
        # Trouver la première couleur disponible
        for color in available_colors:
            if color not in neighbor_colors:
                color_assignment[node] = color
                break
    
    return color_assignment


def get_coloring_stats(coloring):
    stats = {}
    for node, color in coloring.items():
        stats[color] = stats.get(color, 0) + 1
    return stats