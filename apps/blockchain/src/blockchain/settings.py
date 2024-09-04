# projet/settings.py

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'blockchain.urls'

USE_I18N = True
LANGUAGE_CODE = 'en-us'

ADMIN_USERNAME = 'admin'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

ALLOWED_HOSTS = ['*']


APPEND_SLASH = False

DEBUG = False


MIDDLEWARE = [
    "django.middleware.common.CommonMiddleware",
]

AUTHENTICATION_BACKENDS = []


CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_HOSTNAME', 'redis'), os.getenv('REDIS_PORT', 6379))],
        },
    },
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