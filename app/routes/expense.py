from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from ..models import Expense, Category
from ..extensions import db

expense_bp = Blueprint('expense', __name__, url_prefix='/api')

@expense_bp.route('/categories', methods=['GET'])
def get_categories():
    categories = Category.query.order_by(Category.name).all()
    return jsonify({'categories': [c.to_dict() for c in categories]})

@expense_bp.route('/expenses', methods=['GET'])
@login_required
def get_expenses():
    month_param = request.args.get('month') # YYYY-MM
    cat_param = request.args.get('category_id')
    query = Expense.query.filter_by(user_id=current_user.id)

    if month_param:
        try:
            year, month = map(int, month_param.split('-'))
            query = query.filter(
                extract('year', Expense.date) == year,
                extract('month', Expense.date) == month
            )
        except ValueError:
            pass

    if cat_param:
        try:
            query = query.filter_by(category_id=int(cat_param))
        except ValueError:
            pass

    expenses = query.order_by(Expense.date.desc()).all()
    total_amount = sum(e.amount for e in expenses)

    return jsonify({
        'expenses': [e.to_dict() for e in expenses],
        'total_amount': round(total_amount, 2)
    })

@expense_bp.route('/expenses', methods=['POST'])
@login_required
def create_expense():
    data = request.get_json() or {}
    category_id = data.get('category_id')
    amount = data.get('amount')
    date_str = data.get('date')
    note = data.get('note', '').strip()

    if not category_id or amount is None:
        return jsonify({'error': 'Category and amount are required'}), 400

    category = db.session.get(Category, category_id)

    if not category:
        return jsonify({'error': 'Invalid category ID'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    exp_date = date.today()
    if date_str:
        try:
            exp_date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

    expense = Expense(
        user_id=current_user.id,
        category_id=category.id,
        amount=amount,
        date=exp_date,
        note=note
    )

    db.session.add(expense)
    db.session.commit()

    return jsonify({
        'message': 'Expense logged successfully',
        'expense': expense.to_dict()
    }), 201

@expense_bp.route('/expenses/<int:expense_id>', methods=['DELETE'])
@login_required
def delete_expense(expense_id):
    expense = Expense.query.filter_by(id=expense_id, user_id=current_user.id).first()
    if not expense:
        return jsonify({'error': 'Expense record not found'}), 404

    db.session.delete(expense)
    db.session.commit()

    return jsonify({'message': 'Expense record deleted'})
