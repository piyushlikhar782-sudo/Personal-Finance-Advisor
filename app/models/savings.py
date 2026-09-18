from datetime import date
from ..extensions import db

class SavingsGoal(db.Model):
    __tablename__ = 'savings_goals'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    goal_name = db.Column(db.String(100), nullable=False)
    target_amount = db.Column(db.Float, nullable=False)
    current_amount = db.Column(db.Float, default=0.0)
    target_date = db.Column(db.Date, nullable=True)

    def to_dict(self):
        progress_pct = min(100.0, round((self.current_amount / self.target_amount) * 100, 1)) if self.target_amount > 0 else 0
        return {
            'id': self.id,
            'user_id': self.user_id,
            'goal_name': self.goal_name,
            'target_amount': round(self.target_amount, 2),
            'current_amount': round(self.current_amount, 2),
            'remaining_amount': round(max(0.0, self.target_amount - self.current_amount), 2),
            'progress_pct': progress_pct,
            'target_date': self.target_date.isoformat() if self.target_date else None
        }
