# game/lobby.py

from channels.layers import get_channel_layer
from game.consumers import GameState

import game.enums as enu
import random


TOURNAMENT_MAX_PLAYER = 4

class Lobby:
    def __init__(self, host, n_players=2, types=enu.Game) -> None:
        self.host = host
        self._invited = set()
        self._ready = set()
        self._players = set()
        self._players.add(host)
        self.n_players = n_players
        self._chlayer = get_channel_layer()
        self.types=types

    async def clear(self):
        for user in self._invited:
            await self._chlayer.group_send(user, {"type":self.types.KICK, "author":self.host})
        self.broadcast({"type":self.types.KICK, "author":self.host})

    async def invite(self, user):
        if user == "" or user == self.host:
            return ;
        self._invited.add(user)
        await self._chlayer.group_send(user, {"type":self.types.INVITE, "author":self.host})

    async def kick(self, user):
        if user == "":
            return ;
        self._players.discard(user)
        self._invited.discard(user)
        await self._chlayer.group_send(user, {"type":self.types.KICK, "author":self.host})

    async def add(self, user):
        self._players.add(user)
        if self.n_players < len(self._players):
            print(f"too much player : len is {len(self._players)}, max is {self.n_players}")
            self._players.discard(user)
            return False
        return True

    async def add_ready(self, user):
        if user == "":
            return ;
        self._ready.add(user)

        await self.broadcast({"type":self.types.READY, "author":user, "r":True})

    def ready(self):
        if len(self._ready) == self.n_players:
            return True
        return False

    def full(self):
        if len(self._players) == self.n_players:
            return True
        return False

    async def start(self):
        await self.broadcast({"type":self.types.START, "author":self.host})

    def invited(self, user):
        return user in self._invited

    async def broadcast(self, message):
        for player in self._players:
            await self._chlayer.group_send(player, message)


class Match(Lobby):

    def __init__(self, host, tournament=None):
        super().__init__(host)
        self._players.add(host)
        self.game_state = GameState()
        self.task = None
        self.host = host
        self.tournament = tournament

    async def invite(self, user):
        if self.tournament is None:
            await super().invite(user)

    async def kick(self, user):
        if self.tournament is None:
            await super().kick(user)

    def compute(self):
        guest = [x for x in list(self._players) if x != self.host][0]
        scores = {self.host:self.game_state.status['leftPlayerScore'], guest:self.game_state.status['rightPlayerScore']}
        winner = self.game_state.status['winner']
        loser = [x for x in list(self._players) if x != winner][0]
        if winner == 'leftWin':
            winner = self.host
        else:
            winner = guest
        self.result = {"scores":scores,"winner":winner, "loser":loser}
        return self.result

    async def end(self, cancelled=False):
        if cancelled == False:
            if hasattr(self, "result") is False:
                self.result = self.compute()
            # send match history data to usermgt
            # import httpx
            # await httpx.AsyncClient().post(url='http://auth-service:8000/user/match/', data=self.result)
            if self.tournament is True:
                await self._chlayer.send_group(self.tournament, {"type":enu.Tournament.RESULT, "message":self.result})
        if self.task is not None:
            self.task.cancel()


class Tournament(Lobby):
    def __init__(self, host, n_players=TOURNAMENT_MAX_PLAYER) -> None:
        super().__init__(host=host, n_players=n_players, types=enu.Tournament)
        self.host = host
        self.losers = set()
        self.match_count = 0

    async def end(self, cancelled=False):
        pass

    async def start(self):
        super().start()

    async def make_phase(self):
        tmp = list(self._players)
        random.shuffle(tmp)
        self.current = [(tmp[i],tmp[i + 1]) for i in range(0, len(tmp), 2)]
        self.match_count = len(self.current)
        self.broadcast({"type":self.types.PHASE, "message":self.current, "author":self.host})

    async def order_match(self):
        for match in self.current:
            message = {"type":self.types.MATCH, "author":self.host, "message":{"host":match[0],"guest":match[1]}}
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
