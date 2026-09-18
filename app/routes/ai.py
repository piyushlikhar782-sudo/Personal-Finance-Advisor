from datetime import date
from flask import Blueprint, request, jsonify
from flask_login import login_required, current_user
from ..services.ai_advisor import AIAdvisorService

ai_bp = Blueprint('ai', __name__, url_prefix='/api/ai')

@ai_bp.route('/insights', methods=['GET'])
@login_required
def get_insights():
    month = request.args.get('month', date.today().strftime('%Y-%m'))
    analysis = AIAdvisorService.analyze_spending_and_generate_insights(current_user, month)
    return jsonify(analysis)

@ai_bp.route('/chat', methods=['POST'])
@login_required
def chat():
    data = request.get_json() or {}
    user_prompt = data.get('prompt', '').strip()

    if not user_prompt:
        return jsonify({'error': 'Prompt is required'}), 400

    reply = AIAdvisorService.process_ai_chat_prompt(current_user, user_prompt)
    return jsonify({'reply': reply})
