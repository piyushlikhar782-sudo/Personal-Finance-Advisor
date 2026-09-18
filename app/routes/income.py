from datetime import datetime, date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from ..models import Income
from ..extensions import db

income_bp = Blueprint('income', __name__, url_prefix='/api/income')

@income_bp.route('', methods=['GET'])
@login_required
def get_incomes():
    month_param = request.args.get('month') # YYYY-MM
    query = Income.query.filter_by(user_id=current_user.id)

    if month_param:
        try:
            year, month = map(int, month_param.split('-'))
            query = query.filter(
                extract('year', Income.date_received) == year,
                extract('month', Income.date_received) == month
            )
        except ValueError:
            pass

    incomes = query.order_by(Income.date_received.desc()).all()
    total_amount = sum(i.amount for i in incomes)

    return jsonify({
        'incomes': [i.to_dict() for i in incomes],
        'total_amount': round(total_amount, 2)
    })

@income_bp.route('', methods=['POST'])
@login_required
def create_income():
    data = request.get_json() or {}
    source = data.get('source', '').strip()
    amount = data.get('amount')
    date_str = data.get('date_received')
    is_recurring = data.get('is_recurring', False)
    note = data.get('note', '').strip()

    if not source or amount is None:
        return jsonify({'error': 'Source and amount are required'}), 400

    try:
        amount = float(amount)
        if amount <= 0:
            return jsonify({'error': 'Amount must be greater than zero'}), 400
    except (ValueError, TypeError):
        return jsonify({'error': 'Invalid amount'}), 400

    date_received = date.today()
    if date_str:
        try:
            date_received = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return jsonify({'error': 'Invalid date format (use YYYY-MM-DD)'}), 400

    income = Income(
        user_id=current_user.id,
        source=source,
        amount=amount,
        date_received=date_received,
        is_recurring=bool(is_recurring),
        note=note
    )

    db.session.add(income)
    db.session.commit()

    return jsonify({
        'message': 'Income logged successfully',
        'income': income.to_dict()
    }), 201

@income_bp.route('/<int:income_id>', methods=['DELETE'])
@login_required
def delete_income(income_id):
    income = Income.query.filter_by(id=income_id, user_id=current_user.id).first()
    if not income:
        return jsonify({'error': 'Income record not found'}), 404

    db.session.delete(income)
    db.session.commit()

    return jsonify({'message': 'Income record deleted'})
