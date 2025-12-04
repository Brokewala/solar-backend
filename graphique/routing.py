# realtime/routing.py
from django.urls import re_path
from consumers import ModuleDataConsumer

websocket_urlpatterns = [

    # Données temps réel par module_id (Battery/Panneau/Prise du même module)
    re_path(
        r"ws/module/(?P<module_id>[-\w]+)/$",
        ModuleDataConsumer.as_asgi(),
    ),
]
