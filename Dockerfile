# ---------- STAGE 1: builder ----------
    FROM python:3.12-slim AS builder

    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1
    
    # Paquets nécessaires pour compiler Pillow & autres deps natives
    RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        gcc \
        libjpeg62-turbo-dev \
        zlib1g-dev \
        libpng-dev \
        libopenjp2-7-dev \
        libtiff5-dev \
        libfreetype6-dev \
        liblcms2-dev \
        libwebp-dev \
        && rm -rf /var/lib/apt/lists/*
    
    WORKDIR /app
    
    # Optimise le cache pip
    COPY requirements.txt ./
    
    # Mets à jour pip/setuptools/wheel puis installe les deps dans /install
    RUN python -m pip install --upgrade pip setuptools wheel \
     && pip install --prefix=/install --no-cache-dir -r requirements.txt
    
    # ---------- STAGE 2: runtime ----------
    FROM python:3.12-slim AS runtime
    
    ENV PYTHONDONTWRITEBYTECODE=1 \
        PYTHONUNBUFFERED=1 \
        PIP_NO_CACHE_DIR=1 \
        PORT=8000
    
    # Libs partagées nécessaires à l'exécution de Pillow (sans toolchain)
    RUN apt-get update && apt-get install -y --no-install-recommends \
        libjpeg62-turbo \
        zlib1g \
        libpng16-16 \
        libopenjp2-7 \
        libtiff5 \
        libfreetype6 \
        liblcms2-2 \
        libwebp7 \
        tzdata \
        && rm -rf /var/lib/apt/lists/*
    
    # Copie des packages Python construits en builder → runtime
    # (les wheels installés avec --prefix=/install sont sous /install)
    COPY --from=builder /install /usr/local
    
    # App non-root
    RUN useradd -m -u 10001 appuser
    WORKDIR /app
    USER appuser
    
    # Copie du code (ajoute un .dockerignore pour éviter node_modules, .venv, etc.)
    COPY --chown=appuser:appuser . /app
    
    # Expose le port de l’app web (Gunicorn/Django par ex.)
    EXPOSE 8000
    
    # CMD par défaut (adapte si ASGI/uvicorn ou autre)
    # Exemple WSGI:
    # CMD ["gunicorn", "project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "2"]
    # Exemple ASGI (si tu as asgi.py):
    # CMD ["gunicorn", "project.asgi:application", "-k", "uvicorn.workers.UvicornWorker", "--bind", "0.0.0.0:8000", "--workers", "2"]
    