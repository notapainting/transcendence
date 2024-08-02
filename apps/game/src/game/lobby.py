# game/lobby.py

from channels.layers import get_channel_layer
from game.gamestate import GameState, MIN_SCORE, MAX_SCORE, DEFAULT_SCORE, BONUSED
from rest_framework.renderers import JSONRenderer
import game.enums as enu
import random, httpx


LOBBY_MAXIMUM_PLAYERS = 24
LOBBY_DEFAULT_MATCH_PLAYER = 2
LOBBY_DEFAULT_PLAYERS = 8
LOBBY_MINIMUM_PLAYERS = 2

class LobbyException(BaseException):
    pass

class ScoreException(LobbyException):
    pass

class MaxPlayerException(LobbyException):
    pass

def getDefault():
    return {
        "bonused":BONUSED,
        "scoreToWin":DEFAULT_SCORE,
        "maxPlayer":LOBBY_DEFAULT_PLAYERS,
    }

"""
BqseLobby -> LOCAL LOBBY : matchmake/next, + send_json
        -> REM LOBBY : + get chlayer
                |-> MATCH : 
                |-> TRN : 

class BaseLobby:
    def __init__(self, host=None, bonused=BONUSED, maxPlayer=LOBBY_DEFAULT_PLAYERS, scoreToWin=DEFAULT_SCORE) -> None:
        self.bonused = bonused
        self.scoreToWin = scoreToWin
        self.maxPlayer = maxPlayer

        self.task = None
        self.gameState = None

        self.host = host
        self.invited = []
        self.ready = []
        self.players = []
        self.players.append(host)

    @property
    def maxPlayer(self):
        return self._maxPlayer

    @maxPlayer.setter
    def maxPlayer(self, value):
        if value < len(self._players) or value > LOBBY_MAXIMUM_PLAYERS:
            raise ScoreException()
        self._maxPlayer = value

    @property
    def scoreToWin(self):
        return self._scoreToWin

    @scoreToWin.setter
    def scoreToWin(self, value):
        if value < MIN_SCORE or value > MAX_SCORE:
            raise MaxPlayerException()
        self._scoreToWin = value

    def clear(self):
        self.invitations = []
        self.ready = []
        self.players = []
        self.players.add(host)


    def invite(self, user):
        if user not in self.invitations:
            self.invitations.append(user)

    def add(self, user):
        if user not in self.players:
            if len(self.players) == self.maxPlayer:
                raise MaxPlayerException()
            self.players.append(user)

    def kick(self, user):
        try :
            self.invitations.remove(user)
            self.players.remove(user)
            self.ready.remove(user)
        except ValueError:
            pass

    def check(self, user):
        if user in self.player:
            self.ready.append(user)

    def invited(self, user):
        return user in self.invitations

    def full(self):
        if len(self.players) == self.maxPlayer:
            return True
        return False

    def checked(self):
        if len(self.ready) == len(self.players):
            return True
        return False

"""

class Lobby:
    def __init__(self, host, maxPlayer=LOBBY_DEFAULT_PLAYERS, types=enu.Game) -> None:
        self.host = host
        self._maxPlayer = None
        self._test = set()
        self._invited = set()
        self._ready = set()
        self._players = set()
        self._players.add(host)
        self.maxPlayer = maxPlayer
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
    def maxPlayer(self):
        return self._maxPlayer

    @maxPlayer.setter
    def maxPlayer(self, value):
        if hasattr(self, "_players") and value < len(self._players):
            return
        self._maxPlayer = value


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
        if len(self._players) < self.maxPlayer:
            self._players.add(user)
        else :
            print(f"cant add people")

    async def add_ready(self, user):
        if user in self._players:
            self._ready.add(user)
            await self.broadcast({"type":self.types.READY, "author":user, "r":True})

    def ready(self):
        if len(self._ready) == self.maxPlayer:
            return True
        return False

    def full(self):
        if len(self._players) == self.maxPlayer:
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
    def __init__(self, host, maxPlayer=LOBBY_DEFAULT_MATCH_PLAYER, tournament=None):
        super().__init__(host=host, maxPlayer=maxPlayer)
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
            return self.game_state.changeSettings(data)

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
    def __init__(self, host, maxPlayer=LOBBY_MAXIMUM_PLAYERS) -> None:
        super().__init__(host=host, maxPlayer=maxPlayer, types=enu.Tournament)
        self.host = host
        self.losers = set()
        self.match_count = 0

    async def end(self, cancelled=False):
        pass

    async def start(self):
        await super().start()
        print(f"state {self.players_state()}")


    @Lobby.maxPlayer.setter
    def maxPlayer(self, value):
        value = int(value)
        if value % 2 == 0:
            if hasattr(self, "_players") and value < len(self._players):
                print(f"cant decrease max players")
                return
            if value < LOBBY_MINIMUM_PLAYERS:
                value = LOBBY_MINIMUM_PLAYERS
            self._maxPlayer = value


    def changeSettings(self, data):
        setattr(self, data['param'], data['value'])
        return self.getSettings()

    def getSettings(self):
        return {
            "scoreToWin":self.scoreToWin,
            "bonused":self.bonused,
            "maxPlayer":self.maxPlayer,
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
        return {"invited":list(self._invited), "players":list(self._players), "host":self.host, "size":self.maxPlayer}
