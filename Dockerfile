# syntax=docker/dockerfile:1

##############################
# Builder image
FROM python:3.12-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# build deps for Pillow, psycopg etc.
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff5-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# install Python deps into /install to leverage layer caching
COPY requirements.txt ./
RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --prefix=/install -r requirements.txt

##############################
# Runtime image
FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    libtiff5 \
    libfreetype6 \
    liblcms2-2 \
    libwebp7 \
    libopenjp2-7 \
    libpq5 \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# copy installed packages from builder
COPY --from=builder /install /usr/local

# non-root user
RUN useradd -m -u 10001 appuser
WORKDIR /app
USER appuser

COPY --chown=appuser:appuser . /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:${PORT:-8000}/health/ || exit 1

CMD ["sh", "-c", "gunicorn solar_backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}"]
# For WSGI replace the command with:
# CMD ["sh", "-c", "gunicorn solar_backend.wsgi:application --bind 0.0.0.0:${PORT:-8000} --workers ${WEB_CONCURRENCY:-2}"]
