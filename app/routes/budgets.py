from flask import Blueprint, render_template, request, session, redirect, url_for
from ..models import Budget
from .. import db

bp = Blueprint('budgets', __name__, url_prefix='/budgets')

@bp.route('/', methods=['GET', 'POST'])
def manage_budgets():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    uid = session['user_id']

    if request.method == 'POST':
        category = request.form['category'].strip().lower()
        limit = float(request.form['limit_amount'])

        existing = Budget.query.filter_by(user_id=uid, category=category).first()
        if existing:
            existing.limit_amount = limit
        else:
            new_budget = Budget(user_id=uid, category=category, limit_amount=limit)
            db.session.add(new_budget)

        db.session.commit()
        return redirect(url_for('budgets.manage_budgets'))

    budgets = Budget.query.filter_by(user_id=uid).all()
    return render_template('budget.html', budgets=budgets)
