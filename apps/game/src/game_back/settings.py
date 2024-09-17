# game_back/settings.py

from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent



# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = ['*']


INSTALLED_APPS = [
    'daphne',
	'game',
]

MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
]

# ROOT_URLCONF = 'game_back.urls'

ASGI_APPLICATION = "game_back.asgi.application"

CHANNEL_LAYERS = {
    "default": {
        "BACKEND": "channels_redis.core.RedisChannelLayer",
        "CONFIG": {
            "hosts": [(os.getenv('REDIS_HOSTNAME', 'redis'), os.getenv('REDIS_PORT', 6379))],
        },
    },
}



LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'CET'

USE_I18N = True

USE_TZ = True


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
    "root": {
        "handlers": ["console"],
        "level": "WARNING",
        "propagate": False,
    },
    "loggers": {
        "base": {
            "handlers": ["console"],
            "level": os.getenv("DJANGO_LOG_LEVEL", "INFO"),
            "propagate": False,
        },
    }
}
