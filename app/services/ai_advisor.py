from datetime import datetime, date, timedelta
from sqlalchemy import extract, func
from ..models import Income, Expense, Category, Budget, SavingsGoal, User
from ..extensions import db

class AIAdvisorService:

    @staticmethod
    def get_monthly_income_data(user, target_month=None):
        """
        Calculates income for target_month (format YYYY-MM).
        For freelancers, calculates a rolling 3-month average income for budget smoothing.
        """
        if not target_month:
            target_month = date.today().strftime('%Y-%m')
        
        year, month = map(int, target_month.split('-'))
        
        # Direct income for target month
        direct_incomes = Income.query.filter(
            Income.user_id == user.id,
            extract('year', Income.date_received) == year,
            extract('month', Income.date_received) == month
        ).all()
        month_income = sum(i.amount for i in direct_incomes)

        # Handle freelancer rolling average
        is_freelancer_smoothed = False
        effective_income = month_income

        if user.account_type == 'freelancer':
            # Get income for past 3 months
            start_date = date(year, month, 1) - timedelta(days=90)
            past_incomes = Income.query.filter(
                Income.user_id == user.id,
                Income.date_received >= start_date
            ).all()
            
            if past_incomes:
                total_past_income = sum(i.amount for i in past_incomes)
                effective_income = max(month_income, total_past_income / 3.0)
                is_freelancer_smoothed = effective_income > month_income

        return {
            'actual_income': round(month_income, 2),
            'effective_income': round(effective_income, 2),
            'is_freelancer_smoothed': is_freelancer_smoothed
        }

    @staticmethod
    def generate_recommended_budget(user, target_month=None):
        """
        Generates budget limits per category based on 50/30/20 rule,
        user account type, and historical category spending proportions.
        """
        if not target_month:
            target_month = date.today().strftime('%Y-%m')

        income_data = AIAdvisorService.get_monthly_income_data(user, target_month)
        income = income_data['effective_income']

        if income <= 0:
            # Baseline fallback if no income logged yet
            income = 3000.0

        # Budget Allocation Rules by Account Type
        if user.account_type == 'student':
            essential_ratio = 0.60
            discretionary_ratio = 0.25
            savings_ratio = 0.15
        elif user.account_type == 'freelancer':
            essential_ratio = 0.45
            discretionary_ratio = 0.25
            savings_ratio = 0.30 # higher buffer for irregular income
        else: # individual, household
            essential_ratio = 0.50
            discretionary_ratio = 0.30
            savings_ratio = 0.20

        essential_pool = income * essential_ratio
        discretionary_pool = income * discretionary_ratio
        savings_pool = income * savings_ratio

        categories = Category.query.all()
        essential_cats = [c for c in categories if c.type == 'essential']
        discretionary_cats = [c for c in categories if c.type == 'discretionary']

        # Historical spending distribution for weighting
        historical_expenses = Expense.query.filter(Expense.user_id == user.id).all()
        
        cat_hist_totals = {}
        for exp in historical_expenses:
            cat_hist_totals[exp.category_id] = cat_hist_totals.get(exp.category_id, 0.0) + exp.amount

        # Distribute essential pool
        essential_hist_sum = sum(cat_hist_totals.get(c.id, 0) for c in essential_cats)
        recommended_budgets = []

        for c in essential_cats:
            if essential_hist_sum > 0 and c.id in cat_hist_totals:
                weight = cat_hist_totals[c.id] / essential_hist_sum
            else:
                weight = 1.0 / len(essential_cats) if essential_cats else 0
            limit = round(essential_pool * weight, 2)
            recommended_budgets.append({
                'category_id': c.id,
                'category_name': c.name,
                'category_type': c.type,
                'category_color': c.color,
                'limit_amount': max(50.0, limit)
            })

        # Distribute discretionary pool
        disc_hist_sum = sum(cat_hist_totals.get(c.id, 0) for c in discretionary_cats)
        for c in discretionary_cats:
            if disc_hist_sum > 0 and c.id in cat_hist_totals:
                weight = cat_hist_totals[c.id] / disc_hist_sum
            else:
                weight = 1.0 / len(discretionary_cats) if discretionary_cats else 0
            limit = round(discretionary_pool * weight, 2)
            recommended_budgets.append({
                'category_id': c.id,
                'category_name': c.name,
                'category_type': c.type,
                'category_color': c.color,
                'limit_amount': max(25.0, limit)
            })

        return {
            'month': target_month,
            'effective_income': income,
            'is_freelancer_smoothed': income_data['is_freelancer_smoothed'],
            'allocations': {
                'essential': round(essential_pool, 2),
                'discretionary': round(discretionary_pool, 2),
                'savings_target': round(savings_pool, 2)
            },
            'budgets': recommended_budgets
        }

    @staticmethod
    def analyze_spending_and_generate_insights(user, target_month=None):
        """
        Analyzes actual category expenses vs budgets, flags overspending,
        and creates personalized, account-type tailored actionable insights.
        """
        if not target_month:
            target_month = date.today().strftime('%Y-%m')

        year, month = map(int, target_month.split('-'))

        # Fetch monthly totals
        incomes = Income.query.filter(
            Income.user_id == user.id,
            extract('year', Income.date_received) == year,
            extract('month', Income.date_received) == month
        ).all()
        total_income = sum(i.amount for i in incomes)

        expenses = Expense.query.filter(
            Expense.user_id == user.id,
            extract('year', Expense.date) == year,
            extract('month', Expense.date) == month
        ).all()
        total_expenses = sum(e.amount for e in expenses)
        total_savings = total_income - total_expenses

        # Fetch month budgets
        budgets = Budget.query.filter(
            Budget.user_id == user.id,
            Budget.month == target_month
        ).all()
        budget_map = {b.category_id: b.limit_amount for b in budgets}

        # Category spending aggregation
        cat_spending = {}
        for e in expenses:
            cat_spending[e.category_id] = cat_spending.get(e.category_id, 0.0) + e.amount

        categories = Category.query.all()
        cat_map = {c.id: c for c in categories}

        insights = []
        overspend_flags = []

        # Category level variance analysis
        for cat_id, spent in cat_spending.items():
            cat = cat_map.get(cat_id)
            if not cat:
                continue
            
            budget_limit = budget_map.get(cat_id)
            if budget_limit and budget_limit > 0:
                pct = ((spent - budget_limit) / budget_limit) * 100
                if pct > 10.0: # Exceeding budget by > 10%
                    overspend_flags.append({
                        'category_name': cat.name,
                        'category_type': cat.type,
                        'spent': round(spent, 2),
                        'limit': round(budget_limit, 2),
                        'overspend_pct': round(pct, 1),
                        'excess_amount': round(spent - budget_limit, 2)
                    })
            elif spent > 25.0 and budget_map: # Unbudgeted spending when budgets exist
                overspend_flags.append({
                    'category_name': cat.name,
                    'category_type': cat.type,
                    'spent': round(spent, 2),
                    'limit': 0.0,
                    'overspend_pct': 100.0,
                    'excess_amount': round(spent, 2)
                })

        # Sort overspending flags by severity
        overspend_flags.sort(key=lambda x: x['overspend_pct'], reverse=True)

        # Generate Actionable Recommendations
        if overspend_flags:
            top_over = overspend_flags[0]
            if top_over['limit'] > 0:
                insights.append({
                    'type': 'warning',
                    'title': f"High Overspending in {top_over['category_name']}",
                    'message': f"You spent ${top_over['spent']:.2f}, which is {top_over['overspend_pct']}% over your budget of ${top_over['limit']:.2f}. Capping this category could save you ${top_over['excess_amount']:.2f} next month."
                })
            else:
                insights.append({
                    'type': 'warning',
                    'title': f"Unbudgeted Spending in {top_over['category_name']}",
                    'message': f"You spent ${top_over['spent']:.2f} in {top_over['category_name']} without setting a budget limit for it."
                })
            if len(overspend_flags) > 1:
                second = overspend_flags[1]
                if second['limit'] > 0:
                    insights.append({
                        'type': 'info',
                        'title': f"Watch Out: {second['category_name']}",
                        'message': f"You're currently {second['overspend_pct']}% above target limit (${second['spent']:.2f} vs ${second['limit']:.2f})."
                    })
                else:
                    insights.append({
                        'type': 'info',
                        'title': f"Watch Out: {second['category_name']}",
                        'message': f"Unbudgeted spending of ${second['spent']:.2f} detected."
                    })

        # Savings Rate Insight
        savings_rate = (total_savings / total_income * 100) if total_income > 0 else 0
        if savings_rate >= 20:
            insights.append({
                'type': 'success',
                'title': 'Great Savings Momentum!',
                'message': f"Your savings rate is {savings_rate:.1f}% this month (${total_savings:.2f}), exceeding the 20% benchmark!"
            })
        elif total_savings < 0:
            insights.append({
                'type': 'warning',
                'title': 'Monthly Cashflow Deficit',
                'message': f"You spent more than your total income this month (Net deficit of ${abs(total_savings):.2f}). Try cutting non-essential discretionary spending."
            })
        elif total_income > 0 and savings_rate < 10:
            insights.append({
                'type': 'warning',
                'title': 'Low Monthly Savings Rate',
                'message': f"You saved only {savings_rate:.1f}% of income (${total_savings:.2f}). Try cutting non-essential discretionary spending."
            })

        # Account Type Specific Advice
        if user.account_type == 'freelancer':
            inc_info = AIAdvisorService.get_monthly_income_data(user, target_month)
            if inc_info['is_freelancer_smoothed']:
                insights.append({
                    'type': 'tip',
                    'title': 'Freelancer Income Smoothing Active',
                    'message': f"Your current income (${total_income:.2f}) is below your 3-month average (${inc_info['effective_income']:.2f}). Budget limits have been auto-smoothed to prevent sudden austerity."
                })
            else:
                insights.append({
                    'type': 'tip',
                    'title': 'Freelancer Tax Reserve Suggestion',
                    'message': "Set aside 25-30% of variable incoming payments into a dedicated tax/emergency reserve."
                })
        elif user.account_type == 'student':
            insights.append({
                'type': 'tip',
                'title': 'Student Budget Optimization',
                'message': "Essential costs (housing & courses) dominate student spending. Utilize campus student perks, book exchanges, and meal prep."
            })
        elif user.account_type == 'household':
            insights.append({
                'type': 'tip',
                'title': 'Shared Household Sync',
                'message': "Consolidate recurring utility bills & bulk grocery orders with household members to unlock shared volume savings."
            })

        if not insights:
            insights.append({
                'type': 'success',
                'title': 'Healthy Financial Tracking',
                'message': "Your cashflow is balanced and aligned with your monthly goals. Keep up the consistent logging!"
            })

        return {
            'month': target_month,
            'summary': {
                'total_income': round(total_income, 2),
                'total_expenses': round(total_expenses, 2),
                'total_savings': round(total_savings, 2),
                'savings_rate': round(savings_rate, 1)
            },
            'overspend_flags': overspend_flags,
            'insights': insights
        }

    @staticmethod
    def process_ai_chat_prompt(user, user_prompt):
        """
        Interactive AI financial prompt processor. Synthesizes current user data
        and provides natural language financial counseling.
        """
        current_month = date.today().strftime('%Y-%m')
        analysis = AIAdvisorService.analyze_spending_and_generate_insights(user, current_month)

        goals = SavingsGoal.query.filter_by(user_id=user.id).all()
        goal_summary = ", ".join([f"{g.goal_name} (${g.current_amount:.0f}/${g.target_amount:.0f})" for g in goals]) if goals else "None active"

        user_prompt_lower = user_prompt.lower()

        # Rule-based natural language response generator with data context
        if 'save' in user_prompt_lower or 'saving' in user_prompt_lower:
            response = f"Based on your {current_month} data, your total income is **${analysis['summary']['total_income']:.2f}** and total expenses are **${analysis['summary']['total_expenses']:.2f}**, leaving **${analysis['summary']['total_savings']:.2f}** in net savings.\n\n"
            if analysis['overspend_flags']:
                flag = analysis['overspend_flags'][0]
                response += f"💡 **Top Savings Tip**: You spent **${flag['spent']:.2f}** on *{flag['category_name']}*, which is **{flag['overspend_pct']}% above budget**. Cutting back here could free up **${flag['excess_amount']:.2f}** per month for your savings goals ({goal_summary})."
            else:
                response += f"🎉 You're managing expenses well! Consider allocating your ${analysis['summary']['total_savings']:.2f} surplus into higher-yield savings or accelerating your goals: {goal_summary}."

        elif 'freelance' in user_prompt_lower or 'income' in user_prompt_lower or 'variable' in user_prompt_lower:
            inc_info = AIAdvisorService.get_monthly_income_data(user, current_month)
            response = f"As a **{user.account_type.capitalize()}**, managing cash flow variance is key. Your effective income benchmark is **${inc_info['effective_income']:.2f}**.\n\n"
            if inc_info['is_freelancer_smoothed']:
                response += f"⚠️ Your actual income logged this month (${inc_info['actual_income']:.2f}) is lower than your 3-month average. We've smoothed your budget so you don't panic, but prioritize essential bills first!"
            else:
                response += f"✅ Your income logged (${inc_info['actual_income']:.2f}) is strong! Put 20-30% of this month's surplus into a liquidity buffer for future low-earning months."

        elif 'budget' in user_prompt_lower or 'category' in user_prompt_lower or 'overspend' in user_prompt_lower:
            if analysis['overspend_flags']:
                response = f"⚠️ You have **{len(analysis['overspend_flags'])} category/categories over budget** this month:\n\n"
                for flag in analysis['overspend_flags']:
                    response += f"• **{flag['category_name']}**: Spent **${flag['spent']:.2f}** vs Limit **${flag['limit']:.2f}** ({flag['overspend_pct']}% over)\n"
                response += "\nClick 'Generate AI Budget' in the Budget tab to auto-rebalance your category targets!"
            else:
                response = f"✅ Excellent work! None of your categories have exceeded their set limits for {current_month}."

        else:
            response = f"Hello {user.name}! I'm your **Personal Finance Advisor Bot**.\n\nHere is your financial snapshot for **{current_month}**:\n"
            response += f"• **Income logged**: ${analysis['summary']['total_income']:.2f}\n"
            response += f"• **Expenses logged**: ${analysis['summary']['total_expenses']:.2f}\n"
            response += f"• **Net Savings**: ${analysis['summary']['total_savings']:.2f} ({analysis['summary']['savings_rate']}% savings rate)\n"
            response += f"• **Account Type**: {user.account_type.capitalize()}\n\n"
            response += "Feel free to ask me how to optimize your budget, set up savings goals, or analyze your spending patterns!"

        return response
