# Deployment Notes

## Required environment variables
- `DJANGO_SETTINGS_MODULE=solar_backend.settings`
- `SECRET_KEY` (set a strong value)
- `DEBUG=false`
- `TIME_ZONE=Indian/Antananarivo`
- `ALLOWED_HOSTS=.up.railway.app,solar-backend-production-12aa.up.railway.app,localhost,127.0.0.1`
- `CSRF_TRUSTED_ORIGINS=https://solar-backend-production-12aa.up.railway.app`
- `DATABASE_URL=postgresql://user:password@host:5432/dbname?sslmode=require`

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
