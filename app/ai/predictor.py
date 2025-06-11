# app/ai/predictor.py
import pandas as pd
from sklearn.linear_model import LinearRegression

def predict_next_month_spend(transactions):
    """
    transactions: list of (month_idx, amount) tuples for past N months
    returns: float predicted spend
    """
    if not transactions:
        return 0.0

    df = pd.DataFrame(transactions, columns=['month_idx', 'amount'])
    model = LinearRegression().fit(df[['month_idx']], df['amount'])
    next_month = df['month_idx'].max() + 1
    predicted = model.predict([[next_month]])[0]
    return float(predicted)


def generate_tips(user, budgets, spent, recent_txs):
    """
    user: User model instance (has income, maybe emergency_amt, has_insurance, debt_balance)
    budgets: list of Budget objects
    spent: dict mapping category -> float (this month's spend)
    recent_txs: list of Transaction objects (this month)
    returns: list of strings
    """
    tips = []
    income = float(user.income or 0.0)

    # 1) 50/20/20 Budgeting Rule Check
    needs_cats = {'Rent / Mortgage', 'Groceries', 'Utilities'}
    needs = sum(spent.get(cat, 0.0) for cat in needs_cats)
    total_spent = sum(spent.values())
    wants = total_spent - needs

    if income > 0:
        if wants > 0.20 * income:
            tips.append(
                f"Your wants spending is ₹{wants:.2f}, above the 20% target of ₹{0.20 * income:.2f}. "
                "Consider cutting back on non‑essentials."
            )
        if needs > 0.50 * income:
            tips.append(
                f"Essentials are at ₹{needs:.2f}, over 50% of your income. Look into cheaper alternatives for utilities or housing."
            )

    # 2) Emergency Fund
    emergency_amt = getattr(user, 'emergency_amt', 0.0)
    monthly_exp = getattr(user, 'monthly_expenses', 0.0)

    if emergency_amt is not None and monthly_exp:
        target = 6 * float(monthly_exp)
        if float(emergency_amt) < target:
            diff = target - float(emergency_amt)
            tips.append(
                f"You’re ₹{diff:.2f} shy of a 6‑month emergency fund. "
                f"Allocate part of your savings each month until you reach ₹{target:.2f}."
            )

    # 3) Insurance
    if hasattr(user, 'has_insurance') and not user.has_insurance:
        tips.append("You have no life or term insurance. Protect your dependents by getting at least a term life plan.")

    # 4) Debt
    debt = float(getattr(user, 'debt_balance', 0.0))
    if debt > 0:
        tips.append(
            f"You have outstanding debt of ₹{debt:.2f}. Prioritize high‑interest balances first (e.g. credit cards)."
        )

    # 5) Budget Overruns
    for b in budgets:
        limit = float(b.limit_amount or 0.0)
        actual = float(spent.get(b.category, 0.0))
        if actual > limit and limit > 0:
            over = actual - limit
            tips.append(
                f"You’re ₹{over:.2f} over on your '{b.category}' budget. "
                "Adjust your spending or consider increasing your limit if it's consistently low."
            )

    # 6) Recent Spending Spike
    if len(recent_txs) >= 2:
        latest = float(recent_txs[0].amount)
        previous = float(recent_txs[1].amount)
        if previous > 0 and latest > 1.5 * previous:
            tips.append(
                f"Your latest purchase (₹{latest:.2f}) is 50% higher than the prior one. "
                "Check whether it was a one‑off or recurring cost."
            )

    # 7) All good fallback
    if not tips:
        tips.append("All looks good! You’re on track with your budgets, debt, and emergency fund.")

    return tips
