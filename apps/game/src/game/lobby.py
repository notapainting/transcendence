# game/lobby.py

from channels.layers import get_channel_layer
from game.gamestate import GameState, MIN_SCORE, MAX_SCORE, DEFAULT_SCORE, BONUSED
from rest_framework.renderers import JSONRenderer
import game.enums as enu
import random, httpx
from uuid import uuid4

import httpx
import asyncio
import traceback
import sys

from game.plaza import plaza, tid_count

from logging import getLogger
logger = getLogger('base')

LOBBY_MAXIMUM_PLAYERS = 36
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

async def send_match_to_blockchain(tournament_id, result):
    logger.info("try to talk to bc")
    url = "http://blockchain:8000/register_match/"

    data = result
    data['tournament_id'] = tournament_id

    timeout = httpx.Timeout(90.0, connect=90.0)
    try:
        task = asyncio.create_task(httpx.AsyncClient(timeout=timeout).post(url, json=data))
        logger.info("Le match a été envoyé à l'API blockchain avec succès.")

    except Exception as e:
        error_message = "Erreur lors de l'envoi à l'API blockchain :\n"
        error_message += f"Type d'erreur : {type(e).__name__}\n"
        error_message += f"Message d'erreur : {str(e)}\n"
        error_message += "Traceback complet :\n"
        error_message += traceback.format_exc()
        logger.critical(error_message)


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

    @property
    def maxPlayer(self):
        return self._maxPlayer

    @maxPlayer.setter
    def maxPlayer(self, value):
        value = int(value)
        if value < len(self.players) or value > LOBBY_MAXIMUM_PLAYERS:
            raise MaxPlayerException("Cant have less max players than current count of players")
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

    def set_players(self, players):
        if len(players) < 2:
            MaxPlayerException("Need more players")
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
                raise MaxPlayerException("Too much players")
            self.players.append(user)
            if user in self.invitations:
                self.invitations.remove(user)
            return True
        return False

    def kick(self, user):
        kicked = self.uninvite(user)
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
        if len(self.ready) == len(self.players) and len(self.ready) == self.maxPlayer:
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

    async def match_pause(self, requester=None):
        if hasattr(self, "game_state"):
            if requester is not None:
                if self.requester is None:
                    self.requester = requester
                    await self.game_state.pause()
                elif self.requester == requester:
                    self.requester = None
                    await self.game_state.pause()
            else:
                await self.game_state.pause()

    async def match_feed(self, data):
        if hasattr(self, "game_state"):
            if data['message'] == "bonus":
                await self.game_state.feed_bonus(data['bonus'])
            else:
                await self.game_state.feed(data['message'])

class BaseTournament:
    def is_end(self):
        if len(self.current) == 1 and not hasattr(self, "odd"):
            return True
        return False

    async def update_result(self, data):
        if data['loser'] in self.players:
            self.players.remove(data['loser'])
        self.match_count -= 1
        if self.match_count == 0:
            return True
        return False

    async def make_phase(self):
        if len(self.players) % 2 != 0:
            if hasattr(self, "odd"):
                self.players.append(self.odd)
                logger.info(f"add odd : {self.odd}, rest: {self.players}")
                del self.odd
            else:
                self.odd = self.players.pop()
                logger.info(f"pop odd : {self.odd}, rest: {self.players}")
        random.shuffle(self.players)
        self.current = [{"id":i, "host":self.players[i],"guest":self.players[i + 1]} for i in range(0, len(self.players), 2)]
        self.match_count = len(self.current)
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Tournament.PHASE, "new":True, "phase":self.current}})

 
class LocalTournament(BaseLobby, BaseTournament, BaseMatch):
    def __init__(self, host, host_channel_name):
        super().__init__(host=host, host_channel_name=host_channel_name)
        self.current = []
        self.match_count = -2

    async def _init(self):
        await super()._init()
        self.id = await tid_count.retrieve()

    async def broadcast(self, message):
        message['author'] = self.host
        await self._chlayer.group_send(self._id, message)

    async def start(self, players):
        if len(players) != self.maxPlayer:
            return
        self.set_players(players)
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Game.START}})
        await self.make_phase()

    async def reset(self):
        await self.match_stop()
        self.current = []
        self.match_count = -2
        self.players = []

    async def next(self):
        if self.match_count > 0:
            match = self.current[len(self.current) - self.match_count]
            self.game_state = GameState(group=self._id, leftPlayer=match['host'], rightPlayer=match['guest'], bonused=self.bonused, scoreToWin=self.scoreToWin)
            await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Tournament.MATCH, "match":match, "state":self.game_state.to_dict()}})

    async def update_result(self, data):
        await send_match_to_blockchain(self.id, self.game_state.result)
        if await super().update_result(data):
            if self.is_end():
                await self.broadcast({"type":enu.Tournament.END, "winner":data['winner']})
                self.reset()
            else:
                await self.make_phase()
   
    async def end(self, smooth=True):
        await self.match_stop()
        await super()._end()

