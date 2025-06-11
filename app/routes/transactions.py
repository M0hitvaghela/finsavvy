from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from ..models import Transaction
from .. import db
from datetime import datetime

bp = Blueprint('tx', __name__)

@bp.route('/add-transaction', methods=['GET', 'POST'])
def add_transaction():
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # 1. Gather form data
        amt   = request.form.get('amount', type=float)
        cat   = request.form.get('category')
        date_ = request.form.get('date')
        desc  = request.form.get('description', '')

        # 2. Parse date
        try:
            dt = datetime.strptime(date_, '%Y-%m-%d').date()
        except ValueError:
            flash('Invalid date format. Use YYYY‑MM‑DD.')
            return redirect(url_for('tx.add_transaction'))

        # 3. Insert into DB
        tx = Transaction(
            user_id=session['user_id'],
            amount=amt,
            category=cat,
            date=dt,
            description=desc
        )
        db.session.add(tx)
        db.session.commit()
        flash('Transaction added!')
        return redirect(url_for('dashboard.dashboard'))

    # GET → show form
    return render_template('add_transaction.html')
