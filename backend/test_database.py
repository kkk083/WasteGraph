import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from backend.database.connection import Database

# Test
db = Database()

try:
    db.connect()
    
    cursor = db.get_cursor()
    
    # Vérifier version PostgreSQL
    cursor.execute("SELECT version();")
    version = cursor.fetchone()
    print(f"PostgreSQL: {version['version'][:50]}...")
    
    # Compter les tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public'
    """)
    tables = cursor.fetchall()
    print(f"\nTables créées:")
    for table in tables:
        print(f"  - {table['table_name']}")
    
    cursor.close()
    
except Exception as e:
    print(f"❌ Erreur: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()