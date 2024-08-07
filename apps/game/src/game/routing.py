# game/routing.py
from django.urls import re_path


import game.consumers.remote as rem
import game.consumers.local as loc

websocket_urlpatterns = [
    re_path("game/local/", loc.LocalConsumer.as_asgi()),
    re_path("game/", rem.RemoteGamer.as_asgi()),
]