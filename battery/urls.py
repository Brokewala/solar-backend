from django.urls import path
from battery import views


urlpatterns = [
    # battery
    path("all", views.get_all_battery),
    path("battery/<str:module_id>/module", views.get_one_battery_by_module),
    path("battery", views.BatteryAPIView.as_view()),
    path("battery/<str:battery_id>", views.BatteryAPIView.as_view()),
    # battery data
    path("battery-data", views.BatteryDataAPIView.as_view()),
    path("battery-data/<str:battery_data_id>", views.BatteryDataAPIView.as_view()),
    path("battery-data/<str:battery_id>/battery", views.get_one_batterydata_by_battery),
    # battery planning
    path("battery-planning", views.BatteryPlanningPIView.as_view()),
    path(
        "battery-planning/<str:battery_data_id>", views.BatteryPlanningPIView.as_view()
    ),
    path(
        "battery-planning/<str:battery_id>/battery",
        views.get_one_batteryplanning_by_battery,
    ),
]
