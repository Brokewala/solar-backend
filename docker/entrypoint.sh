#!/bin/bash
set -e

# Determine port (default 8000) using Python so shell ${PORT} isn't required
export PORT=$(python - <<'PY'
import os
print(os.getenv("PORT", "8000"))
PY
)

# Wait briefly for Postgres if DATABASE_URL points to it
if [ -n "${DATABASE_URL:-}" ] && [[ "${DATABASE_URL}" == postgres* ]]; then
  python <<'PY'
import os, time
url = os.environ["DATABASE_URL"]
for _ in range(5):
    try:
        import psycopg
        with psycopg.connect(url, connect_timeout=2) as conn:
            conn.execute("SELECT 1")
        break
    except Exception:
        time.sleep(1)
PY
fi

python manage.py collectstatic --noinput || true
python manage.py migrate || true

exec "$@"
