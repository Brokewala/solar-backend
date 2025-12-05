from django.urls import path
from rating import views


urlpatterns = [
    # rating
    path("all", views.get_all_rating),
    path("rating/<str:user_id>/user", views.get_one_rating_by_user),
    path("rating", views.RatingAPIView.as_view()),
    path("rating/<str:rating_id>", views.RatingAPIView.as_view()),
]
