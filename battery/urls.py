from django.urls import path
from battery import views


urlpatterns = [
    # battery
    path("all", views.get_all_battery),
    path("battery/<str:module_id>/module", views.get_one_battery_by_module),
    path("battery/<str:module_id>/module-put", views.put_battery_by_module),
    path("battery", views.BatteryAPIView.as_view()),
    path("battery/<str:battery_id>", views.BatteryAPIView.as_view()),
    # battery data
    path("battery-data", views.BatteryDataAPIView.as_view()),
    path("battery-data/<str:battery_data_id>", views.BatteryDataAPIView.as_view()),
    path("battery-data/<str:battery_id>/battery", views.get_one_batterydata_by_battery),
    # battery planning
    path("battery-planning", views.BatteryPlanningPIView.as_view()),
    path(
        "battery-planning/<str:battery_planning_id>", views.BatteryPlanningPIView.as_view()
    ),
    path(
        "battery-planning/<str:battery_id>/battery",
        views.get_batteryplanning_by_battery,
    ),
     path(
        "battery-planning/<str:module_id>/module",
        views.get_BatteryPlanning_by_module,
    ),
    # relai state
    path("battery-relaistate", views.BatteryRelaiStateAPIView.as_view()),
    path(
        "battery-relaistate/<str:battery_relai_id>",
        views.BatteryRelaiStateAPIView.as_view(),
    ),
    path(
        "battery-relaistate/<str:battery_id>/battery",
        views.get_one_batteryrelaistate_by_battery,
    ),
    path(
        "battery-relaistate/<str:battery_id>/switch",
        views.switch_batteryRelaiState_by_battery,
    ),
    path('relai-state/<str:battery_id>/iot/', views.BatteryRelaiStateByBatteryAPIView.as_view(), name='battery-relai-state'),

    # referance
    path("battery-reference", views.BatteryReferenceAPIView.as_view()),
    path(
        "battery-reference/<str:battery_reference_id>",
        views.BatteryReferenceAPIView.as_view(),
    ),
    path(
        "battery-reference/<str:battery_id>/battery",
        views.get_one_batteryreference_by_battery,
    ),
    # api data for battery=======================
    path(
        "battery-duration/<str:module_id>/",
        views.yearly_battery_utilisation,
        name="get_duree_utilisation_batterie_annuelle_by_id_module",
    ),
    path(
        "battery-colors/<str:module_id>/",
        views.get_couleur_batterie_by_id_module,
        name="get_couleur_batterie_by_id_module",
    ),
    path(
        "battery-data/<str:module_id>/<str:date>/",
        views.liste_batterie_data_by_date_and_id_module,
        name="liste_batterie_data_by_date_and_id_module",
    ),
    # listeDureeBatterieMensuelleByIdModuleAndMonth
    #  path(
    #     "battery-data-month/<str:module_id>/",
    #     views.liste_duree_batterie_mensuelle_by_id_module_and_month,
    #     name="liste_duree_batterie_mensuelle_by_id_module_and_month",
    # ),
      path(
        "<str:module_id>/battery-data-month",
        views.get_battery_annual_breakdown,
        name="get_battery_annual_breakdown",
    ),
    path('battery-data-week/<str:module_id>/', views.get_battery_consumption_by_week),
    path('battery-data-weekly/<str:module_id>/<str:year>/<str:month>/', views.get_weekly_battery_data_for_month),
    path('battery-data-daily/<str:module_id>/<str:week_number>/<str:day_of_week>/', views.get_daily_battery_data_for_week),
    path('battery-data-detailed/<str:module_id>/<str:week_number>/<str:day_of_week>/', views.get_detailed_battery_data_for_week),
    # Nouvelles APIs pour niveau de batterie et production mensuelle
    path('battery-level/<str:module_id>/', views.get_current_battery_level, name='get_current_battery_level'),
    path('monthly-production/<str:module_id>/', views.get_monthly_production_summary, name='get_monthly_production_summary'),
    # API pour récupérer l'état du relais par module
    path('battery-relay-state/<str:module_id>/', views.get_battery_relay_state_by_module, name='get_battery_relay_state_by_module'),
    #=============================== graphique===================================
    path('daily-data/<str:module_id>/', views.get_daily_battery_data, name='daily_battery_data'),
    path('daily-data/<str:module_id>/<int:week_number>/<str:day_of_week>/', 
         views.get_daily_battery_data, name='daily_battery_data_specific'),
    path('realtime-data/<str:module_id>/', views.get_realtime_battery_data, name='realtime_battery_data'),
    path('statistics/<str:module_id>/', views.get_battery_statistics, name='battery_statistics'),
]
