from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from ..models import Household, User, Income, Expense
from ..extensions import db

household_bp = Blueprint('household', __name__, url_prefix='/api/household')

@household_bp.route('/create', methods=['POST'])
@login_required
def create_household():
    data = request.get_json() or {}
    name = data.get('name', '').strip()

    if not name:
        return jsonify({'error': 'Household name is required'}), 400

    household = Household(name=name)
    db.session.add(household)
    db.session.flush()

    current_user.household_id = household.id
    current_user.account_type = 'household'
    db.session.commit()

    return jsonify({
        'message': f"Household '{household.name}' created!",
        'household': household.to_dict()
    }), 201

@household_bp.route('/join', methods=['POST'])
@login_required
def join_household():
    data = request.get_json() or {}
    invite_code = data.get('invite_code', '').strip().upper()

    if not invite_code:
        return jsonify({'error': 'Invite code is required'}), 400

    household = Household.query.filter_by(invite_code=invite_code).first()
    if not household:
        return jsonify({'error': 'Invalid invite code'}), 404

    current_user.household_id = household.id
    current_user.account_type = 'household'
    db.session.commit()

    return jsonify({
        'message': f"Successfully joined {household.name}!",
        'household': household.to_dict()
    })

@household_bp.route('/summary', methods=['GET'])
@login_required
def household_summary():
    if not current_user.household_id:
        return jsonify({'has_household': False, 'message': 'Not part of a household'})

    household = db.session.get(Household, current_user.household_id)

    members = household.members

    current_month = date.today().strftime('%Y-%m')
    year, month_num = map(int, current_month.split('-'))

    total_household_income = 0.0
    total_household_expenses = 0.0
    member_stats = []

    for m in members:
        m_incomes = Income.query.filter(
            Income.user_id == m.id,
            extract('year', Income.date_received) == year,
            extract('month', Income.date_received) == month_num
        ).all()
        m_inc = sum(i.amount for i in m_incomes)

        m_expenses = Expense.query.filter(
            Expense.user_id == m.id,
            extract('year', Expense.date) == year,
            extract('month', Expense.date) == month_num
        ).all()
        m_exp = sum(e.amount for e in m_expenses)

        total_household_income += m_inc
        total_household_expenses += m_exp

        member_stats.append({
            'user_id': m.id,
            'name': m.name,
            'income': round(m_inc, 2),
            'expenses': round(m_exp, 2),
            'savings': round(m_inc - m_exp, 2)
        })

    return jsonify({
        'has_household': True,
        'household_name': household.name,
        'invite_code': household.invite_code,
        'month': current_month,
        'total_income': round(total_household_income, 2),
        'total_expenses': round(total_household_expenses, 2),
        'total_savings': round(total_household_income - total_household_expenses, 2),
        'members': member_stats
    })
