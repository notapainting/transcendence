# game/lobby.py

from channels.layers import get_channel_layer
from game.gamestate import GameState, MAX_SCORE, DEFAULT_SCORE

import game.enums as enu
import random


LOBBY_MAXIMUM_PLAYERS = 8
LOBBY_DEFAULT_PLAYERS = 2
LOBBY_MINIMUM_PLAYERS = 2

class Lobby:
    def __init__(self, host, nPlayers=LOBBY_DEFAULT_PLAYERS, types=enu.Game) -> None:
        self.host = host
        self._nPlayers = None
        self._test = set()
        self._invited = set()
        self._ready = set()
        self._players = set()
        self._players.add(host)
        self.nPlayers = nPlayers
        self._chlayer = get_channel_layer()
        self.types = types
        self.bonused = True
        self.scoreToWin = DEFAULT_SCORE

    async def clear(self):
        for user in self._invited:
            await self._chlayer.group_send(user, {"type":self.types.KICK, "author":self.host})
        self.broadcast({"type":self.types.KICK, "author":self.host})
        self._invited = set()
        self._ready = set()
        self._players = set()
        self._players.add(self.host)

    @property
    def nPlayers(self):
        return self._nPlayers

    @nPlayers.setter
    def nPlayers(self, value):
        if hasattr(self, "_players") and value < len(self._players):
            return
        self._nPlayers = value


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

    def add(self, user):
        if len(self._players) < self.nPlayers:
            self._players.add(user)
        else :
            print(f"cant add people")

    async def add_ready(self, user):
        if user in self._players:
            self._ready.add(user)
            await self.broadcast({"type":self.types.READY, "author":user, "r":True})

    def ready(self):
        if len(self._ready) == self.nPlayers:
            return True
        return False

    def full(self):
        if len(self._players) == self.nPlayers:
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

    def changeSettings(self, data):
        if hasattr(self, "game_state"):
            self.game_state.changeSettings(data)

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
            import httpx
            from rest_framework.renderers import JSONRenderer
            data = self.result
            data['score_w'] = self.result['scores'][data['winner']]
            data['score_l'] = self.result['scores'][data['loser']]
            del data['scores']
            await httpx.AsyncClient().post(url='http://user:8000/user/match_history/new/', data=JSONRenderer().render(data))
            if self.tournament is True:
                await self._chlayer.send_group(self.tournament, {"type":enu.Tournament.RESULT, "message":self.result})
        if self.task is not None:
            self.task.cancel()


class Tournament(Lobby):
    def __init__(self, host, nPlayers=LOBBY_MAXIMUM_PLAYERS) -> None:
        super().__init__(host=host, nPlayers=nPlayers, types=enu.Tournament)
        self.host = host
        self.losers = set()
        self.match_count = 0

    async def end(self, cancelled=False):
        pass

    async def start(self):
        await super().start()
        print(f"state {self.players_state()}")


    @Lobby.nPlayers.setter
    def nPlayers(self, value):
        if value % 2 == 0:
            if hasattr(self, "_players") and value < len(self._players):
                print(f"cant decrease max players")
                return
            if value < LOBBY_MINIMUM_PLAYERS:
                value = LOBBY_MINIMUM_PLAYERS
            self._nPlayers = value


    def changeSettings(self, data):
        setattr(self, data['param'], data['value'])

    def getSettings(self):
        return {
            "scoreToWin":self.scoreToWin,
            "bonused":self.bonused,
            "nPlayers":self.nPlayers,
        }

    async def make_phase(self):
        tmp = list(self._players)
        random.shuffle(tmp)
        self.current = [(tmp[i],tmp[i + 1]) for i in range(0, len(tmp), 2)]
        self.match_count = len(self.current)
        await self.broadcast({"type":self.types.PHASE, "message":self.current, "author":self.host})

    async def order_match(self):
        for match in self.current:
            message = {"type":self.types.MATCH, "author":self.host, "message":{"host":match[0],"guest":match[1], "settings":self.getSettings()}}
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

    def players_state(self):
        return {"invited":list(self._invited), "players":list(self._players), "host":self.host, "size":self.nPlayers}
