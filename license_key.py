from src.models.user import db
from datetime import datetime

class LicenseKey(db.Model):
    __tablename__ = 'license_keys'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    is_used = db.Column(db.Boolean, nullable=False, default=False)

    def __repr__(self):
        return f'<LicenseKey {self.key}>'

    def to_dict(self):
        return {
            'id': self.id,
            'key': self.key,
            'created_at': self.created_at.isoformat(),
            'is_used': self.is_used
        }

