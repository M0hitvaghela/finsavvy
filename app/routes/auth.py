import random
from flask import (
    Blueprint, render_template, request,
    redirect, session, flash, url_for
)
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError

from .. import db, mail
from flask_mail import Message
from ..models import User  # make sure your User model is in app/models.py

bp = Blueprint('auth', __name__)

@bp.route('/')
@bp.route('/home')
def home():
    return render_template('home.html')


# STEP 1: Registration → send OTP
@bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name     = request.form['name']
        email    = request.form['email']
        password = request.form['password']

        # Check if user already exists
        existing_user = User.query.filter_by(email=email).first()
        if existing_user:
            flash("This email is already registered. Please log in or use a different email.", "warning")
            return render_template('register.html')

        # Store hashed password and info in session
        session['reg_name']      = name
        session['reg_email']     = email
        session['reg_password']  = generate_password_hash(password)

        # Generate OTP
        otp = f"{random.randint(100000, 999999)}"
        session['email_otp'] = otp

        # Compose email
        msg = Message("Your FinSavvy Registration OTP", recipients=[email])

        # Plaintext fallback
        msg.body = (
            f"Hello {name},\n\n"
            f"Your OTP for FinSavvy registration is: {otp}\n\n"
            "If you did not request this, you can ignore this email."
        )

        # Styled HTML email
        msg.html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
            <table style="max-width: 600px; margin: auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                <tr>
                    <td style="text-align: center;">
                        <h2 style="color: #0d6efd;">Welcome to FinSavvy!</h2>
                        <p style="font-size: 1rem; color: #333;">Hi <strong>{name}</strong>,</p>
                        <p style="font-size: 1rem; color: #555;">
                            Thank you for registering with <strong>FinSavvy</strong>. Please use the OTP below to verify your email address:
                        </p>
                        <div style="margin: 30px 0;">
                            <span style="display: inline-block; font-size: 1.5rem; letter-spacing: 4px; color: #0d6efd; font-weight: bold;">
                                {otp}
                            </span>
                        </div>
                        <p style="font-size: 0.95rem; color: #777;">
                            This OTP is valid for a limited time. If you didn’t initiate this registration, you can safely ignore this email.
                        </p>
                        <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                        <p style="font-size: 0.85rem; color: #aaa;">
                            &copy; 2025 FinSavvy. All rights reserved.<br>
                            <a href="#" style="color: #0d6efd; text-decoration: none;">Privacy Policy</a> |
                            <a href="#" style="color: #0d6efd; text-decoration: none;">Terms</a>
                        </p>
                    </td>
                </tr>
            </table>
        </body>
        </html>
        """

        # Send email
        mail.send(msg)

        return redirect(url_for('auth.verify_otp'))

    return render_template('register.html')



# STEP 2: Verify OTP → create user
@bp.route('/verify-otp', methods=['GET', 'POST'])
def verify_otp():
    if request.method == 'POST':
        entered = request.form['otp']
        real_otp = session.get('email_otp')

        if real_otp and entered == real_otp:
            # Create the new user
            try:
                new_user = User(
                    name          = session.pop('reg_name'),
                    email         = session.pop('reg_email'),
                    password_hash = session.pop('reg_password')
                )
                db.session.add(new_user)
                db.session.commit()
                # Cleanup OTP
                session.pop('email_otp', None)
                flash("Registration complete! Please log in.", "success")
                return redirect(url_for('auth.login'))

            except IntegrityError:
                db.session.rollback()
                flash("Email already registered.", "danger")
                return redirect(url_for('auth.register'))
        else:
            flash("Invalid OTP. Please try again.", "warning")

    return render_template('verify_otp.html')


@bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email    = request.form['email']
        password = request.form['password']

        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password_hash, password):
            session['user_id']   = user.id
            session['user_name'] = user.name
            return redirect(url_for('dashboard.dashboard'))
        else:
            flash("Invalid email or password.", "danger")

    return render_template('login.html')

@bp.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email'].lower().strip()
        user = User.query.filter_by(email=email).first()

        if user:
            otp = f"{random.randint(100000, 999999)}"
            session['reset_email'] = email
            session['reset_otp'] = otp

            msg = Message("FinSavvy Password Reset OTP", recipients=[email])

            # Plaintext fallback
            msg.body = (
                f"Hello,\n\n"
                f"Your OTP for resetting your FinSavvy password is: {otp}\n\n"
                "If you did not request this, you can ignore this email."
            )

            # HTML version
            msg.html = f"""
            <html>
            <body style="font-family: Arial, sans-serif; background-color: #f4f4f7; padding: 20px;">
                <table style="max-width: 600px; margin: auto; background-color: white; border-radius: 10px; padding: 30px; box-shadow: 0 2px 8px rgba(0,0,0,0.05);">
                    <tr>
                        <td style="text-align: center;">
                            <h2 style="color: #dc3545;">Password Reset Request</h2>
                            <p style="font-size: 1rem; color: #333;">Hi there,</p>
                            <p style="font-size: 1rem; color: #555;">
                                We received a request to reset your FinSavvy password. Please use the OTP below to proceed:
                            </p>
                            <div style="margin: 30px 0;">
                                <span style="display: inline-block; font-size: 1.5rem; letter-spacing: 4px; color: #dc3545; font-weight: bold;">
                                    {otp}
                                </span>
                            </div>
                            <p style="font-size: 0.95rem; color: #777;">
                                This OTP is valid for a limited time. If you didn’t make this request, you can safely ignore this email.
                            </p>
                            <hr style="margin: 30px 0; border: none; border-top: 1px solid #eee;">
                            <p style="font-size: 0.85rem; color: #aaa;">
                                &copy; 2025 FinSavvy. All rights reserved.<br>
                                <a href="#" style="color: #0d6efd; text-decoration: none;">Privacy Policy</a> |
                                <a href="#" style="color: #0d6efd; text-decoration: none;">Terms</a>
                            </p>
                        </td>
                    </tr>
                </table>
            </body>
            </html>
            """

            mail.send(msg)
            flash("An OTP has been sent to your email address.", "info")
            return redirect(url_for('auth.verify_reset_otp'))

        flash("No account found with that email address.", "danger")

    return render_template('forgot_password.html')


@bp.route('/verify-reset-otp', methods=['GET','POST'])
def verify_reset_otp():
    if request.method=='POST':
        if request.form['otp']==session.get('reset_otp'):
            return redirect(url_for('auth.reset_password'))
        flash("Invalid OTP.")
    return render_template('verify_reset_otp.html')

@bp.route('/reset-password', methods=['GET','POST'])
def reset_password():
    if request.method=='POST':
        pwd = request.form['password']
        # update user password
        user = User.query.filter_by(email=session.get('reset_email')).first()
        user.password_hash = generate_password_hash(pwd)
        db.session.commit()
        session.pop('reset_email',None)
        session.pop('reset_otp',None)
        flash("Password updated. Please log in.")
        return redirect(url_for('auth.login'))
    return render_template('reset_password.html')


@bp.route('/logout')
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for('auth.login'))
