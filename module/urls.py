from django.urls import path
from module import views


urlpatterns = [
    # module
    path("all", views.get_all_module),
    path("create-module", views.create_module_all),
    path("modules/<str:user_id>/user", views.get_one_module_by_user),
    path("modules", views.ModulesAPIView.as_view()),
    path("modules/<str:module_id>", views.ModulesAPIView.as_view()),
    # module info
    path("module-info", views.ModulesInfoAPIView.as_view()),
    path("module-info/<str:module_id>", views.ModulesInfoAPIView.as_view()),
    path("module-info/<str:module_id>/module", views.get_one_moduleinfo_by_module),
]
