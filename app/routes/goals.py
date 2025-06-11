from flask import Blueprint, render_template, request, redirect, url_for, session, flash
from sqlalchemy import func

from .. import db
from ..models import Goal, Transaction

goals_bp = Blueprint('goals', __name__, url_prefix='/goals')

@goals_bp.route('/', methods=['GET'])
def list_goals():
    uid = session['user_id']
    goals = Goal.query.filter_by(user_id=uid).all()

    # compute saved_amount and convert target_amount to float, as before...
    for g in goals:
        total = (
            db.session.query(func.coalesce(func.sum(Transaction.amount), 0))
            .filter(Transaction.user_id==uid,
                    func.lower(Transaction.category)==g.name.lower())
            .scalar()
        )
        g.saved_amount = float(total)
        g.target_amount = float(g.target_amount)

    return render_template('goals/list.html', goals=goals)



@goals_bp.route('/add', methods=['GET','POST'])
def add_goal():
    if request.method=='POST':
        g = Goal(
            user_id=session['user_id'],
            name=request.form['name'],
            target_amount=float(request.form['target_amount']),
            due_date=request.form.get('due_date') or None
        )
        db.session.add(g); db.session.commit()
        flash('Goal created!', 'success')
        return redirect(url_for('goals.list_goals'))
    return render_template('goals/form.html')

@goals_bp.route('/update/<int:id>', methods=['GET','POST'])
def update_goal(id):
    g = Goal.query.get_or_404(id)
    if request.method=='POST':
        g.name = request.form['name']
        g.target_amount = float(request.form['target_amount'])
        g.due_date = request.form.get('due_date') or None
        db.session.commit()
        flash('Goal updated.', 'success')
        return redirect(url_for('goals.list_goals'))
    return render_template('goals/form.html', goal=g)

@goals_bp.route('/delete/<int:id>', methods=['POST'])
def delete_goal(id):
    g = Goal.query.get_or_404(id)
    db.session.delete(g); db.session.commit()
    flash('Goal removed.', 'info')
    return redirect(url_for('goals.list_goals'))
