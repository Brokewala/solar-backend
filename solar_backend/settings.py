"""
Default values are hard-coded so the app can boot reliably on Railway without
requiring a `.env` file. Environment variables may override these defaults in
production.
"""

import os
import ast
import sys
import tempfile
import importlib
from pathlib import Path
from datetime import timedelta
from types import ModuleType

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
from dotenv import load_dotenv

load_dotenv()

try:
    importlib.import_module("django.middleware.timezone")
except ModuleNotFoundError:
    from django.utils import timezone as django_timezone
    from django.utils.deprecation import MiddlewareMixin

    timezone_module = ModuleType("django.middleware.timezone")

    class TimeZoneMiddleware(MiddlewareMixin):
        """Fallback middleware for Django versions lacking TimeZoneMiddleware."""

        def process_request(self, request):
            django_timezone.activate(django_timezone.get_default_timezone())

        def process_response(self, request, response):
            django_timezone.deactivate()
            return response

    timezone_module.TimeZoneMiddleware = TimeZoneMiddleware
    sys.modules["django.middleware.timezone"] = timezone_module


# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SECRET_KEY", "django-insecure-517me7l6)qts)dk@or&cs*sj-wm38p!8p918&k7g9kktdav#i5")

# Default configuration so the app boots even without a .env file
DEBUG = True
USE_TZ = True
ALLOWED_HOSTS = ["*"]

CSRF_TRUSTED_ORIGINS = [
    f"https://{h}" for h in ALLOWED_HOSTS if h and not h.startswith("http")
]
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")


# Application definition

INSTALLED_APPS = [
    "daphne",
    "channels",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    'drf_yasg',
    "corsheaders",
    "storages",
    "anymail",
    "rest_framework",
    "rest_framework_simplejwt",
    "django_filters",
    'users',
    'module',
    'battery',
    'panneau',
    'prise',
    'rating',
    'report',
    'subscription',
    'stats',
    "notification.apps.NotificationConfig",
    "graphique.apps.GraphiqueConfig",
    "relaystate.apps.RelaystateConfig"

]

REST_FRAMEWORK = {
    "DEFAULT_PERMISSION_CLASSES": [],
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ],
    "DEFAULT_FILTER_BACKENDS": ["django_filters.rest_framework.DjangoFilterBackend"],
    "DEFAULT_THROTTLE_RATES": {
        "reset_password": "5/hour",
    },
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%S%z",
}

# minutes
SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=24),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=10),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
    "ALGORITHM": "HS256",
    "SIGNING_KEY": SECRET_KEY,
    "VERIFYING_KEY": None,
    "AUTH_HEADER_TYPES": ("Bearer",),
    "USER_ID_FIELD": "id",
    "USER_ID_CLAIM": "user_id",
    "AUTH_TOKEN_CLASSES": ("rest_framework_simplejwt.tokens.AccessToken",),
    "TOKEN_TYPE_CLAIM": "token_type",
}


MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.middleware.timezone.TimeZoneMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "solar_backend.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [os.path.join(BASE_DIR, "templates")],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "solar_backend.wsgi.application"
ASGI_APPLICATION = "solar_backend.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels.layers.InMemoryChannelLayer",
    },
}


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    import dj_database_url

    DATABASES = {
        "default": dj_database_url.config(default=DATABASE_URL, conn_max_age=600, ssl_require=True)
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": os.path.join(BASE_DIR, "db.sqlite3"),
        }
    }

engine = DATABASES["default"].get("ENGINE", "")
if "postgres" in engine:
    db_options = DATABASES["default"].setdefault("OPTIONS", {})
    existing_psql_options = db_options.get("options")
    timezone_option = "-c timezone=Indian/Antananarivo"
    if existing_psql_options:
        if timezone_option not in existing_psql_options:
            db_options["options"] = f"{existing_psql_options} {timezone_option}".strip()
    else:
        db_options["options"] = timezone_option

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/
LANGUAGE_CODE = "en-us"

TIME_ZONE = "Indian/Antananarivo"

USE_I18N = True



# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = "/static/"
# Allow overriding the static files destination via the ``STATIC_ROOT``
# environment variable. This is useful in restricted environments where the
# default location may not be writable (e.g. during collectstatic on read-only
# filesystems).
STATIC_ROOT = os.getenv("STATIC_ROOT", os.path.join(BASE_DIR, "staticfiles"))
if not os.access(os.path.dirname(STATIC_ROOT), os.W_OK):
    STATIC_ROOT = os.path.join(tempfile.gettempdir(), "staticfiles")
MEDIA_URL = "/media/"
MEDIA_ROOT = os.path.join(BASE_DIR, "assets")
# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field
APPEND_SLASH = False
AUTH_USER_MODEL = "users.ProfilUser"
DATA_UPLOAD_MAX_MEMORY_SIZE = 52428800
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"
CORS_ALLOW_HEADERS = (
    "accept",
    "authorization",
    "content-type",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
)
CORS_ALLOW_ALL_ORIGINS = True
CORS_ALLOWED_ORIGINS = [
    "https://solar-backend-production-12aa.up.railway.app",
    "https://solar-bakend-production.up.railway.app",
    "http://localhost:3000",
    "http://localhost:4200",
    "http://localhost:5173",
    "exp://sttlt3y-anonymous-8081.exp.direct",
    "http://localhost:8081",
    "http://192.168.x.x:8081",
    "http://172.20.10.2:8000",
    "http://192.168.1.178:8081",

]
# Email configuration
# EMAIL_BACKEND = "anymail.backends.resend.EmailBackend"
# EMAIL_HOST = "smtp.gmail.com"
# EMAIL_PORT = 587
# EMAIL_HOST_USER = "rakotoarisoa.ga@gmail.com"
# EMAIL_HOST_PASSWORD = "loxb wora pney rane"
# EMAIL_USE_TLS = True
# EMAIL_USE_SSL = False

# ================
EMAIL_BACKEND = "anymail.backends.brevo.EmailBackend"
ANYMAIL = {
    "BREVO_API_KEY":os.getenv("BREVO_API_KEY") 
}
DEFAULT_FROM_EMAIL = 'solar smart system <rakotoarisoa.ga@gmail.com>'
SERVER_EMAIL = "brokewala@gmail.com" 


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
        },
        'mail.reset_password': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}
