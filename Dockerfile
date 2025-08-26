# syntax=docker/dockerfile:1
# Multi-stage build for Django + Celery
# Build with: docker build -t solar-backend .
# - Web:   docker run --env-file .env -p 8000:8000 solar-backend
# - Worker: docker run --env-file .env solar-backend \
#             celery -A solar_backend worker --loglevel=INFO \
#             --concurrency=${CELERY_CONCURRENCY:-4} \
#             --prefetch-multiplier=${CELERY_PREFETCH_MULTIPLIER:-4} \
#             --max-tasks-per-child=100
# - Beat:   docker run --env-file .env solar-backend \
#             celery -A solar_backend beat --loglevel=INFO

FROM python:3.12-slim AS builder
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential libpq-dev && rm -rf /var/lib/apt/lists/*

COPY requirements.txt ./
RUN pip install --prefix=/install --no-cache-dir -r requirements.txt

FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev curl && rm -rf /var/lib/apt/lists/*

COPY --from=builder /install /usr/local
COPY . .

RUN useradd -m app && chown -R app /app
USER app

EXPOSE ${PORT}
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s CMD curl -f http://localhost:${PORT}/health/ || exit 1

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["gunicorn", "solar_backend.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "-w", "${WEB_CONCURRENCY:-2}", "-b", "0.0.0.0:${PORT}"]
