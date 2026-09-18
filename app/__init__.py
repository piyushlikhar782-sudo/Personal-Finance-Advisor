from flask import Flask
from .config import Config
from .extensions import db, login_manager, migrate
from .models import Category, DEFAULT_CATEGORIES

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions
    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'views.index'
    migrate.init_app(app, db)

    # Register Blueprints
    from .routes import (
        auth_bp, income_bp, expense_bp, budget_bp,
        savings_bp, reports_bp, household_bp, ai_bp, views_bp
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(income_bp)
    app.register_blueprint(expense_bp)
    app.register_blueprint(budget_bp)
    app.register_blueprint(savings_bp)
    app.register_blueprint(reports_bp)
    app.register_blueprint(household_bp)
    app.register_blueprint(ai_bp)
    app.register_blueprint(views_bp)

    # Ensure tables and default categories exist
    with app.app_context():
        db.create_all()
        seed_default_categories()

    return app

def seed_default_categories():
    if Category.query.count() == 0:
        for cat_data in DEFAULT_CATEGORIES:
            cat = Category(
                name=cat_data['name'],
                type=cat_data['type'],
                icon=cat_data['icon'],
                color=cat_data['color']
            )
            db.session.add(cat)
        db.session.commit()
