from django.urls import path
from module import views


urlpatterns = [
    # module
    path("all", views.get_all_module),
    path("create-module", views.create_module_all),
    path("modules/<str:user_id>/user", views.get_one_module_by_user),
    path("modules/<str:user_id>/user-iot/", views.get_one_module_by_user_for_IOT),
    path("modules/<str:reference>/reference", views.get_module_by_reference),
    path("modules", views.ModulesAPIView.as_view()),
    path("modules/<str:module_id>", views.ModulesAPIView.as_view()),
    # nouvelles APIs pour Hotspot
    path("modules/<str:module_id>/toggle-active", views.toggle_module_active),
    path("modules/<str:module_id>/with-elements", views.get_module_with_elements),
    # module info
    path("module-info", views.ModulesInfoAPIView.as_view()),
    path("module-info/<str:module_id>", views.ModulesInfoAPIView.as_view()),
    path("module-info/<str:module_id>/module", views.get_one_moduleinfo_by_module),
    # refresh et token
     path("token/", views.IoTModuleTokenView.as_view(), name="iot_module_token"),
    path("token-refresh/", views.IoTTokenRefreshView.as_view(), name="iot_token_refresh"),
]
