from django.urls import path
from stats.views import (
    BatteryWeeklyByMonthView,
    PanneauWeeklyByMonthView,
    PriseWeeklyByMonthView,
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
]
