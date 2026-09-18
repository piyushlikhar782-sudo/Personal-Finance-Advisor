from .auth import auth_bp
from .income import income_bp
from .expense import expense_bp
from .budget import budget_bp
from .savings import savings_bp
from .reports import reports_bp
from .household import household_bp
from .ai import ai_bp
from .views import views_bp

__all__ = [
    'auth_bp',
    'income_bp',
    'expense_bp',
    'budget_bp',
    'savings_bp',
    'reports_bp',
    'household_bp',
    'ai_bp',
    'views_bp'
]
