from flask import Blueprint, render_template, session, redirect, url_for
from datetime import date, datetime
from flask_mail import Message , Mail
from collections import defaultdict
from ..models import Transaction, Budget, User, Goal
from .. import db
from ..ai.predictor import predict_next_month_spend, generate_tips

bp = Blueprint('dashboard', __name__)
mail = Mail()
@bp.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    uid = session['user_id']
    user = User.query.get(uid)
    if not user or not user.income:
        return redirect(url_for('profile.set_income'))

    income = float(user.income)

    today = date.today()
    txs = (Transaction.query
           .filter_by(user_id=uid)
           .filter(db.extract('year', Transaction.date) == today.year)
           .filter(db.extract('month', Transaction.date) == today.month)
           .order_by(Transaction.date.desc())
           .all())

    # Weekly Spending
    week_sums = [0.0] * 4
    week_labels = [f'Week {i + 1}' for i in range(4)]
    for t in txs:
        w = min((t.date.day - 1) // 7, 3)
        week_sums[w] += float(t.amount)

    recent_tx = txs[:5]

    budgets = Budget.query.filter_by(user_id=uid).all()
    spent = {b.category.lower(): 0.0 for b in budgets}

    for t in txs:
        key = t.category.strip().lower()
        if key in spent:
            spent[key] += float(t.amount)

    # Predict Next Month Spend
    monthly = defaultdict(float)
    for t in Transaction.query.filter_by(user_id=uid):
        key = (t.date.year, t.date.month)
        monthly[key] += float(t.amount)

    last6 = sorted(monthly.items())[-6:]
    data_for_pred = [(i, amt) for i, (_, amt) in enumerate(last6)]
    if data_for_pred:
        pred = predict_next_month_spend(data_for_pred)
        lower, upper = round(pred * 0.95, 2), round(pred * 1.05, 2)
    else:
        pred = lower = upper = 0.0

    banner = None
    for b in budgets:
        limit = float(b.limit_amount) if b.limit_amount else 0.0
        pct = (spent.get(b.category.lower(), 0) / limit) if limit else 0
        if pct >= 0.9:
            banner = {'category': b.category, 'pct': int(pct * 100)}
            break

    over = None
    for b in budgets:
        limit = float(b.limit_amount) if b.limit_amount else 0.0
        if spent.get(b.category.lower(), 0) > limit:
            over = {
                'category': b.category,
                'over_amt': spent[b.category.lower()] - limit,
                'limit': limit
            }
            break

    # Ideal Budget - 50/20/20/7.5/3
    ideal = {
        'Needs': 0.50 * income,
        'Wants': 0.20 * income,
        'Savings': 0.20 * income,
        'Debt': 0.075 * income,
        'Charity': 0.03 * income
    }

    mapping = {
        'Needs': {'rent', 'groceries', 'utilities'},
        'Wants': {'dining', 'entertainment', 'subscriptions'},
        'Savings': {'savings', 'bank deposit', 'investment'},  # Updated ✅
        'Debt': {'loan', 'credit card'},
        'Charity': {'donation', 'charity'}
    }

    group_spent = {k: 0.0 for k in ideal}
    for t in Transaction.query.filter_by(user_id=uid):
        cat = t.category.strip().lower()
        assigned = False
        for group, keywords in mapping.items():
            if cat in keywords:
                group_spent[group] += float(t.amount)
                assigned = True
                break
        if not assigned:
            group_spent['Wants'] += float(t.amount)  # Fallback

    # Budgeting Tips
    ai_tips = []
    for group, actual in group_spent.items():
        if actual > ideal[group]:
            ai_tips.append(
                f"You’re over your {group.lower()} budget by ₹{actual - ideal[group]:.2f}. "
                f"Try cutting down on {group.lower()} expenses."
            )
        elif group == 'Savings' and actual < ideal['Savings']:
            surplus = ideal['Savings'] - actual
            ai_tips.append(
                f"You have ₹{surplus:.2f} free. Consider investing it in a Nifty 50 fund, "
                f"which historically grows ~12% annually."
            )
    if not ai_tips:
        ai_tips.append("Great job! You’re within all ideal budget percentages.")

    fin_tips = generate_tips(user, budgets, spent, recent_tx)

    pros = []
    cons = []

    if all(spent.get(b.category.lower(), 0) <= float(b.limit_amount or 0) for b in budgets):
        pros.append("You’re spending within all your set budgets.")

    if group_spent.get('Savings', 0) >= ideal.get('Savings', 0):
        pros.append("You're meeting or exceeding your savings goal. Great job!")

    if hasattr(user, 'debt_balance') and float(user.debt_balance or 0) == 0:
        pros.append("You’re debt-free! That’s a strong financial position.")

    for b in budgets:
        if float(spent.get(b.category.lower(), 0)) > float(b.limit_amount or 0):
            cons.append(f"Overspending in {b.category} by ₹{float(spent[b.category.lower()]) - float(b.limit_amount):.2f}.")

    if hasattr(user, 'has_insurance') and not user.has_insurance:
        cons.append("You're missing life or term insurance. Consider getting coverage.")

    if group_spent.get('Wants', 0) > ideal.get('Wants', 0):
        cons.append("Your discretionary ('wants') spending exceeds the ideal 20% of your income.")

    total_expense = sum(spent.values())
    trade_deficit = total_expense > income

    last_updated = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    monthly_expenses = sum(float(t.amount) for t in txs)

    if hasattr(user, 'emergency_amt'):
        if float(user.emergency_amt or 0) < 3 * monthly_expenses:
            cons.append("Your emergency fund is below 3 months of expenses.")

    goals = Goal.query.filter_by(user_id=uid).all()

    # --- Projection logic ---
    current_savings = group_spent.get('Savings', 0.0)
    growth_rate = 0.12
    years = list(range(1, 11))
    projections = [
        {'year': year, 'value': round(current_savings * ((1 + growth_rate) ** year), 2)}
        for year in years
    ]

    financially_free = False
    required_savings = None
    if monthly_expenses > 0:
        required_savings = 25 * monthly_expenses
        financially_free = current_savings >= required_savings

    # After computing trade_deficit, total_expense, and income:
    if trade_deficit:
        # Only send once per session/month
        sent_key = f"deficit_alert_sent_{today.year}_{today.month}"
        if not session.get(sent_key):
            # Mark as sent
            session[sent_key] = True

            # Compose the email
            msg = Message(
                subject="⚠️ FinSavvy Alert: Your Expenses Exceed Your Income",
                recipients=[user.email]
            )

            # Plain-text fallback
            msg.body = (
                f"Hello {user.name},\n\n"
                f"Our records show your total spending this month (₹{total_expense:,.2f}) "
                f"has exceeded your income (₹{income:,.2f}).\n"
                "This puts you in a trade deficit, which can erode savings over time.\n\n"
                "Consider reviewing your budgets and cutting back on non-essential items. "
                "Log in to FinSavvy for personalized tips.\n\n"
                "Best,\nThe FinSavvy Team"
            )

            # Rich HTML version
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background: #f4f6f8; padding: 20px;">
              <div style="max-width:600px; margin:auto; background:#fff; border-radius:8px;
                          box-shadow:0 2px 8px rgba(0,0,0,0.05); overflow:hidden;">
                <div style="background:#dc3545; color:#fff; padding:20px; text-align:center;">
                  <h1 style="margin:0; font-size:24px;">FinSavvy Alert</h1>
                </div>
                <div style="padding:30px; color:#333;">
                  <p style="font-size:16px;">Hello <strong>{user.name}</strong>,</p>
                  <p style="font-size:16px;">
                    We noticed that your <strong>total spending</strong> this month is
                    <span style="color:#dc3545; font-weight:bold;">₹{total_expense:,.2f}</span>, 
                    which exceeds your income of 
                    <span style="color:#28a745; font-weight:bold;">₹{income:,.2f}</span>.
                  </p>
                  <p style="font-size:16px;">
                    This places you in a <strong style="color:#dc3545;">trade deficit</strong>. 
                    Running a deficit month after month can deplete your savings and increase stress.
                  </p>
                  <hr style="border:none; border-top:1px solid #eee; margin:20px 0;" />
                  <h2 style="font-size:18px; color:#0d6efd; margin-bottom:10px;">
                    Next Steps
                  </h2>
                  <ul style="font-size:16px; line-height:1.5; color:#555;">
                    <li>Review your budgets in the FinSavvy dashboard.</li>
                    <li>Identify non-essential categories where you can cut back.</li>
                    <li>Enable spending alerts to stay within limits.</li>
                    <li>Check your AI-driven tips for personalized recommendations.</li>
                  </ul>
                  <p style="text-align:center; margin:30px 0;">
                    <a href="{url_for('dashboard.dashboard', _external=True)}"
                       style="background:#0d6efd; color:#fff; padding:12px 20px; 
                              text-decoration:none; border-radius:4px; font-size:16px;">
                      View Your Dashboard
                    </a>
                  </p>
                  <p style="font-size:14px; color:#888;">
                    If you believe this is an error, please contact our support at 
                    <a href="mailto:support@finsavvy.com" style="color:#0d6efd;">support@finsavvy.com</a>.
                  </p>
                </div>
                <div style="background:#fafafa; padding:15px; text-align:center; font-size:12px; color:#aaa;">
                  &copy; 2025 FinSavvy. All rights reserved.
                </div>
              </div>
            </body>
            </html>
            """
            mail.send(msg)

    return render_template('dashboard.html',
        name=session.get('user_name'),
        week_labels=week_labels,
        week_sums=week_sums,
        budgets=budgets,
        spent=spent,
        recent_tx=recent_tx,
        predicted_spend=round(pred, 2),
        pred_range=(lower, upper),
        context_months=len(last6),
        banner=banner,
        over=over,
        last_updated=last_updated,
        ideal=ideal,
        group_spent=group_spent,
        ai_tips=ai_tips,
        fin_tips=fin_tips,
        pros=pros,
        cons=cons,
        trade_deficit=trade_deficit,
        goals=goals,
        total_expense=total_expense,
        income=income,
        projections=projections,
        current_savings=round(current_savings, 2),
        financially_free=financially_free,
        required_savings=round(required_savings, 2) if required_savings else None
    )