class RemoteLobby(BaseLobby):
    def __init__(self, host, host_channel_name, maxPlayer=LOBBY_DEFAULT_PLAYERS):
        super().__init__(host=host, host_channel_name=host_channel_name, maxPlayer=maxPlayer)
        self.players.append(host)

    async def _send(self, target_name, message):
        message['author'] = self.host
        target = plaza.translate(target_name)
        if target is not None:
            await self._chlayer.send(target, message)

    async def broadcast(self, message):
        message['author'] = self.host
        await self._chlayer.group_send(self._id, message)

    async def start(self, data=None):
        await self.clear_invitations()
        await self.broadcast({"type":enu.Game.RELAY, "relay":{"type":enu.Game.START}})

    async def invite(self, user, mode=enu.Game.TRN):
        if super().invite(user):
            await self._send(user, {"type":enu.Game.INVITE, "mode":mode})
            return True
        return False

    async def reject(self, user):
        if super().uninvite(user):
            await self._send(user, {"type":enu.Invitation.REJECT})
            return True
        return False

    async def clear_invitations(self):
        for user in self.invitations:
            await self.reject(user)

    async def add(self, user):
        if super().add(user):
            target = plaza.translate(user, raise_exception=True)
            await self._chlayer.group_add(self._id, target)
            return True
        return False

    async def remove(self, user):
        if super().kick(user):
            target = plaza.translate(user)
            if target is not None:
                await self._chlayer.group_discard(self._id, target)
            return True
        return False

    async def check(self, user):
        if super().check(user):
            await self.broadcast({"type":enu.Game.READY, "player":user})
            return True
        return False

    async def kick(self, user):
        if user in self.invitations:
            await self.reject(user)
        elif super().kick(user):
            await self._send(user, {"type":enu.Game.KICK})
            await self._chlayer.group_discard(self._id, plaza.translate(user, raise_exception=True))
            return True
        return False

    async def end(self, smooth=True):
        await self.clear_invitations()
        if smooth is False:
            await self.broadcast({"type":enu.Game.KICK})
        for player_name in self.players:
            player = plaza.translate(player_name)
            if player is not None:
                await self._chlayer.group_discard(self._id, player)
        await super()._end()

    async def quit(self):
        await self.broadcast({"type":enu.Game.QUIT})
        await self.end()

