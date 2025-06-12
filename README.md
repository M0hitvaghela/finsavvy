
# FinSavvy

**AI‑Powered Personal Finance Manager**

---

## Contents
- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [AI & Insights](#ai--insights)
- [Screenshots](#screenshots)
- [Future Improvements](#future-improvements)
- [License](#license)

---

## Overview
FinSavvy is a Flask-based personal finance management web application that empowers users to take control of their financial lives. It enables users to track expenses, create budgets, and get smart AI-powered recommendations based on their financial behavior. FinSavvy combines clean UI design, dynamic budget tracking, and predictive analytics to help users achieve financial independence.

---

## Features

✅ **User Account Management**
- Email-based registration & login with OTP verification via Flask-Mail  
- Profile setup with monthly income and optional debt/emergency details

💸 **Transaction & Budgeting**
- Add, view, and categorize transactions (e.g., Rent, Food, Utilities)
- Create category-wise monthly budgets and track actual vs. target

📊 **Interactive Dashboard**
- Weekly and category-based spending visualization using Chart.js
- Budget usage alerts (e.g., 90% warning, over-limit detection)

🧠 **AI-Powered Insights**
- Linear regression-based monthly spend predictions with confidence intervals
- Smart budget tips (e.g., over-saving alerts, savings shortfalls, Nifty 50 investment advice)
- 50-20-20-7.5-3 budgeting benchmark support (Needs, Wants, Savings, Debt, Charity)

📧 **Smart Alerts**
- Email alerts if monthly spending exceeds income (trade deficit)
- Dynamic AI-generated savings/investment tips

🧾 **Other Highlights**
- Mobile responsive design with Bootstrap 5
- Static pages: Home, About, Contact, Privacy Policy, Terms

---

## Tech Stack

### 🧑‍💻 Backend
- Python 3, Flask, SQLAlchemy ORM
- Flask-Mail (email alerts), Flask-Session (session mgmt)
- Redis (session store)
- PostgreSQL (transaction + user data)
- scikit-learn (linear regression predictor)

### 🖼️ Frontend
- HTML5, CSS3, Bootstrap 5
- Chart.js (visualizations)
- Jinja2 (templating)

---

## Installation

1. **Clone the Repository**
   ```bash
   git clone https://github.com/M0hitvaghela/finsavvy.git
   cd finsavvy
   ```

2. **Create Virtual Environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**  
   Create a `.env` file or edit `config.py` with the following:
   ```
   FLASK_APP=run.py
   FLASK_ENV=development
   SECRET_KEY=your_secret_key
   SQLALCHEMY_DATABASE_URI=postgresql://username:password@localhost/dbname
   MAIL_SERVER=smtp.example.com
   MAIL_PORT=587
   MAIL_USERNAME=your_email
   MAIL_PASSWORD=your_password
   ```

5. **Initialize the Database**
   ```bash
   from app import create_app, db
   app = create_app()
   with app.app_context():
       db.create_all()
   ```

6. **Run the App**
   ```bash
   flask run
   ```

---

## Usage

- Go to `http://127.0.0.1:5000/`
- Register with your email and verify OTP
- Set income and start adding transactions and budgets
- Navigate to Dashboard to see spending, predictions, and alerts
- View dashboard for charts, budgets, and AI insights

---

## Project Structure
```
finsavvy/
│
├── app/
│   ├── __init__.py           # App factory & config
│   ├── models.py             # SQLAlchemy models: User, Transaction, Budget
│   ├── ai/
│   │   ├── predictor.py      # Monthly spend prediction logic
│   │   └── tips.py           # AI budgeting advice
│   ├── routes/               # Flask blueprints: auth, dashboard, budget, contact
│   ├── templates/            # Jinja2 HTML templates
│   └── static/
│       ├── css/              # Stylesheets (home.css, dashboard.css)
│       ├── js/               # JavaScript (Chart.js configs)
│       └── assets/           # Icons, logos
│
├── run.py                    # Entry point
├── config.py                 # Flask config settings
├── requirements.txt          # Python dependencies
└── README.md                 # Project documentation
```

---

## AI & Insights

FinSavvy uses linear regression on the user's past 6 months of spending data to:
- Predict next month’s spending
- Generate a range for realistic expectations
- Offer dynamic budget tips:
  - “You’re ₹2,000 over your savings goal. Consider reducing investments.”
  - “You’ve saved ₹10,000 this month. Consider Nifty 50 investment.”

It follows a modified **50-20-20-7.5-3** budget guideline:
- 50% Needs
- 20% Wants
- 20% Savings
- 7.5% Debt payments
- 3% Charity

---

## Screenshots

### Home Page

![Home Page](screenshot/home_page.png)

### Login Page

![Login Page](https://github.com/M0hitvaghela/finsavvy/blob/main/Screenshot/Login.png)

### Register Page

![Registration Page](screenshot/registration.png)

### Dashboard Page

![Dashboard Page](screenshot/dashboard.png)

### Contact Page

![Contact Page](screenshot/Contact.png)
---

## Future Improvements
- ✅ Export transaction data as PDF/Excel
- 🔐 Two-factor authentication
- 📈 Investment tracking with real-time market data
- 💬 In-app chatbot for financial queries

---

## License

 License © 2025 FinSavvy
