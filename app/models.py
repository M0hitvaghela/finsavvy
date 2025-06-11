from . import db

class Transaction(db.Model):
    __tablename__ = 'transactions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)
    date = db.Column(db.Date, nullable=False)
    description = db.Column(db.String(200))

class Budget(db.Model):
    __tablename__ = 'budgets'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    category = db.Column(db.String(50), nullable=False)
    limit_amount = db.Column(db.Float, nullable=False)

class User(db.Model):
    __tablename__ = 'users'
    id             = db.Column(db.Integer, primary_key=True)
    name           = db.Column(db.String(100), nullable=False)
    email          = db.Column(db.String(100), unique=True, nullable=False)
    password_hash  = db.Column(db.String(200), nullable=False)
    income         = db.Column(db.Numeric(10,2), nullable=True)   # NEW
    created_at     = db.Column(db.DateTime, server_default=db.func.now())
    
class Goal(db.Model):
    __tablename__ = 'goals'
    id           = db.Column(db.Integer, primary_key=True)
    user_id      = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    name         = db.Column(db.String(100), nullable=False)
    target_amount= db.Column(db.Numeric(12,2), nullable=False)
    saved_amount = db.Column(db.Numeric(12,2), nullable=False, default=0)
    due_date     = db.Column(db.Date, nullable=True)  # optional deadline
    created_at   = db.Column(db.DateTime, server_default=db.func.now())
