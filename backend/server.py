from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import sys
import os
from urllib.parse import urlparse, parse_qs

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.controllers import GraphController, AlgorithmController


class WasteGraphHandler(BaseHTTPRequestHandler):
    """Gestionnaire des requêtes HTTP pour WasteGraph"""
    
    graph_controller = GraphController()
    algo_controller = AlgorithmController()
    
    def _set_headers(self, status_code=200, content_type='application/json'):
        """Définir les headers de la réponse"""
        self.send_response(status_code)
        self.send_header('Content-Type', content_type)
        self.send_header('Access-Control-Allow-Origin', '*')
        self.send_header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS')
        self.send_header('Access-Control-Allow-Headers', 'Content-Type')
        self.end_headers()
    
    def _send_json(self, data, status_code=200):
        """Envoyer une réponse JSON"""
        self._set_headers(status_code)
        self.wfile.write(json.dumps(data, ensure_ascii=False).encode('utf-8'))
    
    def _send_error(self, message, status_code=400):
        """Envoyer une erreur"""
        self._send_json({'error': message}, status_code)
    
    def _parse_body(self):
        """Parser le body JSON de la requête"""
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length == 0:
            return {}
        body = self.rfile.read(content_length)
        return json.loads(body.decode('utf-8'))
    
    def do_OPTIONS(self):
        """Gérer les requêtes OPTIONS (CORS preflight)"""
        self._set_headers(204)
    
    def do_GET(self):
        """Gérer les requêtes GET"""
        parsed_path = urlparse(self.path)
        path = parsed_path.path
        query_params = parse_qs(parsed_path.query)
        
        try:
            # GET /graph - Récupérer tout le graphe
            if path == '/graph':
                graph = self.graph_controller.get_graph()
                self._send_json(graph.to_dict())
            
            # GET /constraints - Contraintes actives
            elif path == '/constraints':
                constraints = self.graph_controller.get_active_constraints()
                self._send_json(constraints)
            
            # GET /constraints/all - Toutes les contraintes
            elif path == '/constraints/all':
                constraints = self.graph_controller.get_all_constraints()
                self._send_json(constraints)
            
            # GET /history/paths - Historique des calculs
            elif path == '/history/paths':
                limit = int(query_params.get('limit', [20])[0])
                history = self.algo_controller.get_path_history(limit)
                self._send_json(history)
            
            # GET /history/paths/{id}/replay - Recalculer un chemin
            elif path.startswith('/history/paths/') and path.endswith('/replay'):
                history_id = int(path.split('/')[3])
                result = self.algo_controller.replay_path_calculation(history_id)
                self._send_json(result)
            
            # GET /algo/dijkstra?src=A&dst=Z&constraints={"A-B":5}
            elif path == '/algo/dijkstra':
                source = query_params.get('src', [None])[0]
                destination = query_params.get('dst', [None])[0]
                constraints_str = query_params.get('constraints', ['{}'])[0]
                save_history = query_params.get('save', ['true'])[0].lower() == 'true'
                notes = query_params.get('notes', [None])[0]
                
                if not source or not destination:
                    self._send_error("Paramètres 'src' et 'dst' requis")
                    return
                
                custom_constraints = json.loads(constraints_str) if constraints_str else {}
                
                result = self.algo_controller.find_shortest_path(
                    source, destination, custom_constraints, save_history, notes
                )
                self._send_json(result)
            
            # GET /algo/coloring
            elif path == '/algo/coloring':
                result = self.algo_controller.color_graph()
                self._send_json(result)
            
            else:
                self._send_error(f"Route inconnue: {path}", 404)
        
        except Exception as e:
            self._send_error(str(e), 500)
    
    def do_POST(self):
        """Gérer les requêtes POST"""
        path = self.path
        
        try:
            data = self._parse_body()
            
            # POST /graph/node - Créer un nœud
            if path == '/graph/node':
                node_id = data.get('id')
                x = data.get('x', 0)
                y = data.get('y', 0)
                capacity = data.get('capacity', 0)
                
                if not node_id:
                    self._send_error("Le champ 'id' est requis")
                    return
                
                result = self.graph_controller.create_node(node_id, x, y, capacity)
                self._send_json(result, 201)
            
            # POST /graph/edge - Créer une arête
            elif path == '/graph/edge':
                source = data.get('source')
                target = data.get('target')
                weight = data.get('weight')
                
                if not source or not target or weight is None:
                    self._send_error("Les champs 'source', 'target' et 'weight' sont requis")
                    return
                
                result = self.graph_controller.create_edge(source, target, weight)
                self._send_json(result, 201)
            
            # POST /constraints - Créer une contrainte
            elif path == '/constraints':
                source = data.get('source')
                target = data.get('target')
                constraint_value = data.get('constraint_value')
                reason = data.get('reason')
                expiry_days = data.get('expiry_days')
                
                if not source or not target or constraint_value is None:
                    self._send_error("Les champs 'source', 'target' et 'constraint_value' sont requis")
                    return
                
                result = self.graph_controller.create_constraint(
                    source, target, constraint_value, reason, expiry_days
                )
                self._send_json(result, 201)
            
            else:
                self._send_error(f"Route inconnue: {path}", 404)
        
        except Exception as e:
            self._send_error(str(e), 500)
    
    def do_PUT(self):
        """Gérer les requêtes PUT"""
        path = self.path
        
        try:
            data = self._parse_body()
            
            # PUT /constraints/{id}/toggle - Activer/désactiver
            if path.startswith('/constraints/') and path.endswith('/toggle'):
                constraint_id = int(path.split('/')[2])
                is_active = data.get('is_active', True)
                
                success = self.graph_controller.toggle_constraint(constraint_id, is_active)
                
                if success:
                    self._send_json({'message': 'Contrainte mise à jour'})
                else:
                    self._send_error("Contrainte non trouvée", 404)
            
            else:
                self._send_error(f"Route inconnue: {path}", 404)
        
        except Exception as e:
            self._send_error(str(e), 500)
    
    def do_DELETE(self):
        """Gérer les requêtes DELETE"""
        path = self.path
        
        try:
            # DELETE /graph - Vider tout
            if path == '/graph':
                self.graph_controller.clear_graph()
                self._send_json({'message': 'Graphe vidé'})
            
            # DELETE /node/{id}/smart - Suppression intelligente (NOUVEAU)
            elif path.startswith('/node/') and path.endswith('/smart'):
                node_id = path.split('/')[2]
                result = self.graph_controller.delete_node_smart(node_id)
                self._send_json(result)
            
            # DELETE /node/{id} - Suppression simple
            elif path.startswith('/node/'):
                node_id = path.split('/')[-1]
                success = self.graph_controller.delete_node(node_id)
                
                if success:
                    self._send_json({'message': f'Nœud {node_id} supprimé'})
                else:
                    self._send_error("Nœud non trouvé", 404)
            
            # DELETE /edge/{source}/{target}
            elif path.startswith('/edge/'):
                parts = path.split('/')
                if len(parts) != 4:
                    self._send_error("Format: /edge/{source}/{target}")
                    return
                
                source = parts[2]
                target = parts[3]
                success = self.graph_controller.delete_edge(source, target)
                
                if success:
                    self._send_json({'message': f'Arête {source}-{target} supprimée'})
                else:
                    self._send_error("Arête non trouvée", 404)
            
            else:
                self._send_error(f"Route inconnue: {path}", 404)
        
        except Exception as e:
            self._send_error(str(e), 500)
    
    def log_message(self, format, *args):
        """Personnaliser les logs"""
        print(f"[{self.log_date_time_string()}] {format % args}")


