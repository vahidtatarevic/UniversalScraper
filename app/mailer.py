import smtplib
from email.message import EmailMessage

from app.config import (
    BASE_URL,
    MAIL_FROM,
    SMTP_HOST,
    SMTP_PASSWORD,
    SMTP_PORT,
    SMTP_USER,
)


def send_verification_email(email, token):
    link = f"{BASE_URL}/verify?token={token}"
    if not SMTP_USER:
        # Development fallback: no mail server configured, so print the link
        # to the server console where it can be opened manually.
        print(f"[email] To: {email} | Verify your account: {link}")
        return

    message = EmailMessage()
    message["Subject"] = "Verify your Universal Scraper account"
    message["From"] = MAIL_FROM or SMTP_USER
    message["To"] = email
    message.set_content(
        "Click the link below to verify your email address:\n\n"
        f"{link}\n\n"
        "The link expires in 24 hours. "
        "If you did not sign up, you can ignore this email."
    )
    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as smtp:
        smtp.starttls()
        smtp.login(SMTP_USER, SMTP_PASSWORD)
        smtp.send_message(message)
