from ..extensions import db

class Category(db.Model):
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    type = db.Column(db.String(20), nullable=False, default='discretionary') # essential, discretionary
    icon = db.Column(db.String(30), nullable=True, default='tag')
    color = db.Column(db.String(20), nullable=True, default='#6366F1')

    expenses = db.relationship('Expense', backref='category_rel', lazy=True)
    budgets = db.relationship('Budget', backref='category_rel', lazy=True)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type,
            'icon': self.icon,
            'color': self.color
        }

DEFAULT_CATEGORIES = [
    {'name': 'Housing & Rent', 'type': 'essential', 'icon': 'home', 'color': '#3B82F6'},
    {'name': 'Food & Groceries', 'type': 'essential', 'icon': 'shopping-cart', 'color': '#10B981'},
    {'name': 'Utilities & Bills', 'type': 'essential', 'icon': 'zap', 'color': '#F59E0B'},
    {'name': 'Transportation', 'type': 'essential', 'icon': 'truck', 'color': '#8B5CF6'},
    {'name': 'Healthcare & Medical', 'type': 'essential', 'icon': 'activity', 'color': '#EC4899'},
    {'name': 'Education & Courses', 'type': 'essential', 'icon': 'book', 'color': '#06B6D4'},
    {'name': 'Entertainment & Hobbies', 'type': 'discretionary', 'icon': 'film', 'color': '#F43F5E'},
    {'name': 'Dining Out & Cafes', 'type': 'discretionary', 'icon': 'coffee', 'color': '#FB923C'},
    {'name': 'Shopping & Apparel', 'type': 'discretionary', 'icon': 'shopping-bag', 'color': '#A855F7'},
    {'name': 'Travel & Vacation', 'type': 'discretionary', 'icon': 'compass', 'color': '#14B8A6'},
    {'name': 'Subscriptions & Tech', 'type': 'discretionary', 'icon': 'tv', 'color': '#6366F1'},
    {'name': 'Miscellaneous', 'type': 'discretionary', 'icon': 'more-horizontal', 'color': '#64748B'}
]
