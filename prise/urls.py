from django.urls import path
from prise import views


urlpatterns = [
    # prise
    path("all", views.get_all_Prise),
    path("prise/<str:module_id>/module", views.get_one_Prise_by_module),
    path("prise", views.PriseAPIView.as_view()),
    path("prise/<str:prise_id>", views.PriseAPIView.as_view()),
    # PriseAPIView
    path("prise-data", views.PriseDataAPIView.as_view()),
    path("prise-data/<str:prise_data_id>", views.PriseDataAPIView.as_view()),
    path("prise-data/<str:prise_id>/prise", views.get_one_PriseData_by_prise),
    # PrisePlanningPIView
    path("prise-planning", views.PrisePlanningPIView.as_view()),
    path("prise-planning/<str:prise_data_id>", views.PrisePlanningPIView.as_view()),
    path(
        "prise-planning/<str:prise_id>/prise",
        views.get_one_PrisePlanning_by_Prise,
    ),
    path(
        "prise-planning/<str:module_id>/module",
        views.get_PrisePlanning_by_module,
    ),
    # priseRelaiState
    path("prise-relaistate", views.PriseRelaiStateAPIView.as_view()),
    path(
        "prise-relaistate/<str:prise_relai_id>",
        views.PriseRelaiStateAPIView.as_view(),
    ),
    path(
        "prise-relaistate/<str:prise_id>/prise",
        views.get_one_PriseRelaiState_by_Prise,
    ),
    path(
        "prise-relaistate/<str:prise_id>/switch",
        views.switch_PriseRelaiState_by_Prise,
    ),
    # priseReference
    path("prise-reference", views.PriseReferenceAPIView.as_view()),
    path(
        "prise-reference/<str:prise_reference_id>",
        views.PriseReferenceAPIView.as_view(),
    ),
    path(
        "prise-reference/<str:prise_id>/prise",
        views.get_one_PriseReference_by_prise,
    ),
    # ================mobile==========================
    path(
        "couleur-prise/<str:module_id>/",
        views.get_couleur_prise_by_id_module,
        name="couleur-prise-by-module",
    ),
    path(
        "prise-colors/<str:module_id>/",
        views.get_couleur_prise_by_id_module,
        name="prise-colors",  # Alias pour compatibilité frontend
    ),
    # API pour récupérer l'état du relais par module
    path(
        "prise-relay-state/<str:module_id>/",
        views.get_prise_relay_state_by_module,
        name="get_prise_relay_state_by_module",
    ),
    path(
        "consommation-annuelle/<str:module_id>/",
        views.get_consommation_prise_annuelle,
        name="consommation-annuelle",
    ),
    path('prsie-data-week/<str:module_id>/', views.get_socket_consumption_by_week),
    path('prise-data-weekly/<str:module_id>/<str:year>/<str:month>/', views.get_weekly_prise_data_for_month),
    path('prise-data-daily/<str:module_id>/<str:week_number>/<str:day_of_week>/', views.get_daily_prise_data_for_week),

]
