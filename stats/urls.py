from django.urls import path
from stats.views import (
    BatteryWeeklyByMonthView,
    PanneauWeeklyByMonthView,
    PriseWeeklyByMonthView,
)

urlpatterns = [
  path(
        'api/panneau/<str:module_id>/<int:year>/<int:month>/weekly',
        PanneauWeeklyByMonthView.as_view(),
        name='panneau-weekly-by-month',
    ),
    path(
        'api/battery/<str:module_id>/<int:year>/<int:month>/weekly',
        BatteryWeeklyByMonthView.as_view(),
        name='battery-weekly-by-month',
    ),
    path(
        'api/prise/<str:module_id>/<int:year>/<int:month>/weekly',
        PriseWeeklyByMonthView.as_view(),
        name='prise-weekly-by-month',
    ),
]
