from django.core.mail import EmailMessage
from anymail.backends.brevo import EmailBackend as BrevoBackend


# ==================Auto send email======================
class Util:
    @staticmethod
    def send_email(data):
        email = EmailMessage(
            subject=data["email_subject"],
            body=data["email_body"],
            # from_email='Solar | Notification <no-reply@solarsmart.mg>',
            to=[data["to_email"]],
        )
        email.content_subtype = "html"
        # Force l'utilisation du backend HTTP de Brevo pour contourner le blocage réseau SMTP
        # email.connection = BrevoBackend()
        email.send()
