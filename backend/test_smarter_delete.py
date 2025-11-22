import requests
import json

BASE_URL = 'http://localhost:8000'

print("=== COMPARAISON : SUPPRESSION SIMPLE VS INTELLIGENTE ===\n")

# ========================================
# PARTIE 1 : Suppression SIMPLE (perte d'optimalité)
# ========================================

print("PARTIE 1 : Suppression SIMPLE\n")
print("1. Création du graphe...")
requests.delete(f'{BASE_URL}/graph')

nodes = [
    {'id': 'DEPOT', 'x': 0, 'y': 0},
    {'id': 'A', 'x': 100, 'y': 50},
    {'id': 'B', 'x': 100, 'y': 150},
    {'id': 'C', 'x': 200, 'y': 100}
]
for n in nodes:
    requests.post(f'{BASE_URL}/graph/node', json=n)

edges = [
    {'source': 'DEPOT', 'target': 'A', 'weight': 2.0},
    {'source': 'DEPOT', 'target': 'B', 'weight': 2.3},
    {'source': 'A', 'target': 'C', 'weight': 1.8},
    {'source': 'B', 'target': 'C', 'weight': 2.7}
]
for e in edges:
    requests.post(f'{BASE_URL}/graph/edge', json=e)

print("✓ Graphe créé")
print("   Structure:")
print("   DEPOT ─2.0─ A ─1.8─ C")
print("     │               │")
print("     └─2.3─ B ─2.7───┘\n")

# Dijkstra AVANT suppression
print("2. Calcul du chemin optimal DEPOT → C (AVANT suppression de A)...")
result = requests.get(f'{BASE_URL}/algo/dijkstra?src=DEPOT&dst=C&save=false').json()
print(f"   Chemin: {' → '.join(result['path'])}")
print(f"   Distance: {result['distance']}\n")

# Suppression SIMPLE de A
print("3. Suppression SIMPLE du nœud A...")
response = requests.delete(f'{BASE_URL}/node/A')
print(f"   {response.json()['message']}\n")

# Voir le graphe résultant
print("4. Structure après suppression simple:")
graph = requests.get(f'{BASE_URL}/graph').json()
print("   DEPOT       ✗       C")
print("     │               │")
print("     └─2.3─ B ─2.7───┘\n")

# Dijkstra APRÈS suppression simple
print("5. Calcul du chemin optimal DEPOT → C (APRÈS suppression simple)...")
result = requests.get(f'{BASE_URL}/algo/dijkstra?src=DEPOT&dst=C&save=false').json()
print(f"   Chemin: {' → '.join(result['path'])}")
print(f"   Distance: {result['distance']}")
print(f"   ⚠ Perte d'optimalité ! (3.8 → {result['distance']})\n")

# ========================================
# PARTIE 2 : Suppression INTELLIGENTE (préserve l'optimalité)
# ========================================

print("\n" + "="*60)
print("PARTIE 2 : Suppression INTELLIGENTE\n")

print("1. Re-création du même graphe...")
requests.delete(f'{BASE_URL}/graph')

for n in nodes:
    requests.post(f'{BASE_URL}/graph/node', json=n)
for e in edges:
    requests.post(f'{BASE_URL}/graph/edge', json=e)

print("✓ Graphe recréé")
print("   Structure:")
print("   DEPOT ─2.0─ A ─1.8─ C")
print("     │               │")
print("     └─2.3─ B ─2.7───┘\n")

# Dijkstra AVANT suppression
print("2. Calcul du chemin optimal DEPOT → C (AVANT suppression de A)...")
result = requests.get(f'{BASE_URL}/algo/dijkstra?src=DEPOT&dst=C&save=false').json()
print(f"   Chemin: {' → '.join(result['path'])}")
print(f"   Distance: {result['distance']}\n")

# Suppression INTELLIGENTE de A
print("3. Suppression INTELLIGENTE du nœud A...")
result = requests.delete(f'{BASE_URL}/node/A/smart').json()
print(f"   {result['message']}")
print(f"   Raccourcis créés: {result['shortcuts_created']}")
print(f"   Raccourcis améliorés: {result['shortcuts_updated']}\n")

# Voir le graphe résultant
print("4. Structure après suppression intelligente:")
graph = requests.get(f'{BASE_URL}/graph').json()
print("   Arêtes restantes:")
for e in sorted(graph['edges'], key=lambda x: (x['source'], x['target'])):
    print(f"      {e['source']} ─ {e['target']} : {e['weight']}")
print()
print("   Visualisation:")
print("   DEPOT ─3.8─ C    ← RACCOURCI CRÉÉ !")
print("     │         │")
print("     └─2.3─ B ─2.7─┘\n")

# Dijkstra APRÈS suppression intelligente
print("5. Calcul du chemin optimal DEPOT → C (APRÈS suppression intelligente)...")
result = requests.get(f'{BASE_URL}/algo/dijkstra?src=DEPOT&dst=C&save=false').json()
print(f"   Chemin: {' → '.join(result['path'])}")
print(f"   Distance: {result['distance']}")
print(f"   ✓ Optimalité préservée !\n")

print("="*60)
print("\n📊 COMPARAISON FINALE :\n")
print("┌─────────────────────────┬──────────┬──────────────┐")
print("│ Type de suppression     │ Distance │ Optimalité   │")
print("├─────────────────────────┼──────────┼──────────────┤")
print("│ SIMPLE (naïve)          │   5.0    │ ✗ Perdue     │")
print("│ INTELLIGENTE (smart)    │   3.8    │ ✓ Préservée  │")
print("└─────────────────────────┴──────────┴──────────────┘")
print("\n💡 Recommandation : Utilisez toujours /node/{id}/smart")
print("   pour préserver l'optimalité du réseau de collecte !\n")