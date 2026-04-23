# Analyse d'Architecture Backend - Projet Solaire

Ce document présente une évaluation technique approfondie de l'architecture du backend pour le système de gestion solaire.

## 1. Stack Technique
*   **Langage/Framework :** Python 3.13 / Django 4.2.4 avec **Django Rest Framework (DRF)**.
*   **Temps Réel :** **Django Channels 4.0** (WebSockets) via protocole ASGI (**Daphne**).
*   **Base de Données :** **PostgreSQL** (Production) / SQLite (Développement).
*   **API Documentation :** **Swagger/OpenAPI** (drf-yasg).
*   **Authentification :** **JWT** (djangorestframework-simplejwt).

## 2. Structure des Fichiers (Arborescence)
Le projet adopte une structure modulaire par "Apps" Django :
```text
solar-backend/
├── solar_backend/          # Configuration globale
├── users/                  # Utilisateurs & Auth
├── module/                 # Concentrateur (Inverter)
├── battery/                # Batteries & Métriques
├── panneau/                # Panneaux & Production
├── prise/                  # Prises & Consommation
├── graphique/              # Temps Réel (Signals)
├── stats/                  # Analytics
├── notification/           # Alertes
└── docker/                 # Déploiement
```

## 3. Schéma de Données (Modèles)
*   **User :** ProfilUser (email, role, verification).
*   **Module :** Centralise les composants.
*   **Données :** BatteryData, PanneauData, PriseData pour l'historique des métriques.

## 4. Flux de Données & API
*   **Ingestion :** POST HTTP des équipements vers le backend.
*   **Diffusion :** WebSockets via Django Channels pour la mise à jour des graphiques en direct.

## 5. Points d'Attention (Analyse)
1.  **Scalabilité :** Remplacer `InMemoryChannelLayer` par **Redis**.
2.  **Performance :** Utiliser **TimescaleDB** pour la gestion massive des séries temporelles.
3.  **Sécurité :** Sécuriser les endpoints hardware avec des clés d'API.

---
*Document généré par Antigravity.*
