import os

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'personal-finance-advisor-secret-key-2026'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or 'sqlite:///' + os.path.join(os.path.abspath(os.path.dirname(__file__)), '..', 'finance.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
