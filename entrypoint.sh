#!/bin/bash
set -euo pipefail

python manage.py collectstatic --noinput

if [ "${RUN_MIGRATIONS:-0}" = "1" ]; then
  python manage.py migrate --noinput
fi

exec "$@"
