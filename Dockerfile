# syntax=docker/dockerfile:1

##############################
# Builder image
FROM python:3.12-slim-bookworm AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive

ARG APT_FLAGS="--no-install-recommends"

# Dependence de build pour Pillow, psych, etc.
RUN apt-get update \
    && apt-get install -y $APT_FLAGS \
    build-essential \
    gcc \
    libjpeg62-turbo-dev \
    zlib1g-dev \
    libpng-dev \
    libtiff-dev \
    libfreetype6-dev \
    liblcms2-dev \
    libwebp-dev \
    libopenjp2-7-dev \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt ./

RUN python -m pip install --upgrade pip setuptools wheel \
    && pip install --prefix=/install -r requirements.txt

##############################
# Runtime image
FROM python:3.12-slim-bookworm AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    DEBIAN_FRONTEND=noninteractive \
    TZ=UTC \
    PORT=8000

ARG APT_FLAGS="--no-install-recommends"

RUN apt-get update \
    && apt-get install -y $APT_FLAGS \
    libjpeg62-turbo \
    zlib1g \
    libpng16-16 \
    libtiff6 \
    libfreetype6 \
    liblcms2-2 \
    libwebp7 \
    libopenjp2-7 \
    libpq5 \
    tzdata \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copier les packages Python préinstallés (depuis le builder)
COPY --from=builder /install /usr/local

# Utilisateur non-root
RUN useradd -m -u 10001 appuser
WORKDIR /app
USER appuser

# Copier le code de l'app
COPY --chown=appuser:appuser . /app

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS "http://localhost:${PORT}/health/" || exit 1

# Script d'initialisation : collecte des statiques et migrations
ENTRYPOINT ["bash", "docker/entrypoint.sh"]

# Lancement de Gunicorn (ASGI) avec gestion des variables d'environnement
CMD ["bash", "-c", "gunicorn solar_backend.asgi:application -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:${PORT} --workers ${WEB_CONCURRENCY:-2} --timeout ${WEB_TIMEOUT:-60} --graceful-timeout 30 --keep-alive 5"]
