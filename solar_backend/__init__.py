try:  # pragma: no cover - Celery might be absent in tests
    from .celery import app as celery_app
    __all__ = ("celery_app",)
except Exception:  # pragma: no cover
    celery_app = None
    __all__ = ()