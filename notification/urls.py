from django.urls import path
from notification import views

urlpatterns = [
    path("read/<str:id_notif>/", views.read_notification),
    path("all/<str:user_id>/", views.get_all_by_user_notification),
    path("delete/<str:user_id>/", views.delete_all_by_user_notification),
]
