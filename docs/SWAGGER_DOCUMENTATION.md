# Documentation API Solar - Swagger

## Vue d'ensemble

L'API Solar est une API REST complète pour la gestion d'une plateforme solaire. Elle permet de gérer les batteries, panneaux solaires, prises électriques, planifications et notifications pour un système de production d'énergie solaire.

## Accès à la documentation Swagger

### Interface Swagger UI
- **URL**: `http://localhost:8000/swagger/`
- **Description**: Interface interactive pour tester et explorer l'API

### Interface ReDoc
- **URL**: `http://localhost:8000/redoc/`
- **Description**: Documentation alternative avec une présentation plus structurée

### Schéma JSON
- **URL**: `http://localhost:8000/swagger.json`
- **Description**: Schéma OpenAPI au format JSON

## Structure de l'API

### Applications principales

#### 1. **Battery** - Gestion des batteries
- **Base URL**: `/api/solar/battery/`
- **Endpoints**:
  - `GET /all` - Récupère toutes les batteries
  - `GET /battery/{module_id}/module` - Récupère une batterie par module
  - `PUT /battery/{module_id}/module-put` - Met à jour une batterie
  - `POST /battery` - Crée une nouvelle batterie
  - `GET /battery/{battery_id}` - Récupère une batterie par ID
  - `PUT /battery/{battery_id}` - Met à jour une batterie
  - `DELETE /battery/{battery_id}` - Supprime une batterie

#### 2. **Panneau** - Gestion des panneaux solaires
- **Base URL**: `/api/solar/panneau/`
- **Endpoints**:
  - `GET /all` - Récupère tous les panneaux
  - `GET /panneau/{module_id}/module` - Récupère un panneau par module
  - `POST /panneau` - Crée un nouveau panneau
  - `GET /panneau/{panneau_id}` - Récupère un panneau par ID
  - `PUT /panneau/{panneau_id}` - Met à jour un panneau
  - `DELETE /panneau/{panneau_id}` - Supprime un panneau

#### 3. **Prise** - Gestion des prises électriques
- **Base URL**: `/api/solar/prise/`
- **Endpoints**:
  - `GET /all` - Récupère toutes les prises
  - `GET /prise/{module_id}/module` - Récupère une prise par module
  - `POST /prise` - Crée une nouvelle prise
  - `GET /prise/{prise_id}` - Récupère une prise par ID
  - `PUT /prise/{prise_id}` - Met à jour une prise
  - `DELETE /prise/{prise_id}` - Supprime une prise

#### 4. **Module** - Gestion des modules
- **Base URL**: `/api/solar/modules/`
- **Endpoints**:
  - `GET /all` - Récupère tous les modules
  - `POST /module` - Crée un nouveau module
  - `GET /module/{module_id}` - Récupère un module par ID
  - `PUT /module/{module_id}` - Met à jour un module
  - `DELETE /module/{module_id}` - Supprime un module

#### 5. **Users** - Gestion des utilisateurs
- **Base URL**: `/api/solar/users/`
- **Endpoints**:
  - `POST /register` - Inscription d'un nouvel utilisateur
  - `POST /login` - Connexion utilisateur
  - `GET /profile` - Récupère le profil utilisateur
  - `PUT /profile` - Met à jour le profil utilisateur

## Authentification

L'API utilise l'authentification JWT (JSON Web Tokens).

### Obtenir un token d'accès

```bash
POST /api/solar/users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "password123"
}
```

### Utiliser le token

```bash
Authorization: Bearer <access_token>
```

## Modèles de données

### Battery
```json
{
  "id": "uuid",
  "module": "module_id",
  "marque": "string",
  "puissance": "string",
  "voltage": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Panneau
```json
{
  "id": "uuid",
  "module": "module_id",
  "marque": "string",
  "puissance": "string",
  "voltage": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Prise
```json
{
  "id": "uuid",
  "module": "module_id",
  "name": "string",
  "voltage": "string",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

### Module
```json
{
  "id": "uuid",
  "user": "user_id",
  "reference": "string",
  "identifiant": "string",
  "password": "string",
  "active": "boolean",
  "createdAt": "datetime",
  "updatedAt": "datetime"
}
```

## Codes de réponse HTTP

- **200 OK** - Requête réussie
- **201 Created** - Ressource créée avec succès
- **204 No Content** - Requête réussie, pas de contenu à retourner
- **400 Bad Request** - Données de requête invalides
- **401 Unauthorized** - Authentification requise
- **404 Not Found** - Ressource non trouvée
- **500 Internal Server Error** - Erreur serveur

## Exemples d'utilisation

### Créer une nouvelle batterie

```bash
POST /api/solar/battery/battery
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "puissance": "1000W",
  "voltage": "12V",
  "module": "module-uuid",
  "marque": "Tesla"
}
```

### Récupérer les données d'une batterie

```bash
GET /api/solar/battery/battery-data/{battery_id}
Authorization: Bearer <access_token>
```

### Mettre à jour un panneau

```bash
PUT /api/solar/panneau/panneau/{panneau_id}
Content-Type: application/json
Authorization: Bearer <access_token>

