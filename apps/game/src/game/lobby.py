# game/lobby.py

from channels.layers import get_channel_layer
from game.gamestate import GameState, MIN_SCORE, MAX_SCORE, DEFAULT_SCORE, BONUSED
from rest_framework.renderers import JSONRenderer
import game.enums as enu
import random, httpx, asyncio
from uuid import uuid4

from game.plaza import plaza

LOBBY_MAXIMUM_PLAYERS = 24
LOBBY_DEFAULT_MATCH_PLAYER = 2
LOBBY_DEFAULT_PLAYERS = 8
LOBBY_MINIMUM_PLAYERS = 2

class LobbyException(Exception):
    pass

class ScoreException(LobbyException):
    pass

class MaxPlayerException(LobbyException):
    pass

class InvalidPlayersException(LobbyException):
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
"""
"""
gameing ? loop ? 
"""


"""
!!! MOVE connected list in unique class singleton
separate broadcast in remote vs local
local should use gourp_send? _send? 
"""

class BaseLobby:
    def __init__(self, host, bonused=BONUSED, maxPlayer=LOBBY_DEFAULT_PLAYERS, scoreToWin=DEFAULT_SCORE) -> None:
        # lobby
        self.host = host
        self.invited = []
        self.ready = []
        self.players = []

        # channel
        self._id = str(uuid4())
        self._chlayer = get_channel_layer()

        # settings
        self.bonused = bonused
        self.maxPlayer = maxPlayer
        self.scoreToWin = scoreToWin

    async def _init(self):
        await self._chlayer.group_add(self._id, self.host)

    async def _end(self):
        await self._chlayer.group_discard(self._id, self.host)

# settings
    @property
    def maxPlayer(self):
        return self._maxPlayer

    @maxPlayer.setter
    def maxPlayer(self, value):
        value = int(value)
        if value < len(self.players) or value > LOBBY_MAXIMUM_PLAYERS:
            raise MaxPlayerException()
        self._maxPlayer = value

    @property
    def scoreToWin(self):
        return self._scoreToWin

    @scoreToWin.setter
    def scoreToWin(self, value):
        value = int(value)
        if value < MIN_SCORE or value > MAX_SCORE:
            raise ScoreException()
        self._scoreToWin = value

    def changeSettings(self, settings):
        setattr(self, settings['param'], settings['value'])
        return self.getSettings()

    def getSettings(self):
        return {
            "scoreToWin":self.scoreToWin,
            "bonused":self.bonused,
            "maxPlayer":self.maxPlayer,
        }
# user mgt
    def set_players(self, players):
        if len(players) % 2 != 0 or len(players) == 0:
            raise InvalidPlayersException()
        self.players = players

    def invite(self, user):
        if user not in self.invitations and user not in self.players:
            self.invitations.append(user)
            return True
        return False

    def add(self, user):
        if user not in self.players:
            if len(self.players) == self.maxPlayer:
                raise MaxPlayerException()
            self.players.append(user)
            self.invitation.remove(user)
            return True
        return False

    def kick(self, user):
        kicked = False
        if user in self.invitation:
            self.invitations.remove(user)
            kicked = True
        else:
            if user in self.players:
                self.players.remove(user)
                kicked = True
                if user in self.ready:
                    self.ready.remove(user)
        return kicked

    def check(self, user):
        if user in self.players and user not in self.ready:
            self.ready.append(user)
            return True
        return False

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

    async def next(self):
        pass



class LocalTournament(BaseLobby):
    def __init__(self, host):
        super().__init__(host=host)
        self.current = []
        self.matchCount = -2

    async def broadcast(self, message):
        message['author'] = self.host
        await self._chlayer.group_send(self._id, message)

    async def start(self, players):
        self.set_players(players)
        await self.broadcast({"type":enu.Game.START})
        await self.make_phase()

    async def make_phase(self):
        random.shuffle(self.players)
        self.current = [(self.players[i],self.players[i + 1]) for i in range(0, len(self.players), 2)]
        self.matchCount = -1
        await self.broadcast({"type":enu.Tournament.PHASE, "message":self.current})

    async def next(self):
        self.matchCount += 1
        if self.matchCount == len(self.current):
            if len(self.current) == 1:
                return
            await self.make_phase()
        else:
            match = self.current[self.matchCount]
            self.game_state = GameState(group=self._id, bonused=self.bonused, scoreToWin=self.scoreToWin)
            await self.broadcast({"type":enu.Tournament.MATCH, "message":match, "state":self.game_state.to_dict('none')})

    async def reset(self):
        await self.match_stop()
        self.current = []
        self.matchCount = -2
        self.players = []


    async def end(self):
        await self.match_stop()
        await super()._end()

    async def match_start(self):
        if hasattr(self, "game_state"):
            await self.game_state.start()

    async def match_stop(self):
        if hasattr(self, "game_state"):
            await self.game_state.stop()

    async def match_pause(self):
        if hasattr(self, "game_state"):
            await self.game_state.pause()

    async def match_feed(self, data):
        if hasattr(self, "game_state"):
            if data['message'] == "bonus":
                await self.game_state.feed_bonus(data['bonus'])
            else:
                await self.game_state.feed(data['message'])









# substitute hostname to hsot id for group
# pass groupID to  gamestate 
class RemoteLobby(BaseLobby):
    def __init__(self, host, maxPlayer=LOBBY_DEFAULT_PLAYERS):
        super().__init__(host=host, maxPlayer=maxPlayer)
        self.players.append(host)

    async def _send(self, target_name, message):
        message['author'] = self.host
        target = plaza.translate(target_name)
        await self._chlayer._send(target_name, message)

    async def broadcast(self, message):
        message['author'] = self.host
        await self._chlayer.group_send(self._id, message)


    async def start(self, data):
        await self.broadcast({"type":enu.Game.START})

    async def invite(self, user, type=enu.Invitation.TRN):
        if super().invite(user):
            await self._send({"type":type})

    async def add(self, user):
        if super().add(user):
            await self._chlayer.group_add(self._id, host)

    async def check(self, user):
        if super().check(user):
            await self.broadcast({"type":enu.Game.READY, "author":user, "r":True})

    async def kick(self, user):
        if super().kick(user):
            await self._send({"type":enu.Game.KICK})
            await self._chlayer.group_discard(user, self._id)

    async def end(self):
        await super()._end()
        if self.task is not None:
            await self.task.cancel()
        await self.broadcast({"type":enu.Game.KICK})
        for player in players:
            await self._chlayer.group_discard(player, self._id)


class Tournament(RemoteLobby):
    def __init__(self, host):
        super().__init__(host=host)
        self.matchCount = 0

    async def make_phase(self):
        random.shuffle(self.players)
        self.current = [(self.players[i],self.players[i + 1]) for i in range(0, len(self.players), 2)]
        self.matchCount = len(self.current)
        await self.broadcast({"type":enu.Tournament2.PHASE, "message":self.current})

    async def order_match(self):
        for match in self.current:
            message = {"type":enu.Tournament2.MATCH, "author":self.host, "message":{"host":match[0],"guest":match[1], "settings":self.getSettings()}}
            await self._chlayer.group_send(match[0], message)
            await self._chlayer.group_send(match[1], message)
            await httpx.AsyncClient().post(url='http://chat:8000/api/v1/game/tournament/alert/', data=JSONRenderer().render(message['message']))

    async def update_result(self, data):
        loser = data['message']['loser']
        self.players.remove(loser)
        self.broadcast(data)
        self.matchCount -= 1
        if self.matchCount == 0:
            await self.make_phase()

    def players_state(self):
        return {"invited":self.invited, "players":self.players, "host":self.host, "size":self.maxPlayer}



class Match(RemoteLobby):
    def __init__(self, host, tournament=None):
        super().__init__(host=host, maxPlayer=LOBBY_DEFAULT_MATCH_PLAYER)
        self.task = None
        self.gameState = GameState()
        self.tournament = tournament

    async def invite(self, user):
        if self.tournament is None:
            await super().invite(user, type=enu.Invitation.MATCH)

    async def kick(self, user):
        if self.tournament is None:
            await super().kick(user)

    def changeSettings(self, settings):
        if self.tournament is None:
            super().changeSettings()
            return self.gameState.changeSettings(settings)

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
            # _send match history data to usermgt

            data = self.result
            data['score_w'] = self.result['scores'][data['winner']]
            data['score_l'] = self.result['scores'][data['loser']]
            del data['scores']
            await httpx.AsyncClient().post(url='http://user:8000/user/match_history/new/', data=JSONRenderer().render(data))
            if self.tournament is True:
                await self._chlayer.send_group(self.tournament, {"type":enu.Tournament.RESULT, "message":self.result})
        if self.task is not None:
            self.task.cancel()

"""
class DEADLobby:
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


class DEADMatch(Lobby):
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


class DEADTournament(Lobby):
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
            await httpx.AsyncClient().post(url='http://chat:8000/api/v1/game/tournament/alert/', data=JSONRenderer().render(message['message']))


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
"""