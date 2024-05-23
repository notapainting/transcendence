# game/routing.py
from django.urls import re_path

from . import consumers

import game.lcons as rc
import game.lconsv2 as rc2

websocket_urlpatterns = [
    # re_path("game/", consumers.GameConsumer.as_asgi()),
    re_path("game/", rc.RemoteGameConsumer.as_asgi()),
    # re_path("game/", rc2.UltimateGamer.as_asgi()),
]