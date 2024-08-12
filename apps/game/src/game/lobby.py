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


class BaseLobby:
    def __init__(self, host, host_channel_name, bonused=BONUSED, maxPlayer=LOBBY_DEFAULT_PLAYERS, scoreToWin=DEFAULT_SCORE) -> None:
        # lobby
        self.host = host
        self.invitations = []
        self.ready = []
        self.players = []

        # channel
        self._id = str(uuid4())
        self._chlayer = get_channel_layer()
        self._host_channel_name = host_channel_name

        # settings
        self.bonused = bonused
        self.maxPlayer = maxPlayer
        self.scoreToWin = scoreToWin

    async def _init(self):
        await self._chlayer.group_add(self._id, self._host_channel_name)

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

    def uninvite(self, user):
        if user in self.invitations:
            self.invitations.remove(user)
            return True
        return False

    def add(self, user):
        if user not in self.players:
            if len(self.players) == self.maxPlayer:
                raise MaxPlayerException()
            self.players.append(user)
            self.invitations.remove(user)
            return True
        return False

    def kick(self, user):
        kicked = False
        if user in self.invitations:
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


class BaseMatch:
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

    def match_result(self):
        if not hasattr(self, "game_state"):
            return
        winner = self.game_state.status['winner']
        if winner == 'leftWin':
            winner = self.current[self.match_count][0]
            loser = self.current[self.match_count][1]
        else:
            winner = self.current[self.match_count][1]
            loser = self.current[self.match_count][0]
        if hasattr(self, "players"):
            self.players.remove(loser)
        return {"winner":winner, "loser":loser}


class LocalTournament(BaseLobby, BaseMatch):
    def __init__(self, host, host_channel_name):
        super().__init__(host=host, host_channel_name=host_channel_name)
        self.current = []
        self.match_count = -2

    async def broadcast(self, message):
        message['author'] = self.host
        await self._chlayer.group_send(self._id, message)

    async def start(self, players):
        self.set_players(players)
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Game.START}})
        await self.make_phase()

    async def make_phase(self):
        random.shuffle(self.players)
        self.current = [(self.players[i],self.players[i + 1]) for i in range(0, len(self.players), 2)]
        self.match_count = -1
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Tournament.PHASE, "new":True, "message":self.current}})

    async def next(self):
        if self.match_count < -1:
            return
        self.match_count += 1
        if self.match_count == len(self.current):
            if len(self.current) == 1:
                return
            await self.make_phase()
        else:
            match = self.current[self.match_count]
            self.game_state = GameState(group=self._id, bonused=self.bonused, scoreToWin=self.scoreToWin)
            await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Tournament.MATCH, "message":match, "state":self.game_state.to_dict('none')}})

    async def reset(self):
        await self.match_stop()
        self.current = []
        self.match_count = -2
        self.players = []

    async def tournament_result(self):
        print(f"match t oplay : {len(self.current)}")
        if len(self.current) == 1:
            self.reset()
            self.match_count = -2
            await self.broadcast({"type":enu.Game.RELAY, "relay":{'type':enu.Tournament.END, "message":self.players[0]}})

    async def end(self):
        await self.match_stop()
        await super()._end()


# substitute hostname to hsot id for group
# pass groupID to  gamestate 
class RemoteLobby(BaseLobby):
    def __init__(self, host, host_channel_name, maxPlayer=LOBBY_DEFAULT_PLAYERS):
        super().__init__(host=host, host_channel_name=host_channel_name, maxPlayer=maxPlayer)
        self.players.append(host)

    async def _send(self, target_name, message):
        message['author'] = self.host
        target = plaza.translate(target_name, raise_exception=True)
        await self._chlayer.send(target, message)

    async def broadcast(self, message):
        message['author'] = self.host
        await self._chlayer.group_send(self._id, message)

    async def start(self, data=None):
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Game.START}})

    async def invite(self, user, mode=enu.Game.TRN):
        if super().invite(user):
            await self._send(user, {"type":enu.Game.INVITE, "mode":mode})

    async def add(self, user):
        if super().add(user):
            target = plaza.translate(user, raise_exception=True)
            await self._chlayer.group_add(self._id, target)
            return True
        return False

    async def check(self, user):
        if super().check(user):
            await self.broadcast({"type":enu.Game.READY, "player":user, "r":True})
            return True
        return False

    async def kick(self, user):
        if super().kick(user):
            await self._send({"type":enu.Game.KICK})
            await self._chlayer.group_discard(self._id, user)
            return True
        return False

    async def end(self):
        await super()._end()
        if self.task is not None:
            await self.task.cancel()
        await self.broadcast({"type":enu.Game.KICK})
        for player in players:
            await self._chlayer.group_discard(self._id, player)


class Tournament(RemoteLobby):
    def __init__(self, host):
        host_channel_name = plaza.translate(host)
        super().__init__(host=host, host_channel_name=host_channel_name)
        self.match_count = 0

    async def make_phase(self):
        random.shuffle(self.players)
        self.current = [(self.players[i],self.players[i + 1]) for i in range(0, len(self.players), 2)]
        self.match_count = len(self.current)
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
        self.match_count -= 1
        if self.match_count == 0:
            await self.make_phase()

    def players_state(self):
        return {"invited":self.invitations, "players":self.players, "host":self.host, "size":self.maxPlayer}

from django.utils import timezone
class Match(RemoteLobby, BaseMatch):
    def __init__(self, host, tournament=None):
        host_channel_name = plaza.translate(host)
        super().__init__(host=host, host_channel_name=host_channel_name, maxPlayer=LOBBY_DEFAULT_MATCH_PLAYER)
        self.game_state = GameState(group=self._id, bonused=self.bonused, scoreToWin=self.scoreToWin)
        self.tournament = tournament

    async def start(self, data=None):
        await super().start()
        print(f"start send  {timezone.now()}")
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Match.START}})
        print(f"start sleep {timezone.now()}")
        await asyncio.sleep(2)
        print(f"end sleep {timezone.now()}")
        await self.match_start()

    async def invite(self, user):
        if self.tournament is None:
            await super().invite(user, mode=enu.Game.MATCH)

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
        await self.match_stop()
        if cancelled == False:
            if hasattr(self, "result") is False:
                self.result = self.compute()
            data = self.result
            data['score_w'] = self.result['scores'][data['winner']]
            data['score_l'] = self.result['scores'][data['loser']]
            del data['scores']
            await httpx.AsyncClient().post(url='http://user:8000/user/match_history/new/', data=JSONRenderer().render(data))
            if self.tournament is not None:
                await self._chlayer._send(self.tournament, {"type":enu.Tournament.RESULT, "message":self.result})
        

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