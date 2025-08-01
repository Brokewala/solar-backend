# Plateforme Solaire – Backend

## 🌞 Présentation

Ce projet est le backend d’une plateforme de gestion et de suivi de systèmes solaires connectés. Il permet la gestion des utilisateurs, des modules solaires, des batteries, des panneaux, des prises, des rapports, des notifications, des abonnements, et bien plus.

**Technologies principales :**
- Python 3.10
- Django 4.2
- Django REST Framework
- JWT (authentification)
- Channels (WebSocket)
- PostgreSQL (recommandé)
- Docker (optionnel)

---

## ⚙️ Installation locale

1. **Cloner le dépôt**
   ```bash
   git clone <url_du_repo>
   cd solar_backend
   ```

2. **Créer un environnement virtuel**
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configurer les variables d’environnement**  
   Crée un fichier `.env` à la racine du projet (voir section suivante).

5. **Appliquer les migrations**
   ```bash
   python manage.py migrate
   ```

6. **Lancer le serveur**
   ```bash
   python manage.py runserver
   ```

---

## 🔐 Variables d’environnement

Le projet utilise `python-dotenv` pour charger les variables d’environnement.  
Exemple de fichier `.env` à placer à la racine :

```
SECRET_KEY=ta_cle_secrete_django
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
DATABASE_URL=postgres://user:password@localhost:5432/solar_db
```

**NB :**  
- Le fichier `settings.py` charge automatiquement `.env`.
- Pour la production, adapte les variables sensibles et la configuration de la base de données.

---

## 🧪 Lancer les tests

Le projet contient un script de test personnalisé (`test_api.py`) pour tester la base, l’authentification et les endpoints principaux.

```bash
python test_api.py
```

---

# 🔁 Documentation complète de l’API

**Préfixe commun :** `/api/solar/`

## Utilisateurs (`/api/solar/users/`)

| Méthode | URL | Auth | Description | Paramètres | Exemple de réponse |
|---------|-----|------|-------------|------------|--------------------|
| GET     | user/ | JWT | Liste/CRUD utilisateurs | - | `[ {...} ]` |
| POST    | login | - | Authentification | `email`, `password` (body) | `{ "access": "...", "refresh": "...", ... }` |
| POST    | signup | - | Inscription | `email`, `password`, ... (body) | `{ ... }` |
| POST    | refresh | - | Refresh JWT | `refresh` (body) | `{ "access": "...", ... }` |
| POST    | decodeToken | - | Décoder un token | `token` (body) | `{ "token_type": "...", "user_id": ... }` |
| POST    | info | JWT | Infos utilisateur par token | `token` (body) | `{ ... }` |
| GET     | customers | JWT | Liste des clients | - | `[ {...} ]` |
| POST    | signup-with-code | - | Inscription avec code | `email`, ... (body) | `{ ... }` |
| GET     | signup/<user_id> | - | Récupérer code d’inscription | - | `{ ... }` |
| POST    | signup-verify-code | - | Vérifier code d’inscription | `email`, `code` (body) | `{ ... }` |
| POST    | signup-resend-code | - | Renvoyer code d’inscription | `email` (body) | `{ ... }` |
| PUT     | update-profile | JWT | Modifier le profil | champs à modifier (body) | `{ ... }` |

## Modules (`/api/solar/modules/`)

| Méthode | URL | Auth | Description | Paramètres | Exemple de réponse |
|---------|-----|------|-------------|------------|--------------------|
| GET     | all | JWT | Liste tous les modules | - | `[ {...} ]` |
| POST    | create-module | JWT | Crée un module avec éléments | `identifiant`, `password`, `user_id`, ... (body) | `{ ... }` |
| GET     | modules/<user_id>/user | JWT | Modules d’un utilisateur | - | `[ {...} ]` |
| GET     | modules/<reference>/reference | JWT | Module par référence | - | `{ ... }` |
| GET/POST/PUT/DELETE | modules, modules/<module_id> | JWT | CRUD module | selon méthode | `{ ... }` |
| PUT     | modules/<module_id>/toggle-active | JWT | Activer/désactiver module | - | `{ ... }` |
| GET     | modules/<module_id>/with-elements | JWT | Module avec éléments | - | `{ ... }` |
| GET     | module-info, module-info/<module_id> | JWT | Infos module | - | `{ ... }` |
| GET     | module-info/<module_id>/module | JWT | Infos module par module | - | `{ ... }` |

