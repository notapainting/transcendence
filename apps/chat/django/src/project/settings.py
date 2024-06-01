# projet/settings.py

from pathlib import Path
from os import getenv
from socket import SOCK_STREAM


BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_URLCONF = 'project.urls'

USE_I18N = True
LANGUAGE_CODE = 'en-us'

USE_TZ = False
TIME_ZONE = 'CET'


# SECURITY WARNING: keep the secret key used in production secret!
# SECRET_KEY = 'django-insecure-0#_lx+w5u%tmt2kl*9li+!(3jdtc3re@ihht6#hn2!p8-90j_v'

ALLOWED_HOSTS = ['*']
CSRF_COOKIE_SECURE = False
APPEND_SLASH = False

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
        'NAME': getenv('DJ_DB_NAME'),
        'USER': getenv('DB_USER'),
        'PASSWORD': getenv('DB_PASSWORD'),
        'HOST': getenv('DB_NAME'),
        'PORT': getenv('DB_PORT'),
    }
}