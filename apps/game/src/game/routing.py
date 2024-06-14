# game/routing.py
from django.urls import re_path

from . import consumers

import game.remote as rem

websocket_urlpatterns = [
    # re_path("game/", consumers.GameConsumer.as_asgi()),
    re_path("game/", rem.RemoteGamer.as_asgi()),
]