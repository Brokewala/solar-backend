# Endpoints de l'API Solar

Ce document répertorie tous les endpoints disponibles dans le projet **Solar Backend**.
Les chemins sont indiqués avec leurs préfixes complets.

## Routes racine
- `/swagger<format>/`
- `/swagger/`
- `/redoc/`
- `/admin/`
- `/health/`
- `/api/solar/users/`
- `/api/solar/modules/`
- `/api/solar/rating/`
- `/api/solar/battery/`
- `/api/solar/panneau/`
- `/api/solar/prise/`
- `/api/solar/report/`
- `/api/solar/subscription/`
- `/api/solar/notification/`

## Utilisateurs (`/api/solar/users/`)
- `user/` et `user/<id>/`
- `test/`
- `decodeToken/`
- `refresh/`
- `login/`
- `info/`
- `customers/`
- `signup-admin/`
- `admin-all/`
- `signup/`
- `signup-with-code/`
- `signup/<user_id>/`
- `signup-verify-code/`
- `signup-resend-code/`
- `update-profile/`
- `request-reset-password/`
- `reset-password/<uidb64>/<token>/`

## Modules (`/api/solar/modules/`)
- `all`
- `create-module`
- `modules/<user_id>/user`
- `modules/<reference>/reference`
- `modules`
- `modules/<module_id>`
- `modules/<module_id>/toggle-active`
- `modules/<module_id>/with-elements`
- `module-info`
- `module-info/<module_id>`
- `module-info/<module_id>/module`

## Notes (`/api/solar/rating/`)
- `all`
- `rating/<user_id>/user`
- `rating`
- `rating/<rating_id>`

## Batteries (`/api/solar/battery/`)
- `all`
- `battery/<module_id>/module`
- `battery/<module_id>/module-put`
- `battery`
- `battery/<battery_id>`
- `battery-data`
- `battery-data/<battery_data_id>`
- `battery-data/<battery_id>/battery`
- `battery-planning`
- `battery-planning/<battery_planning_id>`
- `battery-planning/<battery_id>/battery`
- `battery-planning/<module_id>/module`
- `battery-relaistate`
- `battery-relaistate/<battery_relai_id>`
- `battery-relaistate/<battery_id>/battery`
- `battery-relaistate/<battery_id>/switch`
- `battery-reference`
- `battery-reference/<battery_reference_id>`
- `battery-reference/<battery_id>/battery`
- `battery-duration/<module_id>/`
- `battery-colors/<module_id>/`
- `battery-data/<module_id>/<date>/`
- `battery-data-month/<module_id>/`
- `battery-data-week/<module_id>/`
- `battery-data-weekly/<module_id>/<year>/<month>/`
- `battery-data-daily/<module_id>/<week_number>/<day_of_week>/`
- `battery-data-detailed/<module_id>/<week_number>/<day_of_week>/`
- `battery-level/<module_id>/`
- `monthly-production/<module_id>/`
- `battery-relay-state/<module_id>/`
- `daily-data/<module_id>/`
- `daily-data/<module_id>/<week_number>/<day_of_week>/`
- `realtime-data/<module_id>/`
- `statistics/<module_id>/`

## Panneaux (`/api/solar/panneau/`)
- `all`
- `panneau/<module_id>/module`
- `panneau`
- `panneau/<panneau_id>`
- `panneau-data`
- `panneau-data/<panneau_data_id>`
- `panneau-data/<panneau_id>/panneau`
- `panneau-planning`
- `panneau-planning/<panneau_planning_id>`
- `panneau-planning/<panneau_id>/panneau`
- `panneau-planning/<module_id>/module`
- `panneau-relaistate`
- `panneau-relaistate/<panneau_relai_id>`
- `panneau-relaistate/<panneau_id>/panneau`
- `panneau-relaistate/<panneau_id>/switch`
- `panneau-reference`
- `panneau-reference/<panneau_reference_id>`
- `panneau-reference/<panneau_id>/panneau`
- `panneau-couleur-by-module/<module_id>/`
- `panneau-colors/<module_id>/`
- `production-annuelle/<module_id>/`
- `production-week/<module_id>/`
- `panneau-data-weekly/<module_id>/<year>/<month>/`
- `panneau-data-daily/<module_id>/<week_number>/<day_of_week>/`
- `panneau-relay-state/<module_id>/`
- `daily-data/<module_id>/`
- `daily-data/<module_id>/<week_number>/<day_of_week>/`
- `realtime-data/<module_id>/`
- `statistics/<module_id>/`

## Prises (`/api/solar/prise/`)
- `all`
- `prise/<module_id>/module`
- `prise`
- `prise/<prise_id>`
- `prise-data`
- `prise-data/<prise_data_id>`
- `prise-data/<prise_id>/prise`
- `prise-planning`
- `prise-planning/<prise_data_id>`
- `prise-planning/<prise_id>/prise`
- `prise-planning/<module_id>/module`
- `prise-relaistate`
- `prise-relaistate/<prise_relai_id>`
- `prise-relaistate/<prise_id>/prise`
- `prise-relaistate/<prise_id>/switch`
- `prise-reference`
- `prise-reference/<prise_reference_id>`
- `prise-reference/<prise_id>/prise`
- `couleur-prise/<module_id>/`
- `prise-colors/<module_id>/`
- `prise-relay-state/<module_id>/`
- `consommation-annuelle/<module_id>/`
- `prsie-data-week/<module_id>/`
- `prise-data-weekly/<module_id>/<year>/<month>/`
- `prise-data-daily/<module_id>/<week_number>/<day_of_week>/`
- `daily-data/<module_id>/`
- `daily-data/<module_id>/<week_number>/<day_of_week>/`
- `realtime-data/<module_id>/`
- `statistics/<module_id>/`

## Rapports (`/api/solar/report/`)
- `all`
- `report/<user_id>/user`
- `report/<report_id>`
- `report`
- `report-comment/<report_id>/report`
- `report-comment/<comment_id>`
- `report-comment`
- `report-state`
- `report-state/<state_id>`
- `report-state/<report_id>/report`

## Abonnements (`/api/solar/subscription/`)
- `all`
- `subscription/<user_id>/user`
- `subscription`
- `subscription/<sub_id>`
- `subscription-price/<sub_id>/subscription`
- `subscription-price`
- `subscription-price/<sub_id>`

## Notifications (`/api/solar/notification/`)
- `read/<id_notif>/`
- `all/<user_id>/`
- `delete/<user_id>/`
- `delete-notif/<id_notif>/`
- `read-all/<user_id>/`

