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

class Tournament:
    current_tournament = {}

    def __str__(self) -> str:
        return self.name

    def __init__(self, host, **kwargs) -> None:
        self.name = 'SuperDuper'
        self.max_player = TOURNAMENT_MAX_PLAYER
        self.host = host
        self.params = kwargs.get('params')
        self.invited = set()
        self.players = set()
        self.players.add(self.name)
        self._chlayer = get_channel_layer()

    async def clear(self):
        for user in self.players:
            await self._chlayer.group_send(user, {"message":enu.Tournament.KICK, "author":self.host})
        for user in self.invited:
            await self._chlayer.group_send(user, {"message":enu.Tournament.KICK, "author":self.host})

    async def invite(self, user):
        self.invited.add(user)
        await self._chlayer.group_send(user, {"type":enu.Tournament.INVITE, "author":self.host})

    async def kick(self, user):
        self.invited.discard(user)
        self.players.discard(user)
        await self._chlayer.group_send(user, {"type":enu.Tournament.KICK, "author":self.host})
    

    def invited(self, user):
        return user in self.invited