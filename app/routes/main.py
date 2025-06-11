# app/routes/main.py
from flask import Blueprint, render_template

bp = Blueprint('main', __name__)

@bp.route('/')
def home():
    return render_template('home.html')

@bp.route('/about')
def about():
    return render_template('about.html')

@bp.route('/contact')
def contact():
    return render_template('contact.html')

@bp.route('/terms')
def terms():
    return render_template('terms.html')

@bp.route('/privacy')
def privacy():
    return render_template('privacy.html')
    
@bp.route('/blog/<slug>')
def blog_post(slug):
    if slug == 'top-10-saving-strategies':
        return render_template('blog/top_10_saving_strategies.html')
    else:
        return render_template('404.html'), 404

@bp.route('/case-study/<int:id>')
def case_study(id):
    # For demo, id=3 is Acme Co. You can extend this logic later to fetch from DB
    if id == 3:
        return render_template('case_study.html')
    else:
        return render_template('404.html'), 404
