import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from backend.database.connection import Database
from backend.models import Node, Edge, Graph


class GraphController:
    """Contrôleur pour gérer le graphe (CRUD)"""
    
    def __init__(self):
        self.db = Database()
    
    # =====================
    # NODES - CRUD
    # =====================
    
    def create_node(self, node_id, x, y, capacity=0):
        """Créer un nœud"""
        try:
            cursor = self.db.get_cursor()
            
            cursor.execute("""
                INSERT INTO nodes (id, x, y, capacity)
                VALUES (%s, %s, %s, %s)
                RETURNING *
            """, (node_id, x, y, capacity))
            
            result = cursor.fetchone()
            self.db.commit()
            cursor.close()
            
            return dict(result)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur création nœud: {e}")
    
    def get_all_nodes(self):
        """Récupérer tous les nœuds"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM nodes ORDER BY id")
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            raise Exception(f"Erreur récupération nœuds: {e}")
    
    def get_node(self, node_id):
        """Récupérer un nœud spécifique"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM nodes WHERE id = %s", (node_id,))
            result = cursor.fetchone()
            cursor.close()
            
            return dict(result) if result else None
            
        except Exception as e:
            raise Exception(f"Erreur récupération nœud: {e}")
    
    def delete_node(self, node_id):
        """Supprimer un nœud"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("DELETE FROM nodes WHERE id = %s", (node_id,))
            deleted = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return deleted
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur suppression nœud: {e}")
    
    # =====================
    # EDGES - CRUD
    # =====================
    
    def create_edge(self, source, target, weight):
        """Créer une arête NON-ORIENTÉE (sans constraint_value)"""
        try:
            cursor = self.db.get_cursor()
            
            # Vérifier que les nœuds existent
            cursor.execute("SELECT id FROM nodes WHERE id IN (%s, %s)", (source, target))
            if cursor.rowcount < 2:
                raise ValueError("Les nœuds source et/ou target n'existent pas")
            
            # Insérer les deux directions
            cursor.execute("""
                INSERT INTO edges (source, target, weight)
                VALUES (%s, %s, %s)
                ON CONFLICT (source, target) DO UPDATE
                SET weight = EXCLUDED.weight
                RETURNING *
            """, (source, target, weight))
            edge1 = cursor.fetchone()
            
            cursor.execute("""
                INSERT INTO edges (source, target, weight)
                VALUES (%s, %s, %s)
                ON CONFLICT (source, target) DO UPDATE
                SET weight = EXCLUDED.weight
            """, (target, source, weight))
            
            self.db.commit()
            cursor.close()
            
            return dict(edge1)
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur création arête: {e}")
    
    def get_all_edges(self):
        """Récupérer toutes les arêtes (sans doublons)"""
        try:
            cursor = self.db.get_cursor()
            
            cursor.execute("""
                SELECT * FROM edges 
                WHERE source < target
                ORDER BY source, target
            """)
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            raise Exception(f"Erreur récupération arêtes: {e}")
    
    def delete_edge(self, source, target):
        """Supprimer une arête (les deux directions)"""
        try:
            cursor = self.db.get_cursor()
            
            cursor.execute("""
                DELETE FROM edges 
                WHERE (source = %s AND target = %s) OR (source = %s AND target = %s)
            """, (source, target, target, source))
            
            deleted = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return deleted
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur suppression arête: {e}")
    
    # =====================
    # CONSTRAINTS - NOUVEAU
    # =====================
    
    def create_constraint(self, source, target, constraint_value, reason=None, expiry_days=None):
        """Créer une contrainte avec cycle de vie"""
        try:
            cursor = self.db.get_cursor()
            
            # Calculer expires_at si expiry_days fourni
            expires_at = None
            if expiry_days:
                from datetime import datetime, timedelta
                expires_at = datetime.now() + timedelta(days=expiry_days)
            
            cursor.execute("""
                INSERT INTO constraints (source, target, constraint_value, reason, expiry_days, expires_at)
                VALUES (%s, %s, %s, %s, %s, %s)
                RETURNING *
            """, (source, target, constraint_value, reason, expiry_days, expires_at))
            
            result = cursor.fetchone()
            self.db.commit()
            cursor.close()
            
            return dict(result)
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur création contrainte: {e}")
    
    def get_active_constraints(self):
        """Récupérer toutes les contraintes valides (actives ET non expirées)"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT * FROM constraints
                WHERE is_active = TRUE 
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY created_at DESC
            """)
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            raise Exception(f"Erreur récupération contraintes: {e}")
    
    def get_all_constraints(self):
        """Récupérer TOUTES les contraintes (même inactives/expirées)"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM constraints ORDER BY created_at DESC")
            results = cursor.fetchall()
            cursor.close()
            
            return [dict(row) for row in results]
            
        except Exception as e:
            raise Exception(f"Erreur récupération contraintes: {e}")
    
    def toggle_constraint(self, constraint_id, is_active):
        """Activer/désactiver une contrainte"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                UPDATE constraints 
                SET is_active = %s
                WHERE id = %s
            """, (is_active, constraint_id))
            
            updated = cursor.rowcount > 0
            self.db.commit()
            cursor.close()
            
            return updated
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur toggle contrainte: {e}")
    
    def get_constraints_for_edge(self, source, target):
        """Récupérer les contraintes valides pour une arête et les sommer"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("""
                SELECT * FROM constraints
                WHERE ((source = %s AND target = %s) OR (source = %s AND target = %s))
                AND is_active = TRUE
                AND (expires_at IS NULL OR expires_at > CURRENT_TIMESTAMP)
                ORDER BY created_at DESC
            """, (source, target, target, source))
            
            results = cursor.fetchall()
            cursor.close()
            
            # Sommer toutes les contraintes valides pour cette arête
            total_constraint = sum(row['constraint_value'] for row in results)
            
            return total_constraint, [dict(row) for row in results]
        except Exception as e:
            raise Exception(f"Erreur récupération contraintes arête: {e}")
    
    # =====================
    # GRAPH COMPLET
    # =====================
    
    def get_graph(self):
        """Récupérer le graphe complet avec contraintes actives intégrées"""
        try:
            graph = Graph()
            
            # Charger les nœuds
            nodes = self.get_all_nodes()
            for node_data in nodes:
                node = Node(
                    node_id=node_data['id'],
                    x=node_data['x'],
                    y=node_data['y'],
                    capacity=node_data['capacity']
                )
                graph.add_node(node)
            
            # Charger les arêtes depuis edges table
            cursor = self.db.get_cursor()
            cursor.execute("SELECT * FROM edges ORDER BY source, target")
            edges = cursor.fetchall()
            cursor.close()
            
            # Construire le dictionnaire d'adjacence avec contraintes
            for edge_data in edges:
                source = edge_data['source']
                target = edge_data['target']
                weight = edge_data['weight']
                
                # Récupérer les contraintes actives pour cette arête
                total_constraint, _ = self.get_constraints_for_edge(source, target)
                
                edge = Edge(source, target, weight, total_constraint)
                
                # Ajouter seulement si pas déjà ajouté
                if source in graph.edges:
                    exists = any(e.target == target for e in graph.edges[source])
                    if not exists:
                        graph.edges[source].append(edge)
                else:
                    graph.edges[source] = [edge]
            
            return graph
            
        except Exception as e:
            raise Exception(f"Erreur récupération graphe: {e}")
    
    def clear_graph(self):
        """Supprimer tout le graphe"""
        try:
            cursor = self.db.get_cursor()
            cursor.execute("TRUNCATE TABLE edges, nodes CASCADE")
            self.db.commit()
            cursor.close()
            
            return True
            
        except Exception as e:
            self.db.rollback()
            raise Exception(f"Erreur suppression graphe: {e}")