from flask import Blueprint, render_template, request, redirect, session, url_for, flash
from ..models import User
from .. import db

bp = Blueprint('profile', __name__, url_prefix='/profile')

@bp.route('/income', methods=['GET', 'POST'])
def set_income():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        try:
            inc = float(request.form['income'])
            user.income = inc
            db.session.commit()
            flash("Monthly income saved.", "success")
            return redirect(url_for('dashboard.dashboard'))
        except:
            flash("Please enter a valid number.", "danger")

    return render_template('set_income.html', income=user.income)

@bp.route('/update-income', methods=['GET', 'POST'])
def update_income():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    user = User.query.get(session['user_id'])

    if request.method == 'POST':
        new_income = request.form.get('income')
        try:
            user.income = float(new_income)
            db.session.commit()
            return redirect(url_for('dashboard.dashboard'))
        except ValueError:
            return render_template('update_income.html', error="Please enter a valid number", income=new_income)

    return render_template('update_income.html', income=user.income)