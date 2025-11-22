import psycopg2
from psycopg2.extras import RealDictCursor
import sys
import os

# Ajouter le dossier racine au path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from config.config import DB_CONFIG


class Database:
    """Singleton pour gérer la connexion PostgreSQL"""
    
    _instance = None
    _connection = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance
    
    def connect(self):
        """Établir la connexion"""
        if self._connection is None or self._connection.closed:
            try:
                self._connection = psycopg2.connect(**DB_CONFIG)
                print("✓ Connexion à PostgreSQL réussie")
            except psycopg2.Error as e:
                print(f"✗ Erreur de connexion : {e}")
                raise
        return self._connection
    
    def get_cursor(self):
        """Obtenir un curseur (retourne des dicts)"""
        conn = self.connect()
        return conn.cursor(cursor_factory=RealDictCursor)
    
    def commit(self):
        """Commit les changements"""
        if self._connection:
            self._connection.commit()
    
    def rollback(self):
        """Annuler les changements"""
        if self._connection:
            self._connection.rollback()
    
    def close(self):
        """Fermer la connexion"""
        if self._connection and not self._connection.closed:
            self._connection.close()
            print("✓ Connexion fermée")