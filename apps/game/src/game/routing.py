# game/routing.py
from django.urls import re_path

from . import consumers

import game.remote as rem

websocket_urlpatterns = [
    re_path("game/local/", consumers.GameConsumer.as_asgi()),
    re_path("game/local/tounament", consumers.TournamentConsumer.as_asgi()),
    re_path("game/", rem.RemoteGamer2.as_asgi()),
]