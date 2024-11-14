from django.urls import path
from subscription import views


urlpatterns = [
    # subscription
    path("all", views.get_all_Subscription),
    path("subscription/<str:user_id>/user", views.get_one_subscription_by_user),
    path("subscription", views.SubscriptionAPIView.as_view()),
    path("subscription/<str:sub_id>", views.SubscriptionAPIView.as_view()),
    # SubscriptionPrice
    path("subscription-price/<str:sub_id>/subscription", views.get_one_SubscriptionPrice_by_subscription),
    path("subscription-price", views.SubscriptionAPIView.as_view()),
    path("subscription-price/<str:sub_id>", views.SubscriptionAPIView.as_view()),

]
