from datetime import datetime, timedelta


class Constraint:
    """Représente une contrainte avec cycle de vie"""
    
    def __init__(self, constraint_id=None, source=None, target=None, 
                 constraint_value=0, is_active=True, reason=None,
                 created_at=None, expiry_days=None, expires_at=None):
        self.id = constraint_id
        self.source = source
        self.target = target
        self.constraint_value = constraint_value
        self.is_active = is_active
        self.reason = reason
        self.created_at = created_at or datetime.now()
        self.expiry_days = expiry_days
        self.expires_at = expires_at
        
        # Calculer la date d'expiration si nécessaire
        if expiry_days and not expires_at:
            self.expires_at = self.created_at + timedelta(days=expiry_days)
    
    def is_expired(self):
        """Vérifier si la contrainte a expiré"""
        if not self.expires_at:
            return False
        return datetime.now() > self.expires_at
    
    def is_valid(self):
        """La contrainte est-elle valide ? (active ET non expirée)"""
        return self.is_active and not self.is_expired()
    
    def to_dict(self):
        return {
            'id': self.id,
            'source': self.source,
            'target': self.target,
            'constraint_value': self.constraint_value,
            'is_active': self.is_active,
            'is_expired': self.is_expired(),
            'is_valid': self.is_valid(),
            'reason': self.reason,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expiry_days': self.expiry_days,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None
        }
    
    @staticmethod
    def from_dict(data):
        return Constraint(
            constraint_id=data.get('id'),
            source=data['source'],
            target=data['target'],
            constraint_value=data['constraint_value'],
            is_active=data.get('is_active', True),
            reason=data.get('reason'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else None,
            expiry_days=data.get('expiry_days'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None
        )