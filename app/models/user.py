from datetime import datetime, timezone
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from ..extensions import db, login_manager

class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    account_type = db.Column(db.String(20), nullable=False, default='individual') # individual, student, freelancer, household
    household_id = db.Column(db.Integer, db.ForeignKey('households.id'), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    incomes = db.relationship('Income', backref='user', lazy=True, cascade="all, delete-orphan")
    expenses = db.relationship('Expense', backref='user', lazy=True, cascade="all, delete-orphan")
    budgets = db.relationship('Budget', backref='user', lazy=True, cascade="all, delete-orphan")
    savings_goals = db.relationship('SavingsGoal', backref='user', lazy=True, cascade="all, delete-orphan")
    reports = db.relationship('MonthlyReport', backref='user', lazy=True, cascade="all, delete-orphan")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def to_dict_basic(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'account_type': self.account_type
        }

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'account_type': self.account_type,
            'household_id': self.household_id,
            'household': self.household.to_dict() if self.household else None,
            'created_at': self.created_at.isoformat() if self.created_at else None
        }

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

