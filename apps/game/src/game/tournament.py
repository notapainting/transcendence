# game/tournament.py

from typing import Any
from django.conf import settings
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

from channels.exceptions import  InvalidChannelLayerError
from channels.layers import get_channel_layer

import game.enums as enu
from game.consumers import GameState

from game.lobby import Lobby, Lobby2



TOURNAMENT_MAX_PLAYER = 16
MATCH_MAX_PLAYER = 2

class Tournament(Lobby2):
    def __init__(self, host, n_player=TOURNAMENT_MAX_PLAYER) -> None:
        super().__init__(host=host, n_player=n_player, types=enu.Tournament)
        self.host = host
        self.losers = set()
        self.match_count = 0


    async def end(self, cancelled=False):
        pass

    async def start(self):
        super().start()

    async def make_phase(self):
        import random
        tmp = list(self._players)
        random.shuffle(tmp)
        self.current = [(tmp[i],tmp[i + 1]) for i in range(0, len(tmp), 2)]
        self.match_count = len(self.current)
        self.broadcast({"type":types.PHASE, "message":self.current, "author":self.host})

    async def order_match(self):
        for match in self.current:
            message = {"type":types.MATCH, "author":self.host, "message":{"host":match[0],"guest":match[1]}}
            await self._chlayer.group_send(match[0], message)
            await self._chlayer.group_send(match[1], message)

    async def update_result(self, data):
        loser = data['message']['loser']
        self._players.discard(loser)
        self.losers.add(loser)
        self.broadcast(data)
        self.match_count -= 1
        if self.match_count == 0:
            await self.make_phase()


# tournament end 