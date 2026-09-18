import unittest
import json
from datetime import date
from app import create_app
from app.extensions import db
from app.models import User, Category, Income, Expense, Budget, SavingsGoal, MonthlyReport

class FinanceAdvisorTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config['TESTING'] = True
        self.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        self.client = self.app.test_client()

        with self.app.app_context():
            db.create_all()
            from app.__init__ import seed_default_categories
            seed_default_categories()

    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()

    def test_user_signup_and_login(self):
        # Signup
        res = self.client.post('/api/auth/signup', json={
            'name': 'Test User',
            'email': 'test@example.com',
            'password': 'password123',
            'account_type': 'freelancer'
        })
        self.assertEqual(res.status_code, 201)
        data = json.loads(res.data)
        self.assertEqual(data['user']['email'], 'test@example.com')
        self.assertEqual(data['user']['account_type'], 'freelancer')

        # Check me
        res_me = self.client.get('/api/auth/me')
        data_me = json.loads(res_me.data)
        self.assertTrue(data_me['authenticated'])

    def test_income_logging(self):
        # Create user
        self.client.post('/api/auth/signup', json={
            'name': 'Income Tester',
            'email': 'income@example.com',
            'password': 'password123'
        })

        # Log income
        res = self.client.post('/api/income', json={
            'source': 'Consulting Contract',
            'amount': 2500.0,
            'date_received': date.today().strftime('%Y-%m-%d'),
            'is_recurring': True,
            'note': 'Retainer'
        })
        self.assertEqual(res.status_code, 201)

        # Retrieve income
        res_get = self.client.get('/api/income')
        data_get = json.loads(res_get.data)
        self.assertEqual(len(data_get['incomes']), 1)
        self.assertEqual(data_get['total_amount'], 2500.0)

    def test_expense_logging_and_budget_gen(self):
        # Signup
        self.client.post('/api/auth/signup', json={
            'name': 'Expense Tester',
            'email': 'expense@example.com',
            'password': 'password123'
        })

        # Get a category ID
        res_cat = self.client.get('/api/categories')
        cats = json.loads(res_cat.data)['categories']
        cat_id = cats[0]['id']

        # Log income
        self.client.post('/api/income', json={
            'source': 'Salary',
            'amount': 4000.0,
            'date_received': date.today().strftime('%Y-%m-%d')
        })

        # Log expense
        res_exp = self.client.post('/api/expenses', json={
            'category_id': cat_id,
            'amount': 350.0,
            'date': date.today().strftime('%Y-%m-%d'),
            'note': 'Test Expense'
        })
        self.assertEqual(res_exp.status_code, 201)

        # Trigger AI Budget generation
        res_b = self.client.post('/api/budget/generate', json={
            'month': date.today().strftime('%Y-%m')
        })
        self.assertEqual(res_b.status_code, 200)

        # Check Report
        res_rep = self.client.get(f"/api/reports/{date.today().strftime('%Y-%m')}")
        self.assertEqual(res_rep.status_code, 200)
        rep_data = json.loads(res_rep.data)
        self.assertEqual(rep_data['summary']['total_income'], 4000.0)
        self.assertEqual(rep_data['summary']['total_expenses'], 350.0)

    def test_savings_goals(self):
        self.client.post('/api/auth/signup', json={
            'name': 'Saver',
            'email': 'saver@example.com',
            'password': 'password123'
        })

        # Create goal
        res_g = self.client.post('/api/savings-goals', json={
            'goal_name': 'Emergency Fund',
            'target_amount': 5000.0,
            'current_amount': 1000.0
        })
        self.assertEqual(res_g.status_code, 201)
        goal_id = json.loads(res_g.data)['goal']['id']

        # Deposit
        res_d = self.client.post(f'/api/savings-goals/{goal_id}/deposit', json={'amount': 500.0})
        self.assertEqual(res_d.status_code, 200)
        goal_data = json.loads(res_d.data)['goal']
        self.assertEqual(goal_data['current_amount'], 1500.0)

if __name__ == '__main__':
    unittest.main()
