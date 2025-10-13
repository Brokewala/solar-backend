from django.urls import path

from . import views

urlpatterns = [
    path(
        "month-aggregate/<str:module_id>/<int:year>/<int:month>",
        views.month_aggregate_view,
        name="month-aggregate",
    ),
    path(
        "battery/<str:module_id>/<int:year>/<int:month>",
        views.get_battery_monthly_stats,
        name="battery-monthly-stats",
    ),
]
