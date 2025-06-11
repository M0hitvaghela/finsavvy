from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_mail import Mail
import redis

db   = SQLAlchemy()
mail = Mail()

def create_app():
    app = Flask(__name__)

    # — Secret & DB —
    app.config['SECRET_KEY'] = 'your_secret_key'
    app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:postgres@localhost/finsavvy_db'

    # — Redis-backed sessions —
    app.config['SESSION_TYPE']   = 'redis'
    app.config['SESSION_REDIS']  = redis.Redis(host='localhost', port=6379, db=0)
    app.config['SESSION_PERMANENT'] = False
    app.config['SESSION_USE_SIGNER'] = True

    # — Flask-Mail SMTP config —
    app.config.update(
        MAIL_SERVER   = 'smtp.gmail.com',
        MAIL_PORT     = 587,
        MAIL_USE_TLS  = True,
        MAIL_USERNAME = 'Your_mail@example.com',
        MAIL_PASSWORD = 'Your_password',
        MAIL_DEFAULT_SENDER = ('FinSavvy', 'Your_mail@example.com')
    )

    # — Init extensions —
    db.init_app(app)
    mail.init_app(app)
    Session(app)

    # — Register blueprints —
    from .routes.auth         import bp as auth_bp
    from .routes.dashboard    import bp as dashboard_bp
    from .routes.transactions import bp as tx_bp
    from .routes.budgets      import bp as budgets_bp
    from .routes.main import bp as main_bp
    from .routes.contact import bp as contact_bp
    from .routes.profile import bp as profile_bp
    from .routes.reports import reports_bp
    from .routes.goals import goals_bp

    app.register_blueprint(goals_bp,  url_prefix='/goals')  # ← register here
    app.register_blueprint(reports_bp)
    app.register_blueprint(profile_bp)
    app.register_blueprint(contact_bp)
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(tx_bp)
    app.register_blueprint(budgets_bp)

    return app
