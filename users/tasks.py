import logging
import smtplib

try:  # pragma: no cover - fallback if Celery not installed
    from celery import shared_task
except Exception:  # pragma: no cover
    def shared_task(*decorator_args, **decorator_kwargs):
        def wrapper(func):
            class DummyTask:
                def __init__(self, f):
                    self.f = f
                    self.request = type('req', (), {'retries': 0})()

                def delay(self, *args, **kwargs):
                    return self.f(self, *args, **kwargs)

                def retry(self, exc=None, countdown=0):
                    raise Exception("retry") from exc

                def __call__(self, *args, **kwargs):
                    return self.f(self, *args, **kwargs)

                def run(self, *args, **kwargs):
                    return self.f(self, *args, **kwargs)

            return DummyTask(func)
        return wrapper
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives

logger = logging.getLogger('mail.reset_password')


@shared_task(bind=True, max_retries=3)
def send_reset_password_email(self, user_id, reset_link, request_id=None):
    """Send password reset email asynchronously with retries."""
    User = get_user_model()
    user = User.objects.filter(id=user_id).first()
    extra = {'email': None, 'user_id': user_id, 'request_id': request_id}
    if not user:
        logger.warning('user_missing', extra=extra | {'status': 'user_missing'})
        return
    extra['email'] = user.email
    subject = "Réinitialisation de mot de passe"
    text_body = f"Utilisez ce lien pour réinitialiser votre mot de passe : {reset_link}"
    html_body = (
        "Cliquez sur le lien pour réinitialiser votre mot de passe: "
        f"<a href='{reset_link}'>Réinitialiser</a>"
    )
    try:
        msg = EmailMultiAlternatives(subject, text_body, to=[user.email])
        msg.attach_alternative(html_body, "text/html")
        msg.send(timeout=getattr(settings, 'EMAIL_TIMEOUT', 10))
        logger.info('sent', extra=extra | {'status': 'sent'})
    except smtplib.SMTPException as exc:
        logger.warning(
            'smtp_error', extra=extra | {'status': 'retry', 'err': str(exc)}
        )
        raise self.retry(exc=exc, countdown=2 ** self.request.retries)
    except Exception as exc:  # pragma: no cover
        logger.error(
            'unexpected_error', extra=extra | {'status': 'error', 'err': str(exc)}
        )
