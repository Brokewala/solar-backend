"""Utility functions for user-related tasks."""

from solar_backend.utils import Util


def send_reset_password_email(email, reset_link, request_id=None):
    """Send a password reset email synchronously."""
    subject = "Réinitialisation de mot de passe"
    html_body = (
        "Cliquez sur le lien pour réinitialiser votre mot de passe: "
        f"<a href='{reset_link}'>Réinitialiser</a>"
    )
    content = {
        "email_body": html_body,
        "to_email": email,
        "email_subject": subject,
    }
    Util.send_email(content)
