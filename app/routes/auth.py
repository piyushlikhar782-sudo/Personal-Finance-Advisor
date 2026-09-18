from flask import Blueprint, request, jsonify
from flask_login import login_user, logout_user, login_required, current_user
from ..models import User, Household
from ..extensions import db

auth_bp = Blueprint('auth', __name__, url_prefix='/api/auth')

@auth_bp.route('/signup', methods=['POST'])
def signup():
    data = request.get_json() or {}
    name = data.get('name', '').strip()
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')
    account_type = data.get('account_type', 'individual')
    invite_code = data.get('invite_code', '').strip().upper()

    if not name or not email or not password:
        return jsonify({'error': 'Name, email, and password are required'}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({'error': 'Email is already registered'}), 400

    household_id = None
    if invite_code:
        household = Household.query.filter_by(invite_code=invite_code).first()
        if household:
            household_id = household.id
            account_type = 'household'
        else:
            return jsonify({'error': 'Invalid household invite code'}), 400

    user = User(
        name=name,
        email=email,
        account_type=account_type,
        household_id=household_id
    )
    user.set_password(password)

    db.session.add(user)
    db.session.commit()

    login_user(user, remember=True)
    return jsonify({
        'message': 'Account created successfully',
        'user': user.to_dict()
    }), 201

@auth_bp.route('/login', methods=['POST'])
def login():
    data = request.get_json() or {}
    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    if not email or not password:
        return jsonify({'error': 'Email and password are required'}), 400

    user = User.query.filter_by(email=email).first()
    if not user or not user.check_password(password):
        return jsonify({'error': 'Invalid email or password'}), 401

    login_user(user, remember=True)
    return jsonify({
        'message': 'Logged in successfully',
        'user': user.to_dict()
    })

@auth_bp.route('/logout', methods=['POST'])
@login_required
def logout():
    logout_user()
    return jsonify({'message': 'Logged out successfully'})

@auth_bp.route('/me', methods=['GET'])
def me():
    if current_user.is_authenticated:
        return jsonify({
            'authenticated': True,
            'user': current_user.to_dict()
        })
    return jsonify({'authenticated': False, 'user': None})

@auth_bp.route('/demo-seed', methods=['POST'])
def demo_seed():
    from seed import run_seed
    run_seed()
    user = User.query.filter_by(email='demo@example.com').first()
    if user:
        login_user(user, remember=True)
        return jsonify({
            'message': 'Demo data loaded successfully!',
            'user': user.to_dict()
        })
    return jsonify({'error': 'Failed to seed demo data'}), 500