class Tournament(RemoteLobby, BaseTournament):
    def __init__(self, host):
        super().__init__(host=host, host_channel_name=plaza.translate(host, raise_exception=True))
        self.match_count = 0

    async def _init(self):
        await super()._init()
        self.id = await tid_count.retrieve()
        
    async def check(self, user=None):
        return False

    def checked(self):
        if self.full():
            return True
        return False

    async def start(self, data=None):
        await super().start()
        message = {
            'author':'tournament',
            'name': f'{self.host} tournament',
            'admins':[],
            'members':self.players,
            'restricts':[],
        }
        promise = await httpx.AsyncClient().post(url='http://chat:8000/api/v1/groups/', data=JSONRenderer().render(message))
        if promise.status_code == 201:
            self.chat_group_id = promise.json()['id']
        await self.make_phase()

    async def end(self, smooth=True):
        if hasattr(self, "chat_group_id"):
            url = f'http://chat:8000/api/v1/groups/{self.chat_group_id}/'
            await httpx.AsyncClient().delete(url=url)
        await super().end(smooth)

    async def make_phase(self):
        await super().make_phase()
        for match in self.current:
            if match['host'] == self.host:
                match['host'] = match['guest']
                match['guest'] = self.host
            message = {"type":enu.Tournament.MATCH, "match":match, "settings":self.getSettings()}
            await self._send(match['host'], message)
            await self._send(match['guest'], message)
            if hasattr(self, "chat_group_id"):
                message = {
                    'author':'tournament',
                    'group':self.chat_group_id,
                    'body': f"Waiting for {match['host']} VS {match['guest']}",
                }
                await httpx.AsyncClient().post(url='http://chat:8000/api/v1/messages/', data=JSONRenderer().render(message))

    async def cheat(self, user):
        data = {}
        data['score_l'] = 0
        data['score_w'] = 99
        if hasattr(self, "current"):
            for match in self.current:
                if match['host'] == user:
                    data['winner'] = match['guest']
                    data['loser'] = match['host']
                    self.current.remove(match)
                    return await self._cheating(data)
                elif match['guest'] == user:
                    data['winner'] = match['host']
                    data['loser'] = match['guest']
                    self.current.remove(match)
                    return await self._cheating(data)
        await self.remove(user)


    async def _cheating(self, data):
        await self.remove(data['loser'])
        if not hasattr(self, "odd"):
            self.odd = data['winner']
        logger.info(f"current match : {self.current}")
        await self.update_result(data) 

    async def next(self, user):
        pass

    async def update_result(self, data):
        await send_match_to_blockchain(self.id, data)
        if await super().update_result(data):
            if self.is_end():
                await self.broadcast({"type":enu.Tournament.END, "winner":data['winner']})
                await self.end()
            else:
                await self.make_phase()
        else:
            await self._send(data['winner'], {"type":enu.Tournament.PHASE, "new":False})
            await self._send(data['loser'], {"type":enu.Tournament.PHASE, "new":False})

    def players_state(self):
        return {"invited":self.invitations, "players":self.players, "host":self.host, "size":self.maxPlayer}

class Match(RemoteLobby, BaseMatch):
    def __init__(self, host, tournament=None, settings=None):
        super().__init__(host=host, host_channel_name=plaza.translate(host, raise_exception=True), maxPlayer=LOBBY_DEFAULT_MATCH_PLAYER)
        self.tournament = tournament
        self.requester = None
        self.go = 0
        if settings is not None:
            self.bonused = settings['bonused']
            self.scoreToWin = settings['scoreToWin']

    async def start(self, data=None):
        await super().start()
        self.game_state = GameState(group=self._id, leftPlayer=self.players[0], rightPlayer=self.players[1], bonused=self.bonused, scoreToWin=self.scoreToWin)
        await self.broadcast({"type":enu.Match.START, "message":self.game_state.to_dict()})
        await self.match_start()

    async def go(self):
        self.go += 1
        if self.go == 2:
            await self.lobby.match_start()

    async def invite(self, user):
        if self.tournament is None:
            return await super().invite(user, mode=enu.Game.MATCH)
        return False

    async def kick(self, user):
        if self.tournament is None:
            await super().kick(user)

    def changeSettings(self, settings):
        if self.tournament is None:
            return super().changeSettings(settings)

    async def end(self, smooth=True, cancelled=False):
        await self.match_stop()
        if hasattr(self, "game_state"):
            result = self.game_state.result
            await httpx.AsyncClient().post(url='http://user:8000/user/match_history/new/', data=JSONRenderer().render(result))
            if self.tournament is not None:
                await self._send(self.tournament, {"type":enu.Match.RESULT, "message":result})
            elif cancelled is True:
                await send_match_to_blockchain(0, result)
        await super().end(smooth=smooth)

    async def next(self):
        pass

