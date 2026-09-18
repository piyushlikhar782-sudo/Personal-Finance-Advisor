# Personal Finance Advisor Bot 🤖💰

An AI-powered personal budgeting, expense-tracking, and financial counseling platform built with **Python (Flask + SQLAlchemy)** and a modern **Dark Glassmorphism Dashboard UI**.

![Tech Stack](https://img.shields.io/badge/Backend-Python%20%7C%20Flask%20%7C%20SQLAlchemy-blue)
![Frontend](https://img.shields.io/badge/Frontend-HTML5%20%7C%20CSS3%20%7C%20Chart.js-emerald)
![License](https://img.shields.io/badge/License-MIT-purple)

---

## 🌟 Key Features

1. **User Accounts & Profile Framing**
   - Secure authentication (email & hashed passwords using `werkzeug.security`).
   - Profile account types tailored to user needs: **Individual**, **Freelancer**, **Student**, and **Household**.

2. **Income Logging**
   - Support for multiple income streams (essential for freelancers with variable monthly income).
   - Recurring vs. variable payment tagging with date filters.

3. **Expense Tracking**
   - Categorized daily/weekly expense logging across essential (Housing, Food, Utilities, Transport, Health, Education) and discretionary (Entertainment, Dining, Shopping, Travel, Tech) categories.

4. **AI-Driven Budget Generator**
   - **50/30/20 Rule Baseline**: Auto-generates recommended monthly category limits.
   - **Freelancer Income Smoothing**: Calculates a **3-month rolling average income** to cushion budget targets during low-earning months.
   - **Overspending Threshold Flags**: Detects and highlights categories exceeding budgets by >10% or >25%.

5. **Savings Goals Tracker**
   - Track progress toward custom financial goals (e.g., Emergency Fund, Laptop Upgrade, Travel).
   - Deposit simulator with real-time visual progress rings and completion dates.

6. **Monthly Summary Report**
   - Executive cashflow breakdown (Income vs. Expenses, Savings Rate %).
   - Category spending split and actionable AI-generated recommendations for next month.
   - Includes printable/PDF media styling.

7. **Interactive AI Financial Assistant**
   - Embedded AI Chatbot widget providing natural language financial counseling and instant overspending diagnostics.

8. **Consolidated Household Budgets**
   - Joint budget management allowing multiple users to contribute to and view a unified household budget using shared invite codes.

---

## 🛠 Tech Stack

- **Backend**: Python 3.14, Flask 3.1, SQLAlchemy 2.0 (ORM), Flask-Login, Flask-Migrate
- **Database**: SQLite (Development) / PostgreSQL-ready ORM structure
- **Frontend**: HTML5, Vanilla JavaScript, Custom Glassmorphism CSS Design System, Chart.js, Feather Icons
- **Testing**: Python `unittest` framework

---

## 📁 Project Structure

```text
Personal-Finance-Advisor/
├── app/
│   ├── models/            # SQLAlchemy DB Models (User, Income, Expense, Category, Budget, Savings, Report, Household)
│   ├── routes/            # Flask API Blueprints (auth, income, expense, budget, savings, reports, household, ai, views)
│   ├── services/          # AI Advisor Engine (50/30/20 rule, rolling avg smoothing, chat bot)
│   ├── static/            # Frontend Assets (Glassmorphism CSS, Chart.js app.js)
│   ├── templates/         # Main SPA index.html layout
│   ├── config.py          # App configuration
│   └── extensions.py      # Extension instances (db, login_manager, migrate)
├── tests/                 # Automated unit test suite
├── run.py                 # Application server launcher
├── seed.py                # Database seeder utility
├── requirements.txt       # Python dependencies
└── README.md
```

---

## 🚀 Quickstart Guide

### 1. Clone the Repository
```bash
git clone https://github.com/piyushlikhar782-sudo/Personal-Finance-Advisor.git
cd Personal-Finance-Advisor
```

### 2. Set Up Virtual Environment & Install Dependencies
```bash
# Windows
py -m venv venv
.\venv\Scripts\activate

# Install requirements
pip install flask flask-sqlalchemy flask-login flask-migrate python-dotenv
```

### 3. Seed Demo Data (Optional)
Populates demo categories, freelancer income records, expenses, and active savings goals:
```bash
python seed.py
```

### 4. Run the Development Server
```bash
python run.py
```
Open your browser at **`http://127.0.0.1:5000`**.

---

## 🔑 Key API Endpoints

| Method | Endpoint | Description |
| :--- | :--- | :--- |
| `POST` | `/api/auth/signup` | Register new user account |
| `POST` | `/api/auth/login` | User login session |
| `POST` | `/api/income` | Log income record |
| `GET` | `/api/income` | Fetch monthly income records |
| `POST` | `/api/expenses` | Log expense transaction |
| `GET` | `/api/expenses` | Fetch category expense records |
| `POST` | `/api/budget/generate` | Trigger AI budget generation |
| `GET` | `/api/budget/:month` | Get budget limits vs actuals |
| `GET` | `/api/savings-goals` | Fetch savings goals |
| `POST` | `/api/savings-goals/:id/deposit` | Add deposit to goal |
| `GET` | `/api/reports/:month` | Fetch executive monthly report |
| `POST` | `/api/ai/chat` | Interactive AI advisor chat |
| `POST` | `/api/household/create` | Create shared household group |

---

## 🧪 Running Automated Tests

Run the backend test suite:
```bash
python -m unittest discover -s tests -p "test_*.py"
```

---

## 📜 License

This project is licensed under the [MIT License](LICENSE).