{
  "puissance": "500W",
  "voltage": "24V",
  "marque": "SunPower"
}
```

## Endpoints de données et statistiques

### Données en temps réel
- `GET /api/solar/battery/realtime-data/{module_id}` - Données de batterie en temps réel
- `GET /api/solar/panneau/realtime-data/{module_id}` - Données de panneau en temps réel
- `GET /api/solar/prise/realtime-data/{module_id}` - Données de prise en temps réel

### Statistiques
- `GET /api/solar/battery/statistics/{module_id}` - Statistiques de batterie
- `GET /api/solar/panneau/statistics/{module_id}` - Statistiques de panneau
- `GET /api/solar/prise/statistics/{module_id}` - Statistiques de prise

### Données par période
- `GET /api/solar/battery/daily-data/{module_id}` - Données quotidiennes
- `GET /api/solar/battery/weekly-data/{module_id}` - Données hebdomadaires
- `GET /api/solar/battery/monthly-data/{module_id}` - Données mensuelles

## Planification et états

### Planification
- `GET /api/solar/battery/battery-planning/{module_id}/module` - Planning de batterie
- `GET /api/solar/panneau/panneau-planning/{module_id}/module` - Planning de panneau
- `GET /api/solar/prise/prise-planning/{module_id}/module` - Planning de prise

### États de relais
- `GET /api/solar/battery/battery-relay-state/{module_id}` - État du relais de batterie
- `GET /api/solar/panneau/panneau-relay-state/{module_id}` - État du relais de panneau
- `GET /api/solar/prise/prise-relay-state/{module_id}` - État du relais de prise

## Notifications

### Gestion des notifications
- `GET /api/solar/notification/notifications` - Récupère les notifications
- `POST /api/solar/notification/notifications` - Crée une notification
- `PUT /api/solar/notification/notifications/{id}` - Met à jour une notification
- `DELETE /api/solar/notification/notifications/{id}` - Supprime une notification

## Rapports

### Génération de rapports
- `GET /api/solar/report/reports` - Récupère les rapports
- `POST /api/solar/report/reports` - Génère un nouveau rapport
- `GET /api/solar/report/reports/{id}` - Récupère un rapport spécifique

## Abonnements

### Gestion des abonnements
- `GET /api/solar/subscription/subscriptions` - Récupère les abonnements
- `POST /api/solar/subscription/subscriptions` - Crée un abonnement
- `PUT /api/solar/subscription/subscriptions/{id}` - Met à jour un abonnement
- `DELETE /api/solar/subscription/subscriptions/{id}` - Supprime un abonnement

## Développement

### Installation et configuration

1. **Cloner le projet**
```bash
git clone <repository-url>
cd solar_backend
```

2. **Installer les dépendances**
```bash
pip install -r requirements.txt
```

3. **Configurer la base de données**
```bash
python manage.py migrate
```

4. **Créer un super utilisateur**
```bash
python manage.py createsuperuser
```

5. **Lancer le serveur**
```bash
python manage.py runserver
```

### Ajout de nouveaux endpoints

Pour ajouter de nouveaux endpoints avec documentation Swagger :

1. **Créer la vue avec le décorateur Swagger**
```python
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

@swagger_auto_schema(
    method='get',
    operation_description="Description de l'endpoint",
    responses={
        200: YourSerializer,
        404: openapi.Response('Ressource non trouvée'),
        500: 'Internal Server Error'
    }
)
@api_view(["GET"])
def your_view(request):
    # Votre logique ici
    pass
```

2. **Ajouter l'URL**
```python
# Dans urls.py
path('your-endpoint/', views.your_view, name='your_view'),
```

3. **Tester dans Swagger**
- Accéder à `http://localhost:8000/swagger/`
- Vérifier que l'endpoint apparaît dans la documentation
- Tester l'endpoint directement depuis l'interface

## Support

Pour toute question ou problème concernant l'API :

- **Email**: contact@solar-platform.com
- **Documentation**: Consultez l'interface Swagger à `/swagger/`
- **Issues**: Utilisez le système de tickets du projet

## Version

- **Version actuelle**: v1
- **Dernière mise à jour**: 2024
- **Statut**: Production 