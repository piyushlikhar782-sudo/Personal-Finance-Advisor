from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models import User, Income, Expense, Category, Budget, SavingsGoal, MonthlyReport
from app.services.ai_advisor import AIAdvisorService

def run_seed():
    app = create_app()
    with app.app_context():
        print("Seeding demo database...")

        # Create Demo User (Freelancer)
        demo_user = User.query.filter_by(email='demo@example.com').first()
        if not demo_user:
            demo_user = User(
                name='Alex Rivers',
                email='demo@example.com',
                account_type='freelancer'
            )
            demo_user.set_password('password123')
            db.session.add(demo_user)
            db.session.commit()
            print("Created demo user: demo@example.com / password123")

        # Clear previous records for demo user to ensure clean seed
        Income.query.filter_by(user_id=demo_user.id).delete()
        Expense.query.filter_by(user_id=demo_user.id).delete()
        Budget.query.filter_by(user_id=demo_user.id).delete()
        SavingsGoal.query.filter_by(user_id=demo_user.id).delete()
        MonthlyReport.query.filter_by(user_id=demo_user.id).delete()
        db.session.commit()

        categories = {c.name: c.id for c in Category.query.all()}
        today = date.today()
        current_month = today.strftime('%Y-%m')
        
        # Calculate dates for current & past month
        prev_month_date = today.replace(day=1) - timedelta(days=10)
        prev_month = prev_month_date.strftime('%Y-%m')

        # Incomes for current month & past month (showing freelancer variable income)
        incomes = [
            # Current Month
            Income(user_id=demo_user.id, source='Client UX Project (Retainer)', amount=3200.0, date_received=today.replace(day=5), is_recurring=True, note='Monthly design contract'),
            Income(user_id=demo_user.id, source='Frontend Development Sprint', amount=1850.0, date_received=today.replace(day=14), is_recurring=False, note='Milestone payment'),
            Income(user_id=demo_user.id, source='Substack Newsletter & Consulting', amount=450.0, date_received=today.replace(day=18), is_recurring=True, note='Ad proceeds & 1-on-1 calls'),
            # Past Month
            Income(user_id=demo_user.id, source='Client UX Project (Retainer)', amount=3200.0, date_received=prev_month_date.replace(day=5), is_recurring=True),
            Income(user_id=demo_user.id, source='Brand Strategy Audit', amount=2400.0, date_received=prev_month_date.replace(day=12), is_recurring=False)
        ]
        db.session.add_all(incomes)

        # Expenses for current month
        expenses = [
            Expense(user_id=demo_user.id, category_id=categories.get('Housing & Rent', 1), amount=1450.0, date=today.replace(day=1), note='Apartment lease payment'),
            Expense(user_id=demo_user.id, category_id=categories.get('Food & Groceries', 2), amount=520.0, date=today.replace(day=8), note='Whole Foods & Trader Joe\'s'),
            Expense(user_id=demo_user.id, category_id=categories.get('Utilities & Bills', 3), amount=185.0, date=today.replace(day=4), note='Electricity & High Speed Fiber'),
            Expense(user_id=demo_user.id, category_id=categories.get('Transportation', 4), amount=130.0, date=today.replace(day=10), note='Transit pass & rideshares'),
            Expense(user_id=demo_user.id, category_id=categories.get('Healthcare & Medical', 5), amount=210.0, date=today.replace(day=3), note='Health insurance contribution'),
            Expense(user_id=demo_user.id, category_id=categories.get('Education & Courses', 6), amount=99.0, date=today.replace(day=11), note='Frontend Masters annual sub'),
            Expense(user_id=demo_user.id, category_id=categories.get('Entertainment & Hobbies', 7), amount=380.0, date=today.replace(day=15), note='Concert tickets & VR games'), # Overspending!
            Expense(user_id=demo_user.id, category_id=categories.get('Dining Out & Cafes', 8), amount=410.0, date=today.replace(day=16), note='Sushi night & espresso bar'), # Overspending!
            Expense(user_id=demo_user.id, category_id=categories.get('Subscriptions & Tech', 11), amount=85.0, date=today.replace(day=2), note='Figma, GitHub, ChatGPT Plus')
        ]
        db.session.add_all(expenses)
        db.session.commit()

        # Savings Goals
        goals = [
            SavingsGoal(user_id=demo_user.id, goal_name='Emergency Freelance Buffer (3 Mo)', target_amount=10000.0, current_amount=6500.0, target_date=today + timedelta(days=120)),
            SavingsGoal(user_id=demo_user.id, goal_name='MacBook Pro M4 Max Upgrade', target_amount=3500.0, current_amount=2100.0, target_date=today + timedelta(days=60)),
            SavingsGoal(user_id=demo_user.id, goal_name='Japan Autumn Travel Fund', target_amount=5000.0, current_amount=1800.0, target_date=today + timedelta(days=240))
        ]
        db.session.add_all(goals)
        db.session.commit()

        # Generate AI Budget & Report for current month
        print("Generating AI budget for current month...")
        AIAdvisorService.generate_recommended_budget(demo_user, current_month)

        print("Generating AI report for current month...")
        AIAdvisorService.analyze_spending_and_generate_insights(demo_user, current_month)

        print("Database seeded successfully!")

if __name__ == '__main__':
    run_seed()
