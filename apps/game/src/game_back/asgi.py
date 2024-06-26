"""
ASGI config for game_back project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.0/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

from game.routing import websocket_urlpatterns
from game_back.middleware import CustomAuthMiddleware
from channels.auth import CookieMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'game_back.settings')

django_asgi_app = get_asgi_application()

import game.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": CookieMiddleware((URLRouter(websocket_urlpatterns))),
})