FROM python:3.10

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends git libpq-dev ffmpeg curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

COPY requirements.txt /app/
RUN pip install -r requirements.txt

COPY . /app/

COPY docker/entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

EXPOSE 8000

HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
    CMD curl -fsS "http://0.0.0.0:${PORT:-8000}/health/" || exit 1

ENTRYPOINT ["/entrypoint.sh"]

CMD ["sh", "-c", "uvicorn solar_backend.asgi:application --host 0.0.0.0 --port ${PORT:-8000} --proxy-headers --forwarded-allow-ips='*' --timeout-keep-alive 5"]

