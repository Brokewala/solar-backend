# realtime/routing.py
from django.urls import re_path
from .consumers import ModuleDataConsumer

websocket_urlpatterns = [

    re_path(
        r"ws/module/(?P<module_id>[-\w]+)/$",
        ModuleDataConsumer.as_asgi(),
    ),
]
