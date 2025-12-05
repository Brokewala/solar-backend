# realtime/routing.py
from django.urls import re_path
from .consumers import RelayStateConsumer

websocket_urlpatterns = [

    re_path(
        r"ws/relaystate/(?P<module_id>[-\w]+)/$",
        RelayStateConsumer.as_asgi(),
    ),
]
