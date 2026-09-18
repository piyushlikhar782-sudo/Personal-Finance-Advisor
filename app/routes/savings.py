from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..models import SavingsGoal
from ..extensions import db

savings_bp = Blueprint('savings', __name__, url_prefix='/api/savings-goals')

@savings_bp.route('', methods=['GET'])
@login_required
def get_savings_goals():
    goals = SavingsGoal.query.filter_by(user_id=current_user.id).order_by(SavingsGoal.id.desc()).all()
    total_target = sum(g.target_amount for g in goals)
    total_saved = sum(g.current_amount for g in goals)

    return jsonify({
        'goals': [g.to_dict() for g in goals],
        'total_target': round(total_target, 2),
        'total_saved': round(total_saved, 2)
    })

@savings_bp.route('', methods=['POST'])
@login_required
def create_savings_goal():
    data = request.get_json() or {}
    goal_name = data.get('goal_name', '').strip()
    target_amount = data.get('target_amount')
    current_amount = data.get('current_amount', 0.0)
    target_date_str = data.get('target_date')

    if not goal_name or target_amount is None:
        return jsonify({'error': 'Goal name and target amount are required'}), 400

    try:
        target_amount = float(target_amount)
        current_amount = float(current_amount)
        if target_amount <= 0:
            return jsonify({'error': 'Target amount must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid numerical values'}), 400

    target_date = None
    if target_date_str:
        try:
            target_date = datetime.strptime(target_date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid target date format (use YYYY-MM-DD)'}), 400

    goal = SavingsGoal(
        user_id=current_user.id,
        goal_name=goal_name,
        target_amount=target_amount,
        current_amount=max(0.0, current_amount),
        target_date=target_date
    )

    db.session.add(goal)
    db.session.commit()

    return jsonify({
        'message': 'Savings goal created successfully',
        'goal': goal.to_dict()
    }), 201

@savings_bp.route('/<int:goal_id>/deposit', methods=['POST'])
@login_required
def deposit_to_goal(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({'error': 'Savings goal not found'}), 404

    data = request.get_json() or {}
    amount = data.get('amount')

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Deposit amount must be positive'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid deposit amount'}), 400

    goal.current_amount += amount
    db.session.commit()

    return jsonify({
        'message': f'Deposited ${amount:.2f} to {goal.goal_name}!',
        'goal': goal.to_dict()
    })

@savings_bp.route('/<int:goal_id>', methods=['DELETE'])
@login_required
def delete_savings_goal(goal_id):
    goal = SavingsGoal.query.filter_by(id=goal_id, user_id=current_user.id).first()
    if not goal:
        return jsonify({'error': 'Savings goal not found'}), 404

    db.session.delete(goal)
    db.session.commit()

    return jsonify({'message': 'Savings goal deleted'})
