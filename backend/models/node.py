class Node:
    """Représente un point de collecte"""
    
    def __init__(self, node_id, x=0, y=0, capacity=0):
        self.id = node_id
        self.x = x
        self.y = y
        self.capacity = capacity
    
    def to_dict(self):
        """Conversion en dictionnaire pour JSON"""
        return {
            'id': self.id,
            'x': self.x,
            'y': self.y,
            'capacity': self.capacity
        }
    
    @staticmethod
    def from_dict(data):
        """Créer un Node depuis un dict"""
        return Node(
            node_id=data['id'],
            x=data['x'],
            y=data['y'],
            capacity=data.get('capacity', 0)
        )