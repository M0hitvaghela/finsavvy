# app/routes/contact.py
from flask import Blueprint, render_template, request, flash, redirect, url_for
from flask_mail import Message
from .. import mail

bp = Blueprint('contact', __name__)

@bp.route('/contact', methods=['GET', 'POST'])
def contact():
    if request.method == 'POST':
        name    = request.form.get('name', '').strip()
        email   = request.form.get('email', '').strip()
        subject = request.form.get('subject', '').strip()
        message = request.form.get('message', '').strip()

        # Validate all fields
        if not name or not email or not subject or not message:
            flash("All fields (Name, Email, Subject, Message) are required.", "danger")
            return redirect(url_for('main.contact'))

        # Compose and send email
        try:
            msg = Message(
                subject=f"[Contact Form] {subject}",
                sender=email,
                recipients=['Your_mail@example.com'],  # replace with your support address
                body=(
                    f"Name:    {name}\n"
                    f"Email:   {email}\n"
                    f"Subject: {subject}\n\n"
                    f"Message:\n{message}"
                )
            )
            mail.send(msg)
            flash("Your message has been sent successfully!", "success")
            return redirect(url_for('main.contact'))

        except Exception as e:
            app.logger.error(f"Contact form error: {e}")
            flash("Something went wrong while sending your message. Please try again later.", "danger")
            return redirect(url_for('main.contact'))

    return render_template('contact.html')
