from django.urls import path
from panneau import views


urlpatterns = [
    # panneau
    path("all", views.get_all_panneau),
    path("panneau/<str:module_id>/module", views.get_one_panneau_by_module),
    path("panneau", views.PanneauAPIView.as_view()),
    path("panneau/<str:panneau_id>", views.PanneauAPIView.as_view()),
    # PanneauData
    path("panneau-data", views.PanneauDataAPIView.as_view()),
    path("panneau-data/<str:panneau_data_id>", views.PanneauDataAPIView.as_view()),
    path("panneau-data/<str:panneau_id>/panneau", views.get_one_PanneauData_by_panneau),
    # PanneauPlanning
    path("panneau-planning", views.PanneauPlanningPIView.as_view()),
    path(
        "panneau-planning/<str:panneau_planning_id>",
        views.PanneauPlanningPIView.as_view(),
    ),
    path(
        "panneau-planning/<str:panneau_id>/panneau",
        views.get_one_PanneauPlanning_by_panneau,
    ),
    path(
        "panneau-planning/<str:module_id>/module",
        views.get_PanneauPlanning_by_module,
    ),
    # PanneauRelaiState
    path("panneau-relaistate", views.PanneauRelaiStateAPIView.as_view()),
    path(
        "panneau-relaistate/<str:panneau_relai_id>",
        views.PanneauRelaiStateAPIView.as_view(),
    ),
    path(
        "panneau-relaistate/<str:panneau_id>/panneau",
        views.get_one_PanneauRelaiState_by_panneau,
    ),
    path(
        "panneau-relaistate/<str:panneau_id>/switch",
        views.switch_panneauRelaiState_by_panneau,
    ),
     path('relai-state/<str:panneau_id>/iot/', views.PanneauRelaiStateAPIViewIOT.as_view(), name='panneau-relai-state'),

    # PanneauReference
    path("panneau-reference", views.PanneauReferenceAPIView.as_view()),
    path(
        "panneau-reference/<str:panneau_reference_id>",
        views.PanneauReferenceAPIView.as_view(),
    ),
    path(
        "panneau-reference/<str:panneau_id>/panneau",
        views.get_one_PanneauReference_by_panneau,
    ),
    # =====================panneau=====================
    path(
        "panneau-couleur-by-module/<str:module_id>/",
        views.couleur_by_module,
        name="couleur-by-module",
    ),
    path(
        "panneau-colors/<str:module_id>/",
        views.couleur_by_module,
        name="panneau-colors",
    ),  # Alias pour compatibilité frontend
    # path(
    #     "production-annuelle/<str:module_id>/",
    #     views.get_production_panneau_annuelle,
    #     name="production-annuelle",
    # ),
     path(
        "production-annuelle/<str:module_id>/",
        views.get_panneau_annual_breakdown,
        name="production-annuelle",
    ),
    path(
        "production-week/<str:module_id>/",
        views.get_panel_consumption_by_week,
        name="production-semaine",
    ),
    path(
        "panneau-data-weekly/<str:module_id>/<str:year>/<str:month>/",
        views.get_weekly_panneau_data_for_month,
    ),
    path(
        "panneau-data-daily/<str:module_id>/<str:week_number>/<str:day_of_week>/",
        views.get_daily_panneau_data_for_week,
    ),
    # API pour récupérer l'état du relais par module
    path(
        "panneau-relay-state/<str:module_id>/",
        views.get_panneau_relay_state_by_module,
        name="get_panneau_relay_state_by_module",
    ),
    #=============================== graphique===================================
    path(
        "daily-data/<str:module_id>/",
        views.get_daily_panneau_data,
        name="daily_panneau_data",
    ),
    path(
        "daily-data/<str:module_id>/<int:week_number>/<str:day_of_week>/",
        views.get_daily_panneau_data,
        name="daily_panneau_data_specific",
    ),
    # celui qui fonctionne
    path(
        "daily-data-filter/<str:module_id>/",
        views.get_panneau_data_filtered,
        name="daily_panneau_data_specific",
    ),
    path(
        "realtime-data/<str:module_id>/",
        views.get_realtime_panneau_data,
        name="realtime_panneau_data",
    ),
    path(
        "statistics/<str:module_id>/",
        views.get_panneau_statistics,
        name="panneau_statistics",
    ),
]
