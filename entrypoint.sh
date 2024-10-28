#!/bin/bash
set -e

# Appliquer les migrations
echo "Appliquer les migrations..."
python manage.py makemigrations
python manage.py migrate

# Démarrer le serveur Django
echo "Démarrer le serveur Django..."
exec "$@"
