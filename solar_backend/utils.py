from django.core.mail import EmailMessage

# from django.core import mail


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
        email.send()