def run_server(host='localhost', port=8000):
    """Lancer le serveur"""
    server_address = (host, port)
    httpd = HTTPServer(server_address, WasteGraphHandler)
    
    print(f"╔════════════════════════════════════════════╗")
    print(f"║   WasteGraph API Server v2.0               ║")
    print(f"║   Serveur démarré sur http://{host}:{port}   ║")
    print(f"╚════════════════════════════════════════════╝")
    print(f"\nEndpoints disponibles:")
    print(f"  GRAPH:")
    print(f"    GET    /graph")
    print(f"    POST   /graph/node")
    print(f"    POST   /graph/edge")
    print(f"    DELETE /node/{{id}}            (suppression simple)")
    print(f"    DELETE /node/{{id}}/smart      (suppression intelligente)")
    print(f"    DELETE /edge/{{source}}/{{target}}")
    print(f"    DELETE /graph")
    print(f"\n  CONSTRAINTS:")
    print(f"    GET    /constraints")
    print(f"    GET    /constraints/all")
    print(f"    POST   /constraints")
    print(f"    PUT    /constraints/{{id}}/toggle")
    print(f"\n  ALGORITHMS:")
    print(f"    GET    /algo/dijkstra?src=A&dst=Z&constraints={{...}}")
    print(f"    GET    /algo/coloring")
    print(f"\n  HISTORY:")
    print(f"    GET    /history/paths")
    print(f"    GET    /history/paths/{{id}}/replay")
    print(f"\nAppuyez sur Ctrl+C pour arrêter le serveur\n")
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✓ Serveur arrêté proprement")
        httpd.server_close()


if __name__ == '__main__':
    run_server()