class Edge:
    """Représente une route entre deux points"""
    
    def __init__(self, source, target, weight, constraint_value=0):
        self.source = source
        self.target = target
        self.weight = weight
        self.constraint_value = constraint_value  # Contrainte par défaut en BDD
    
    def total_cost(self, custom_constraint=None):
        """
        Coût total avec possibilité de contrainte personnalisée
        
        Args:
            custom_constraint: Contrainte temporaire (override la BDD)
        """
        constraint = custom_constraint if custom_constraint is not None else self.constraint_value
        return self.weight + constraint
    
    def to_dict(self):
        return {
            'source': self.source,
            'target': self.target,
            'weight': self.weight,
            'constraint_value': self.constraint_value
        }
    
    @staticmethod
    def from_dict(data):
        return Edge(
            source=data['source'],
            target=data['target'],
            weight=data['weight'],
            constraint_value=data.get('constraint_value', 0)
        )