from datetime import datetime, timezone
import random
import string
from ..extensions import db

def generate_invite_code():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))

class Household(db.Model):
    __tablename__ = 'households'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    invite_code = db.Column(db.String(10), unique=True, nullable=False, default=generate_invite_code)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    members = db.relationship('User', backref='household', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'invite_code': self.invite_code,
            'member_count': len(self.members),
            'members': [m.to_dict_basic() for m in self.members],
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
