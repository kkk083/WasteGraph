import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.controllers.graph_controller import GraphController
from backend.algorithms import dijkstra, graph_coloring, get_coloring_stats


class AlgorithmController:
    """Contrôleur pour les algorithmes"""
    
    def __init__(self):
        self.graph_controller = GraphController()
    
    def find_shortest_path(self, source, destination, custom_constraints=None, save_to_history=True, user_notes=None):
        """
        Trouver le plus court chemin avec Dijkstra
        
        Args:
            source: Nœud de départ
            destination: Nœud d'arrivée
            custom_constraints: dict optionnel {"A-B": 5} pour test temporaire
            save_to_history: Sauvegarder dans l'historique ?
            user_notes: Notes utilisateur pour l'historique
        """
        try:
            # Récupérer le graphe (avec contraintes actives de la BDD déjà intégrées)
            graph = self.graph_controller.get_graph()
            
            # Si contraintes custom fournies, on les merge avec celles de la BDD
            # Sinon on utilise juste celles déjà dans le graphe
            constraints_to_apply = custom_constraints or {}
            
            # Convertir en liste d'adjacence
            adj_list = graph.get_adjacency_list(constraints_to_apply)
            
            # Appeler Dijkstra
            path, distance = dijkstra(adj_list, source, destination)
            
            result = {
                'path': path,
                'distance': distance,
                'source': source,
                'destination': destination,
                'custom_constraints_applied': constraints_to_apply
            }
            
            # Sauvegarder dans l'historique si demandé
            if save_to_history and path:
                self._save_path_to_history(source, destination, path, distance, 
                                           constraints_to_apply, user_notes)
            
            return result
            
        except Exception as e:
            raise Exception(f"Erreur calcul Dijkstra: {e}")
    
    def _save_path_to_history(self, source, destination, path, distance, 
                              constraints_snapshot, user_notes):
        """Sauvegarder un calcul dans l'historique"""
        try:
            cursor = self.graph_controller.db.get_cursor()
            
            import json
            cursor.execute("""
                INSERT INTO path_history 
                (source, destination, path, distance, constraints_snapshot, user_notes)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (source, destination, json.dumps(path), distance, 
                  json.dumps(constraints_snapshot), user_notes))
            
            result = cursor.fetchone()
            self.graph_controller.db.commit()
            cursor.close()
            
            return result['id']
        except Exception as e:
            self.graph_controller.db.rollback()
            print(f"Avertissement: Impossible de sauvegarder dans l'historique: {e}")
    
    def get_path_history(self, limit=20):
        """Récupérer l'historique des calculs"""
        try:
            cursor = self.graph_controller.db.get_cursor()
            cursor.execute("""
                SELECT * FROM path_history
                ORDER BY calculated_at DESC
                LIMIT %s
            """, (limit,))
            
            results = cursor.fetchall()
            cursor.close()
            
            import json
            history = []
            for row in results:
                item = dict(row)
                item['path'] = json.loads(item['path']) if isinstance(item['path'], str) else item['path']
                item['constraints_snapshot'] = json.loads(item['constraints_snapshot']) if isinstance(item['constraints_snapshot'], str) else item['constraints_snapshot']
                history.append(item)
            
            return history
        except Exception as e:
            raise Exception(f"Erreur récupération historique: {e}")
    
    def replay_path_calculation(self, history_id):
        """Recalculer un chemin depuis l'historique"""
        try:
            cursor = self.graph_controller.db.get_cursor()
            cursor.execute("SELECT * FROM path_history WHERE id = %s", (history_id,))
            result = cursor.fetchone()
            cursor.close()
            
            if not result:
                raise ValueError("Calcul introuvable dans l'historique")
            
            import json
            constraints = json.loads(result['constraints_snapshot']) if isinstance(result['constraints_snapshot'], str) else result['constraints_snapshot']
            
            # Recalculer avec les mêmes paramètres
            new_result = self.find_shortest_path(
                result['source'], 
                result['destination'],
                custom_constraints=constraints,
                save_to_history=False,
                user_notes=f"Replay du calcul #{history_id}"
            )
            
            # Ajouter l'info de l'original
            new_result['original_calculation'] = dict(result)
            new_result['original_calculation']['path'] = json.loads(result['path']) if isinstance(result['path'], str) else result['path']
            
            return new_result
        except Exception as e:
            raise Exception(f"Erreur replay: {e}")
    
    def color_graph(self):
        """Colorier le graphe"""
        try:
            graph = self.graph_controller.get_graph()
            adj_list = graph.get_adjacency_list()
            
            coloring = graph_coloring(adj_list)
            stats = get_coloring_stats(coloring)
            chromatic_number = max(coloring.values()) + 1 if coloring else 0
            
            return {
                'coloring': coloring,
                'stats': stats,
                'chromatic_number': chromatic_number
            }
            
        except Exception as e:
            raise Exception(f"Erreur coloriage: {e}")