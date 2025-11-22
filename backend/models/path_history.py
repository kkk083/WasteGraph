from datetime import datetime
import json


class PathHistory:
    """Représente un calcul de chemin sauvegardé"""
    
    def __init__(self, history_id=None, source=None, destination=None,
                 path=None, distance=0, calculated_at=None,
                 constraints_snapshot=None, user_notes=None):
        self.id = history_id
        self.source = source
        self.destination = destination
        self.path = path or []
        self.distance = distance
        self.calculated_at = calculated_at or datetime.now()
        self.constraints_snapshot = constraints_snapshot or {}
        self.user_notes = user_notes
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'destination': self.destination,
            'path': self.path,
            'distance': self.distance,
            'calculated_at': self.calculated_at.isoformat() if self.calculated_at else None,
            'constraints_snapshot': self.constraints_snapshot,
            'user_notes': self.user_notes
        }
    
    @staticmethod
    def from_dict(data):
        return PathHistory(
            history_id=data.get('id'),
            source=data['source'],
            destination=data['destination'],
            path=data['path'] if isinstance(data['path'], list) else json.loads(data['path']),
            distance=data['distance'],
            calculated_at=datetime.fromisoformat(data['calculated_at']) if data.get('calculated_at') else None,
            constraints_snapshot=data.get('constraints_snapshot', {}),
            user_notes=data.get('user_notes')
        )