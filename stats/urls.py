from django.urls import path
from stats.views import (
    BatteryWeeklyByMonthView,
    PanneauWeeklyByMonthView,
    PriseWeeklyByMonthView,
)
from stats.views import (
    BatteryDailyAPIView,
    PanneauDailyAPIView,
    PriseDailyAPIView,
)

urlpatterns = [
  path(
        'panneau/<str:module_id>/<int:year>/<int:month>/weekly',
        PanneauWeeklyByMonthView.as_view(),
        name='panneau-weekly-by-month',
    ),
    path(
        'battery/<str:module_id>/<int:year>/<int:month>/weekly',
        BatteryWeeklyByMonthView.as_view(),
        name='battery-weekly-by-month',
    ),
    path(
        'prise/<str:module_id>/<int:year>/<int:month>/weekly',
        PriseWeeklyByMonthView.as_view(),
        name='prise-weekly-by-month',
    ),
    
    #=============DAILY===========================
    path(
        "panneau/<str:module_id>/<int:year>/<int:month>/<int:day>/daily",
        PanneauDailyAPIView.as_view(),
        name="panneau-daily",
    ),
    path(
        "battery/<str:module_id>/<int:year>/<int:month>/<int:day>/daily",
        BatteryDailyAPIView.as_view(),
        name="battery-daily",
    ),
    path(
        "prise/<str:module_id>/<int:year>/<int:month>/<int:day>/daily",
        PriseDailyAPIView.as_view(),
        name="prise-daily",
    ),
]
