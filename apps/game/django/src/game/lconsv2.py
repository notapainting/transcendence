import json, asyncio, time

from channels.generic.websocket import AsyncWebsocketConsumer

from game.consumers import GameState

import game.enums as enu
from game.tournament import Lobby, Match, MatchManager

import channels.exceptions as exchan
from logging import getLogger
logger = getLogger(__name__)

from game.lcons import BaseConsumer

# chg OK but del not

class UltimateGamer(BaseConsumer):

    def __init__(self):
        self.username = "Anon"
        self.match_status = enu.CStatus.IDLE
        self.tournament_status = enu.CStatus.IDLE
        self.invitations = set()
        self.host = None
        self.match = None


    async def connect(self):
        self.username = self.scope.get('user', 'Anon')
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        await self.channel_layer.group_add(self.channel_name, self.username)

    async def disconnect(self, close_code):
        if self.match_status == enu.CStatus.HOST:
            pass
        elif self.match_status == enu.CStatus.GUEST:
            pass

    async def send_cs(self, target, data):
        data['author'] = self.username
        self.channel_layer.send(target, data)

    async def receive_json(self, json_data):
        if self.match_status == enu.CStatus.HOST:
            match json_data['type']:
                case enu.Game.QUIT: 
                    self.match.end
                    # ???
                case enu.Game.INVITE : 
                    self.match.lobby.invite(json_data['target'])
                case enu.Game.KICK : 
                    self.match.lobby.kick(json_data['target'])
                case enu.Game.READY : 
                    if self.match.lobby.set_ready(self.username) is True:
                        await self.gaming({"message":"startButton"})
                    else:
                        await self.send_cs(self.match.lobby._challenger, json_data)
                case '_': 
                    await self.gaming(json_data)

        elif self.match_status == enu.CStatus.GUEST:
            match json_data['type']:
                case enu.Game.QUIT: 
                    self.match_status = enu.CStatus.IDLE
                    await self.send_cs(self.host, json_data)
                    self.host = None
                case enu.Game.READY :
                    await self.send_cs(self.host, json_data)

        else:
            match json_data['type']:
                case enu.Game.CREATE : 
                    self.match_status = enu.CStatus.HOST
                    self.match = Match(self.username)
                case enu.Game.JOIN:
                    if json_data['message'] in self.invitations:
                        self.invitations.discard(json_data['message'])
                        await self.send_cs(json_data['message'], json_data)

    # BOTH
    async def game_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def game_ready(self, data):
        if self.match_status == enu.CStatus.HOST:
            if self.match.lobby.set_ready(self.username) is True:
                await self.gaming({"message":"startButton"})
            else:
                await self.send_json(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    async def game_update(self, data):
        if self.match_status == enu.CStatus.HOST:
            self.gaming(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    # HOST ONLY
    async def game_quit(self, data):
        self.match.lobby.set_ready.discard(self.match.lobby._challenger)
        self.match.lobby._challenger = None
        await self.send_json(data)

    async def game_join(self, data):
        if self.match.lobby.invited(data['author']) and self.match.lobby.full() is False:
            self.match.lobby._challenger = data['author']
            await self.send_cs(self.match.lobby._challenger, {"message":enu.Game.ACCEPTED})
            await self.send_json(data)
        else:
            await self.send_cs(data['author'], {"message":enu.Game.DENY})

    # GUEST ONLY
    async def game_deny(self, data):
        await self.send_json(data)

    async def game_accepted(self, data):
        self.host = data['author']
        self.match_status = enu.CStatus.GUEST
        await self.send_json(data)

    async def game_kick(self, data):
        if data['author'] == self.host:
            self.host = None
            self.match_status = enu.CStatus.IDLE
        else:
            self.invitations.discard(data['author'])
        await self.send_json(data)

    async def game_settings(self, data):
        await self.send_json(data)

    async def game_start(self, data):
        await self.send_json(data)

    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            if self.match.game_state.status['game_running'] == False :
                self.match.game_state.status['game_running'] = True
                asyncio.create_task(self.loop_remote())
        elif message == "bonus":
            self.match.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.match.game_state.update_player_position(message))

    async def loop_remote(self):
        global reset
        while self.match.game_state.status['game_running']:
            message = self.match.game_state.update()
            await asyncio.sleep(0.02)
            asyncio.create_task(self.match.game_state.update_player_position(message))
            await self.send_json(self.match.game_state.to_dict('none'))
            await self.send_cs(self.match.game_state.to_dict('none'))
            if reset ==  2:
                time.sleep(0.5)
                reset = 0 
