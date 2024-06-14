# game/tournament.py

from typing import Any
from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

from channels.exceptions import  InvalidChannelLayerError
from channels.layers import get_channel_layer

import game.enums as enu
from game.consumers import GameState




TOURNAMENT_MAX_PLAYER = 16
MATCH_MAX_PLAYER = 2

class BaseLobby:
    def __init__(self, host, guest=None):
        self.host = host
        self.guest = guest
        self._ready = set()
        self._invited = set()
        self._chlayer = get_channel_layer()

    async def ready(self, user):
        self._ready.add(user)
        if len(self._ready) == MATCH_MAX_PLAYER:
            await self._chlayer.group_send(self.host, {"type":enu.Game.START, "author":self.host})
            await self._chlayer.group_send(self._challenger, {"type":enu.Game.START, "author":self.host})
            return True
        else:
            return False

    async def unready(self, user):
        if len(self._ready) != MATCH_MAX_PLAYER:
            self._ready.discard(user)
            # await self._chlayer.send(self.host, {"type":enu.Game.UNREADY, "author":self.host})
            # await self._chlayer.send(self.guest, {"type":enu.Game.UNREADY, "author":self.host})

    def is_ready(self, user):
        return user in self._ready

class Match(BaseLobby):
    def __init__(self, host, guest):
        self._invited = set()


class Tournament:
    current_tournament = {}
    lost_guest = {}

    def __str__(self) -> str:
        return self.name

    def __init__(self, owner, **kwargs) -> None:
        self.name = 'SuperDuper'
        self.max_player = TOURNAMENT_MAX_PLAYER
        self.owner = owner
        self.params = kwargs.get('params')
        self.invited = set()
        self.participants = set()
        self._ready = set()
        self._chlayer = get_channel_layer()




