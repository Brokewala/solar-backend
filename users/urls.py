from django.urls import path, include
from rest_framework.routers import DefaultRouter
from users import views


# router
router = DefaultRouter()
# users
router.register(r"user", views.ProfilUserModelViewSet)


urlpatterns = [
    path("", include(router.urls)),
    # auth
    path("decodeToken", views.decode_token),
    path("refresh", views.CustomTokenRefreshView.as_view()),
    path("login", views.CustomTokenObtainPairView.as_view()),
    # # Admin
    path("signup-admin", views.create_admin_of_user),
    path("admin-all", views.get_all_admin),
    # user
    path("signup", views.UsersAPIView.as_view()),

]
