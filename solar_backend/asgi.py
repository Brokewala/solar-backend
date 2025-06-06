import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application


# url patterne
from notification.routing import websocket_urlpatterns as notifications_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'solar_backend.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": django_asgi_app,
        "websocket": AllowedHostsOriginValidator(
            AuthMiddlewareStack(
                URLRouter(
                    notifications_urlpatterns
                )
            )
        ),
    }
)