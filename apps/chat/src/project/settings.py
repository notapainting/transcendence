# projet/settings.py

from pathlib import Path
import os
from socket import SOCK_STREAM


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'project.urls'

USE_I18N = True
LANGUAGE_CODE = 'en-us'

USE_TZ = True
TIME_ZONE = 'CET'

ADMIN_USERNAME = 'admin'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'django-insecure-0#_lx+w5u%tmt2kl*9li+!(3jdtc3re@ihht6#hn2!p8-90j_v'
ALLOWED_HOSTS = ['*']
CSRF_TRUSTED_ORIGINS = ['https://localhost:8443']
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False
APPEND_SLASH = False

DEBUG = True

ASGI_APPLICATION = "project.asgi.application"

INSTALLED_APPS = [
    'daphne',
    'chat',
    'djangoviz',
]


MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

AUTHENTICATION_BACKENDS = []


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [("chat-redis", 6379)],
        },
    },
}

# Database
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.getenv('DJ_DB_NAME'),
        'USER': os.getenv('DB_USER'),
        'PASSWORD': os.getenv('DB_PASSWORD'),
        'HOST': os.getenv('DB_NAME'),
        'PORT': os.getenv('DB_PORT'),
    }
}

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "VERBOSE": {
            "format": "{levelname} {asctime} ({module}) p:{process:d} t:{thread:d} l:{lineno} => {message}",
            "style": "{",
        },
        "MID": {
            "format": "{levelname} {asctime} => {message}   (f:{filename} l:{lineno:d})",
            "style": "{",
        },
        "SIMPLE": {
            "format": "{levelname} => {message}",
            "style": "{",
        },
    },
    "handlers": {
        "console": {
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "class": "logging.StreamHandler",
            "formatter": os.getenv("DJANGO_LOG_FORMAT", "MID"),
        },
    },
    "loggers": {
        "base": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    }
}