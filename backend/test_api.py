import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.controllers import GraphController, AlgorithmController

print("=== TEST DU SYSTÈME AMÉLIORÉ ===\n")

graph_ctrl = GraphController()
algo_ctrl = AlgorithmController()

try:
    # 1. Nettoyer
    print("1. Nettoyage...")
    graph_ctrl.clear_graph()
    print("✓ Graphe nettoyé\n")
    
    # 2. Créer des nœuds
    print("2. Création des nœuds...")
    graph_ctrl.create_node('DEPOT', 0, 0, 0)
    graph_ctrl.create_node('A', 100, 100, 50)
    graph_ctrl.create_node('B', 200, 50, 30)
    graph_ctrl.create_node('C', 150, 200, 40)
    print("✓ 4 nœuds créés\n")
    
    # 3. Créer des arêtes (SANS constraint_value maintenant)
    print("3. Création des arêtes...")
    graph_ctrl.create_edge('DEPOT', 'A', 2.0)
    graph_ctrl.create_edge('DEPOT', 'B', 2.3)
    graph_ctrl.create_edge('A', 'C', 1.8)
    graph_ctrl.create_edge('B', 'C', 2.7)
    print("✓ 4 arêtes créées\n")
    
    # 4. Test Dijkstra SANS contraintes
    print("4. Dijkstra sans contraintes (DEPOT → C)...")
    result1 = algo_ctrl.find_shortest_path('DEPOT', 'C')
    print(f"✓ Chemin: {' → '.join(result1['path'])}")
    print(f"✓ Distance: {result1['distance']}\n")
    
    # 5. Créer une contrainte avec expiration
    print("5. Création d'une contrainte (travaux A-C, +5, expire dans 30 jours)...")
    constraint1 = graph_ctrl.create_constraint('A', 'C', 5.0, "Travaux voirie", 30)
    print(f"✓ Contrainte créée: ID={constraint1['id']}")
    print(f"✓ Expire le: {constraint1['expires_at']}\n")
    
    # 6. Test Dijkstra AVEC contrainte active
    print("6. Dijkstra avec contrainte active (DEPOT → C)...")
    result2 = algo_ctrl.find_shortest_path('DEPOT', 'C')
    print(f"✓ Nouveau chemin: {' → '.join(result2['path'])}")
    print(f"✓ Nouvelle distance: {result2['distance']}\n")
    
    # 7. Créer une autre contrainte permanente
    print("7. Contrainte permanente (B-C, +1, péage)...")
    constraint2 = graph_ctrl.create_constraint('B', 'C', 1.0, "Péage autoroute", None)
    print(f"✓ Contrainte créée: ID={constraint2['id']}\n")
    
    # 8. Dijkstra avec plusieurs contraintes
    print("8. Dijkstra avec multiples contraintes...")
    result3 = algo_ctrl.find_shortest_path('DEPOT', 'C')
    print(f"✓ Chemin: {' → '.join(result3['path'])}")
    print(f"✓ Distance: {result3['distance']}\n")
    
    # 9. Désactiver une contrainte
    print("9. Désactivation de la contrainte des travaux...")
    graph_ctrl.toggle_constraint(constraint1['id'], False)
    print("✓ Contrainte désactivée\n")
    
    # 10. Dijkstra après désactivation
    print("10. Dijkstra après désactivation...")
    result4 = algo_ctrl.find_shortest_path('DEPOT', 'C')
    print(f"✓ Chemin: {' → '.join(result4['path'])}")
    print(f"✓ Distance: {result4['distance']}\n")
    
    # 11. Historique
    print("11. Consultation de l'historique...")
    history = algo_ctrl.get_path_history(limit=10)
    print(f"✓ {len(history)} calculs dans l'historique")
    for h in history:
        # FIX: Convertir calculated_at en string si c'est un datetime
        calc_time = h['calculated_at']
        if isinstance(calc_time, str):
            calc_time_str = calc_time[:19]
        else:
            calc_time_str = calc_time.strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"   - [{h['id']}] {h['source']}→{h['destination']}: {h['distance']} ({calc_time_str})")
    print()
    
    # 12. Replay d'un calcul
    if history:
        print(f"12. Replay du calcul #{history[0]['id']}...")
        replay = algo_ctrl.replay_path_calculation(history[0]['id'])
        print(f"✓ Chemin rejoué: {' → '.join(replay['path'])}")
        print(f"✓ Distance: {replay['distance']}\n")
    
    # 13. Test contrainte temporaire (sans sauvegarder)
    print("13. Test avec contrainte temporaire (+10 sur DEPOT-A)...")
    result5 = algo_ctrl.find_shortest_path('DEPOT', 'C', {'DEPOT-A': 10}, save_to_history=False)
    print(f"✓ Chemin avec contrainte temp: {' → '.join(result5['path'])}")
    print(f"✓ Distance: {result5['distance']}")
    print("✓ Pas sauvegardé dans l'historique\n")
    
    print("=== TOUS LES TESTS RÉUSSIS ! ===")
    
except Exception as e:
    print(f"❌ ERREUR: {e}")
    import traceback
    traceback.print_exc()