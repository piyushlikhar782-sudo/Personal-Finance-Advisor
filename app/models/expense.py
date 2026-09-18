from datetime import date
from ..extensions import db

class Expense(db.Model):
    __tablename__ = 'expenses'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    date = db.Column(db.Date, nullable=False, default=date.today)
    note = db.Column(db.String(255), nullable=True)

    def to_dict(self):
        cat = self.category_rel
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': cat.name if cat else 'Uncategorized',
            'category_type': cat.type if cat else 'discretionary',
            'category_icon': cat.icon if cat else 'tag',
            'category_color': cat.color if cat else '#6366F1',
            'amount': round(self.amount, 2),
            'date': self.date.isoformat() if self.date else None,
            'note': self.note
        }
