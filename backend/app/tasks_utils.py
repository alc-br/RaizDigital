"""
Utility tasks for sending email notifications.

This module defines Celery tasks used to send emails.  If SMTP
configuration is not provided, the email contents are logged to the
console for development purposes.  In production, configure SMTP
settings via environment variables to enable real email delivery.
"""
import smtplib
from email.mime.text import MIMEText
from typing import Optional

from .config import get_settings
from celery import shared_task


@shared_task(name="send_email_task")
def send_email_task(to_email: str, subject: str, body: str) -> None:
    """
    Celery task to send an email to the specified recipient.

    Uses SMTP credentials provided in configuration. If SMTP is not
    configured, falls back to printing the email contents to stdout.
    """
    settings = get_settings()
    # If SMTP isn't configured, just log the email to the console
    if not settings.smtp_server or not settings.smtp_username:
        print("=== EMAIL ===")
        print(f"To: {to_email}")
        print(f"Subject: {subject}")
        print(body)
        print("=== END EMAIL ===")
        return
    # Construct MIME message
    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = settings.email_sender
    msg["To"] = to_email
    # Send via SMTP
    try:
        with smtplib.SMTP(settings.smtp_server, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_username, settings.smtp_password)
            server.send_message(msg)
    except Exception as exc:
        # In production, integrate with your logger
        print(f"Failed to send email: {exc}")