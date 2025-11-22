import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.controllers.graph_controller import GraphController
from backend.controllers.algorithm_controller import AlgorithmController

print("=== TEST DES CONTROLLERS ===\n")

# Initialiser les controllers
graph_ctrl = GraphController()
algo_ctrl = AlgorithmController()

try:
    # Nettoyer le graphe
    print("1. Nettoyage du graphe...")
    graph_ctrl.clear_graph()
    print("✓ Graphe nettoyé\n")
    
    # Créer des nœuds
    print("2. Création des nœuds...")
    graph_ctrl.create_node('DEPOT', 0, 0, 0)
    graph_ctrl.create_node('A', 100, 100, 50)
    graph_ctrl.create_node('B', 200, 50, 30)
    graph_ctrl.create_node('C', 150, 200, 40)
    graph_ctrl.create_node('D', 250, 150, 35)
    print("✓ 5 nœuds créés\n")
    
    # Créer des arêtes
    print("3. Création des arêtes...")
    graph_ctrl.create_edge('DEPOT', 'A', 2.0, 0)
    graph_ctrl.create_edge('DEPOT', 'B', 2.3, 0)
    graph_ctrl.create_edge('A', 'C', 1.8, 0)
    graph_ctrl.create_edge('B', 'C', 2.7, 0)
    graph_ctrl.create_edge('B', 'D', 2.5, 0)
    graph_ctrl.create_edge('C', 'D', 1.9, 0)
    print("✓ 6 arêtes créées\n")
    
    # Afficher le graphe
    print("4. Récupération du graphe...")
    nodes = graph_ctrl.get_all_nodes()
    edges = graph_ctrl.get_all_edges()
    print(f"✓ {len(nodes)} nœuds, {len(edges)} arêtes\n")
    
    # Test Dijkstra
    print("5. Test Dijkstra (DEPOT → C)...")
    result = algo_ctrl.find_shortest_path('DEPOT', 'C')
    print(f"✓ Chemin: {' → '.join(result['path'])}")
    print(f"✓ Distance: {result['distance']}\n")
    
    # Test Dijkstra avec contrainte temporaire
    print("6. Test Dijkstra avec contrainte temporaire (+5 sur A-C)...")
    result2 = algo_ctrl.find_shortest_path('DEPOT', 'C', {'A-C': 5})
    print(f"✓ Nouveau chemin: {' → '.join(result2['path'])}")
    print(f"✓ Nouvelle distance: {result2['distance']}\n")
    
    # Test Coloriage
    print("7. Test Coloriage...")
    coloring_result = algo_ctrl.color_graph()
    print(f"✓ Coloriage: {coloring_result['coloring']}")
    print(f"✓ Nombre chromatique: {coloring_result['chromatic_number']}")
    print(f"✓ Stats: {coloring_result['stats']}\n")
    
    # Modifier contrainte de façon permanente
    print("8. Modification permanente de contrainte (A-C = 5)...")
    graph_ctrl.update_edge_constraint('A', 'C', 5)
    result3 = algo_ctrl.find_shortest_path('DEPOT', 'C')
    print(f"✓ Chemin avec contrainte permanente: {' → '.join(result3['path'])}")
    print(f"✓ Distance: {result3['distance']}\n")
    
    print("=== TOUS LES TESTS RÉUSSIS ! ===")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()