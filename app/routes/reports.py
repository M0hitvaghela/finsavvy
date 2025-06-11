from flask import Blueprint, render_template, make_response, session, redirect, url_for
from xhtml2pdf import pisa
from io import BytesIO
from datetime import date, datetime
from collections import defaultdict
from ..models import Transaction, Budget, User
from ..ai.predictor import predict_next_month_spend

reports_bp = Blueprint('reports', __name__, url_prefix='/dashboard')

@reports_bp.route('/report/pdf')
def generate_pdf_report():
    # --- Authentication check ---
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    uid = session['user_id']
    user = User.query.get(uid)
    if not user or not user.income:
        return redirect(url_for('profile.set_income'))

    # --- Gather the same data as dashboard ---
    income = float(user.income)
    today = date.today()

    # Transactions this month
    txs = (Transaction.query
           .filter_by(user_id=uid)
           .filter(Transaction.date.between(
               date(today.year, today.month, 1),
               date(today.year, today.month, today.day)))
           .order_by(Transaction.date.desc())
           .all())

    # Budgets and spent
    budgets = Budget.query.filter_by(user_id=uid).all()
    spent = defaultdict(float)
    for t in txs:
        spent[t.category.lower()] += float(t.amount)

    # Prediction
    monthly_totals = defaultdict(float)
    for t in Transaction.query.filter_by(user_id=uid):
        key = (t.date.year, t.date.month)
        monthly_totals[key] += float(t.amount)
    last6 = sorted(monthly_totals.items())[-6:]
    data_for_pred = [(i, amt) for i, (_, amt) in enumerate(last6)]
    if data_for_pred:
        pred = predict_next_month_spend(data_for_pred)
        lower, upper = round(pred * 0.95, 2), round(pred * 1.05, 2)
    else:
        pred = lower = upper = 0.0

    # Recent transactions
    recent_tx = txs[:5]

    # Last updated
    last_updated = datetime.now().strftime("%B %d, %Y %H:%M")

    # --- Render HTML template ---
    html = render_template(
        "pdf/dashboard_report.html",
        name=user.name,
        income=income,
        predicted_spend=round(pred, 2),
        pred_range=(lower, upper),
        last_updated=last_updated,
        budgets=budgets,
        spent=spent,
        recent_tx=recent_tx
    )

    # --- Generate PDF ---
    pdf_io = BytesIO()
    status = pisa.CreatePDF(html, dest=pdf_io)
    if status.err:
        return "PDF generation failed", 500

    resp = make_response(pdf_io.getvalue())
    resp.headers["Content-Type"] = "application/pdf"
    resp.headers["Content-Disposition"] = \
        f"attachment; filename=FinSavvy_Report_{today.strftime('%Y%m')}.pdf"
    return resp
