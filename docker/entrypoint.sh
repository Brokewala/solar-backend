#!/bin/bash
set -euo pipefail

# optional startup delay to avoid race conditions
if [ -n "${APP_STARTUP_DELAY:-}" ]; then
  sleep "${APP_STARTUP_DELAY}"
fi

# Wait for database if DATABASE_URL is provided
if [ -n "${DATABASE_URL:-}" ]; then
  for i in 1 2 3 4 5; do
    if python <<'PY'
import os, sys, time
url = os.environ["DATABASE_URL"]
try:
    import psycopg
    with psycopg.connect(url, connect_timeout=5) as conn:
        conn.execute("SELECT 1")
    sys.exit(0)
except Exception:
    sys.exit(1)
PY
    then
      break
    fi
    echo "Waiting for database... ($i/5)"
    sleep 2
    if [ "$i" -eq 5 ]; then
      echo "Database unavailable" >&2
      exit 1
    fi
  done
fi

python manage.py migrate --noinput
python manage.py collectstatic --noinput

exec "$@"
