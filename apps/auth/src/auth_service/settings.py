"""
Django settings for auth_service project.

Generated by 'django-admin startproject' using Django 5.0.2.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/5.0/ref/settings/
"""

import os
from pathlib import Path
# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/5.0/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

#Change current User by CustomUser
AUTH_USER_MODEL = 'auth_service.CustomUser'

SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True

#REST FRAMEWORK CONFIG
REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
	# 'DEFAULT_THROTTLE_CLASSES': [
    #     'rest_framework.throttling.AnonRateThrottle'
    # ],
    # 'DEFAULT_THROTTLE_RATES': {
    #     'anon': '5/min'
    # }
}

#TOKEN JWT DURATION
from datetime import timedelta

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=1),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
}

#e-mail config

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_USE_TLS = True
EMAIL_PORT = 587
EMAIL_HOST_USER = 'jill.transcendance@gmail.com'
EMAIL_HOST_PASSWORD = 'dnml pljr jdnn cxco'

# Application definition

INSTALLED_APPS = [
    'auth_service',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
	'rest_framework.authtoken',
	'rest_framework', #framework rest
	"corsheaders" #autorisation de connection du front
]


#dev mode allow all connexion (must be the proxy server after)



MIDDLEWARE = [
	"corsheaders.middleware.CorsMiddleware",  # Doit être en haut
	"django.middleware.common.CommonMiddleware",
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]


CORS_ALLOW_ALL_ORIGINS = True
ALLOWED_HOSTS = ['*']

# Activer les cookies sécurisés (à définir sur True pour une utilisation en production avec HTTPS)
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_SECURE = False


# Activer les cookies HTTPOnly
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Configuration des domaines (laissez vide pour un développement en local)
SESSION_COOKIE_DOMAIN = ''
CSRF_COOKIE_DOMAIN = ''

CSRF_TRUSTED_ORIGINS = ['https://localhost:8443']


ROOT_URLCONF = 'auth_service.urls'

TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

ADMIN_USERNAME = os.getenv('DJANGO_AUTH_ADMIN_USERNAME', 'admin')
ADMIN_EMAIL = os.getenv('DJANGO_AUTH_ADMIN_MAIL', 'admin@localhost')
ADMIN_PASSWORD = os.getenv('DJANGO_AUTH_ADMIN_PASSWORD', 'admin_password')


AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
        'OPTIONS': {
            'user_attributes': ('username', 'email', 'first_name', 'last_name'),
            'max_similarity': 0.7,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
        'OPTIONS': {
            'min_length': 8,
        }
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [TEMPLATE_DIR],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'auth_service.wsgi.application'


# Database
# https://docs.djangoproject.com/en/5.0/ref/settings/#databases


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



# Internationalization
# https://docs.djangoproject.com/en/5.0/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/5.0/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/5.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


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

