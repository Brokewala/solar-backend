# Deployment Notes

## Key environment variables
Defaults are hard-coded so the app boots on Railway even without a `.env` file.

| Variable | Default |
|----------|---------|
| `PORT` | 8000 (Railway overrides) |
| `WEB_CONCURRENCY` | 2 |
| `WEB_TIMEOUT` | 60 |
| `DATABASE_URL` | fallback SQLite at `/app/db.sqlite3` (Postgres required in prod) |
| `TZ` | `Indian/Antananarivo` (configure in Railway Variables) |

## Run command
```
gunicorn solar_backend.asgi:application \
  -k uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:${PORT} \
  --workers ${WEB_CONCURRENCY:-2} \
  --timeout ${WEB_TIMEOUT:-60} \
  --graceful-timeout 30 \
  --keep-alive 5
```

## Local health check
Start the container and run:
```
curl -fsS http://localhost:${PORT}/health/
```
