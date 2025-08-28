#!/bin/sh
set -e

# Run Django management tasks without blocking startup
python manage.py collectstatic --noinput || true &
python manage.py migrate || true &

exec "$@"
