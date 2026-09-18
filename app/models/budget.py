from ..extensions import db

class Budget(db.Model):
    __tablename__ = 'budgets'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('categories.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False) # Format: YYYY-MM
    limit_amount = db.Column(db.Float, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('user_id', 'category_id', 'month', name='_user_category_month_uc'),
    )

    def to_dict(self):
        cat = self.category_rel
        return {
            'id': self.id,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'category_name': cat.name if cat else 'Uncategorized',
            'category_type': cat.type if cat else 'discretionary',
            'category_color': cat.color if cat else '#6366F1',
            'month': self.month,
            'limit_amount': round(self.limit_amount, 2)
        }