## Batteries (`/api/solar/battery/`)

Voir `battery/urls.py` pour la liste exhaustive. Exemples :

| Méthode | URL | Auth | Description | Paramètres | Exemple de réponse |
|---------|-----|------|-------------|------------|--------------------|
| GET     | all | JWT | Liste toutes les batteries | - | `[ {...} ]` |
| GET     | battery/<module_id>/module | JWT | Batterie d’un module | - | `{ ... }` |
| PUT     | battery/<module_id>/module-put | JWT | Modifier batterie d’un module | champs (body) | `{ ... }` |
| GET/POST/PUT/DELETE | battery, battery/<battery_id> | JWT | CRUD batterie | selon méthode | `{ ... }` |
| ...     | ... | ... | ... | ... | ... |

## Panneaux (`/api/solar/panneau/`)

Voir `panneau/urls.py` pour la liste exhaustive. Exemples :

| Méthode | URL | Auth | Description | Paramètres | Exemple de réponse |
|---------|-----|------|-------------|------------|--------------------|
| GET     | all | JWT | Liste tous les panneaux | - | `[ {...} ]` |
| GET     | panneau/<module_id>/module | JWT | Panneau d’un module | - | `{ ... }` |
| GET/POST/PUT/DELETE | panneau, panneau/<panneau_id> | JWT | CRUD panneau | selon méthode | `{ ... }` |
| ...     | ... | ... | ... | ... | ... |

## Prises (`/api/solar/prise/`)

Voir `prise/urls.py` pour la liste exhaustive. Exemples :

| Méthode | URL | Auth | Description | Paramètres | Exemple de réponse |
|---------|-----|------|-------------|------------|--------------------|
| GET     | all | JWT | Liste toutes les prises | - | `[ {...} ]` |
| GET     | prise/<module_id>/module | JWT | Prise d’un module | - | `{ ... }` |
| GET/POST/PUT/DELETE | prise, prise/<prise_id> | JWT | CRUD prise | selon méthode | `{ ... }` |
| ...     | ... | ... | ... | ... | ... |

## Ratings, Reports, Subscriptions, Notifications

- `/api/solar/rating/` : gestion des notations
- `/api/solar/report/` : gestion des rapports et commentaires
- `/api/solar/subscription/` : gestion des abonnements et prix
- `/api/solar/notification/` : gestion des notifications utilisateurs

Consulte chaque fichier `urls.py` pour la liste complète des endpoints, paramètres et méthodes.

---

## 🔒 Authentification

- La majorité des endpoints nécessitent un token JWT (`Authorization: Bearer <token>`).
- Utilise `/api/solar/users/login` pour obtenir un token.

---

## 📚 Exemples de requêtes

**Authentification :**
```http
POST /api/solar/users/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "motdepasse"
}
```
**Réponse :**
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "user_id": 1,
  "email": "user@example.com",
  ...
}
```

---

## 🗂 Structure du projet

- `solar_backend/` : configuration principale Django
- `users/`, `module/`, `battery/`, `panneau/`, `prise/`, `rating/`, `report/`, `subscription/`, `notification/` : apps métier
- `requirements.txt` : dépendances Python
- `Dockerfile` : conteneurisation
- `test_api.py` : script de tests

---

## 📝 Notes

- Pour la liste exhaustive des routes, consulte chaque fichier `urls.py` dans les apps concernées.
- Les endpoints sont majoritairement RESTful, certains utilisent des ViewSets ou des APIView.
- Les permissions sont gérées via JWT, certains endpoints sont publics (ex : login, signup).

---

**Pour toute question, contacte l’équipe technique.** 