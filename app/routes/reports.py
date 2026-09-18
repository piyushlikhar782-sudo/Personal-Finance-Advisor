from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from sqlalchemy import extract
from ..models import MonthlyReport, Income, Expense, Category
from ..services.ai_advisor import AIAdvisorService
from ..extensions import db

reports_bp = Blueprint('reports', __name__, url_prefix='/api/reports')

@reports_bp.route('/<month>', methods=['GET'])
@login_required
def get_report(month):
    try:
        year, month_num = map(int, month.split('-'))
    except ValueError:
        return jsonify({'error': 'Invalid month format (use YYYY-MM)'}), 400

    # Auto generate or fetch
    analysis = AIAdvisorService.analyze_spending_and_generate_insights(current_user, month)

    # Category breakdown for chart & report
    expenses = Expense.query.filter(
        Expense.user_id == current_user.id,
        extract('year', Expense.date) == year,
        extract('month', Expense.date) == month_num
    ).all()

    cat_map = {}
    for exp in expenses:
        cat_name = exp.category_rel.name if exp.category_rel else 'Other'
        cat_color = exp.category_rel.color if exp.category_rel else '#64748B'
        if cat_name not in cat_map:
            cat_map[cat_name] = {'name': cat_name, 'color': cat_color, 'amount': 0.0}
        cat_map[cat_name]['amount'] += exp.amount

    category_breakdown = list(cat_map.values())
    category_breakdown.sort(key=lambda x: x['amount'], reverse=True)

    # Incomes breakdown
    incomes = Income.query.filter(
        Income.user_id == current_user.id,
        extract('year', Income.date_received) == year,
        extract('month', Income.date_received) == month_num
    ).all()
    inc_breakdown = [{'source': i.source, 'amount': i.amount} for i in incomes]

    return jsonify({
        'month': month,
        'user_name': current_user.name,
        'account_type': current_user.account_type,
        'summary': analysis['summary'],
        'category_breakdown': category_breakdown,
        'income_breakdown': inc_breakdown,
        'overspend_flags': analysis['overspend_flags'],
        'insights': analysis['insights']
    })
