from django.urls import path

from . import views

urlpatterns = [
    path(
        "month-aggregate/<str:module_id>/<int:year>/<int:month>",
        views.month_aggregate_view,
        name="month-aggregate",
    ),
    path(
        "panneau/<str:module_id>/<int:year>/<int:month>",
        views.get_panneau_monthly_stats,
        name="panneau-monthly-stats",
    ),
    path(
        "battery/<str:module_id>/<int:year>/<int:month>",
        views.get_battery_monthly_stats,
        name="battery-monthly-stats",
    ),
    path(
        "prise/<str:module_id>/<int:year>/<int:month>",
        views.get_prise_monthly_stats,
        name="prise-monthly-stats",
    ),
]
