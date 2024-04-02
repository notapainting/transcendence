# game/routing.py
from django.urls import re_path

from . import consumers

websocket_urlpatterns = [
    re_path("ws/ws-game/", consumers.GameConsumer.as_asgi()),
]