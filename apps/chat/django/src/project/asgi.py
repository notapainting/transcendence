# mysite/asgi.py

import os

from channels.auth import CookieMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator

from django.core.asgi import get_asgi_application

from chat.routing import websocket_urlpatterns
from project.middleware import CustomAuthMiddleware

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter(
    {
        "http": (CookieMiddleware(django_asgi_app)),
        "websocket": (
           CookieMiddleware(
               CustomAuthMiddleware(
                   URLRouter(websocket_urlpatterns)))
        ),
    }
)
