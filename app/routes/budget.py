from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from ..models import Budget, Expense, Category
from ..services.ai_advisor import AIAdvisorService
from ..extensions import db

budget_bp = Blueprint('budget', __name__, url_prefix='/api/budget')

@budget_bp.route('/<month>', methods=['GET'])
@login_required
def get_budget(month):
    # Fetch set budgets for month
    budgets = Budget.query.filter_by(user_id=current_user.id, month=month).all()

    try:
        year, month_num = map(int, month.split('-'))
    except ValueError:
        return jsonify({'error': 'Invalid month format (use YYYY-MM)'}), 400

    # Fetch actual expenses for month per category
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month_num
    ).all()

    actual_map = {}
    for exp in expenses:
        actual_map[exp.category_id] = actual_map.get(exp.category_id, 0.0) + exp.amount

    categories = Category.query.all()
    budget_map = {b.category_id: b for b in budgets}

    result = []
    total_budgeted = 0.0
    total_actual = 0.0

    for cat in categories:
        b_entry = budget_map.get(cat.id)
        limit = b_entry.limit_amount if b_entry else 0.0
        spent = actual_map.get(cat.id, 0.0)
        
        total_budgeted += limit
        total_actual += spent

        pct = (spent / limit * 100) if limit > 0 else 0
        is_over = spent > limit if limit > 0 else (spent > 0)

        result.append({
            'category_id': cat.id,
            'category_name': cat.name,
            'category_type': cat.type,
            'category_icon': cat.icon,
            'category_color': cat.color,
            'limit_amount': round(limit, 2),
            'spent_amount': round(spent, 2),
            'remaining_amount': round(limit - spent, 2),
            'spent_pct': round(pct, 1),
            'is_over': is_over
        })

    return jsonify({
        'month': month,
        'total_budgeted': round(total_budgeted, 2),
        'total_actual': round(total_actual, 2),
        'budgets': result
    })

@budget_bp.route('/generate', methods=['POST'])
@login_required
def generate_budget():
    data = request.get_json() or {}
    month = data.get('month', date.today().strftime('%Y-%m'))

    recommendation = AIAdvisorService.generate_recommended_budget(current_user, month)

    # Save generated recommendations to DB
    for item in recommendation['budgets']:
        cat_id = item['category_id']
        limit = item['limit_amount']
        
        existing = Budget.query.filter_by(
            user_id=current_user.id,
            category_id=cat_id,
            month=month
        ).first()

        if existing:
            existing.limit_amount = limit
        else:
            new_budget = Budget(
                user_id=current_user.id,
                category_id=cat_id,
                month=month,
                limit_amount=limit
            )
            db.session.add(new_budget)

    db.session.commit()

    return jsonify({
        'message': f'AI Budget for {month} generated and saved successfully!',
        'recommendation': recommendation
    })

@budget_bp.route('', methods=['POST'])
@login_required
def set_budget():
    data = request.get_json() or {}
    category_id = data.get('category_id')
    month = data.get('month')
    limit_amount = data.get('limit_amount')

    if not category_id or not month or limit_amount is None:
        return jsonify({'error': 'Category, month, and limit amount are required'}), 400

    try:
        limit_amount = float(limit_amount)
        if limit_amount < 0:
            return jsonify({'error': 'Limit amount cannot be negative'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid limit amount'}), 400

    existing = Budget.query.filter_by(
        user_id=current_user.id,
        category_id=category_id,
        month=month
    ).first()

    if existing:
        existing.limit_amount = limit_amount
    else:
        new_b = Budget(
            user_id=current_user.id,
            category_id=category_id,
            month=month,
            limit_amount=limit_amount
        )
        db.session.add(new_b)

    db.session.commit()
    return jsonify({'message': 'Budget updated successfully'})
