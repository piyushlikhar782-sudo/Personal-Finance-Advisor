from datetime import datetime, timezone
import json
from ..extensions import db

class MonthlyReport(db.Model):
    __tablename__ = 'monthly_reports'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    month = db.Column(db.String(7), nullable=False) # YYYY-MM
    total_income = db.Column(db.Float, default=0.0)
    total_expenses = db.Column(db.Float, default=0.0)
    total_savings = db.Column(db.Float, default=0.0)
    insights_json = db.Column(db.Text, nullable=True) # Stored as JSON string
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    __table_args__ = (
        db.UniqueConstraint('user_id', 'month', name='_user_report_month_uc'),
    )

    def get_insights(self):
        if self.insights_json:
            try:
                return json.loads(self.insights_json)
            except Exception:
                return []
        return []

    def set_insights(self, insights):
        self.insights_json = json.dumps(insights)

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'month': self.month,
            'total_income': round(self.total_income, 2),
            'total_expenses': round(self.total_expenses, 2),
            'total_savings': round(self.total_savings, 2),
            'net_savings_rate': round((self.total_savings / self.total_income * 100), 1) if self.total_income > 0 else 0,
            'insights': self.get_insights(),
            'created_at': self.created_at.isoformat() if self.created_at else None
        }
