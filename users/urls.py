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
    path("test", views.teste_email),
    path("decodeToken", views.decode_token),
    path("refresh", views.CustomTokenRefreshView.as_view()),
    path("login", views.CustomTokenObtainPairView.as_view()),
    path("info", views.user_by_token, name="user_by_token"),
    path("customers", views.get_all_customers),
    # # Admin
    path("signup-admin", views.create_admin_of_user),
    path("admin-all", views.get_all_admin),
    # user
    path("signup/", views.UsersAPIView.as_view()),
    # signup-code
    path("signup-with-code", views.signup_user_with_code_in_email),
    path("signup/<str:user_id>", views.get_user_code_with_user_id),
    path("signup-verify-code", views.verify_code_of_user),
    path("signup-resend-code", views.resend_code_of_signup),
    # profile update
    path("update-profile", views.update_user_profile),
    # password reset
    path("request-reset-password", views.RequestResetPasswordView.as_view(), name="request_reset_password"),
    path("reset-password/<str:uidb64>/<str:token>", views.reset_password, name="reset_password"),

]
