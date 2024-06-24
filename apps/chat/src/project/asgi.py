# mysite/asgi.py

import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "project.settings")

from django.core.asgi import get_asgi_application
django_asgi_app = get_asgi_application()

from channels.auth import CookieMiddleware
from channels.routing import ProtocolTypeRouter, URLRouter


from chat.routing import websocket_urlpatterns
from project.middleware import CustomAuthMiddleware


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
