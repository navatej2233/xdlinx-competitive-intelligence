# scripts/email_alerts.py

import smtplib
from email.message import EmailMessage

def send_email_alert(subject: str, body: str, to_email: str):
    """
    Production-ready email alert (Gmail SMTP).
    Uses App Password (recommended).
    """

    SMTP_SERVER = "smtp.gmail.com"
    SMTP_PORT = 587

    FROM_EMAIL = "your_email@gmail.com"        # replace
    FROM_PASSWORD = "your_app_password_here"   # Gmail App Password

    msg = EmailMessage()
    msg["From"] = FROM_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.set_content(body)

    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(FROM_EMAIL, FROM_PASSWORD)
            server.send_message(msg)

        return True

    except Exception as e:
        print("Email alert failed:", e)
        return False

