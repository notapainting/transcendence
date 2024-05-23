import json, asyncio, time

from game.base import BaseConsumer

import game.enums as enu
import channels.exceptions as exchan

from game.consumers import GameState
from game.lobby import Lobby
from game.match import Match

from logging import getLogger
logger = getLogger(__name__)




"""
RemoteGamer  -> Match  -> GameState
            |        | -> Lobby
            |
            | -> Tournament
"""

class RemoteGameConsumer(BaseConsumer):

    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.match_status = enu.CStatus.IDLE
        self.tournament_status = enu.CStatus.IDLE
        self.lobby = None
        self.invitations = set()
        self.host = None
        self.game_state = None

    async def connect(self):
        self.username = str(self.scope.get('user', 'Anon'))
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        print(f"hello {self.username}")
        await self.channel_layer.group_add(self.username, self.channel_name)

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.channel_name, self.username)
        if self.match_status == enu.CStatus.HOST:
            pass
        elif self.match_status == enu.CStatus.GUEST:
            pass

    async def send_cs(self, target, data):
        data['author'] = self.username
        print(f"send to {target}")
        self.channel_layer.group_send(target, data)

    async def receive_json(self, json_data):
        
        if json_data.get('type') == None: # enu.Errors.DECODE
            return await self.send_json({'type':enu.Errors.DECODE})
        print(f"type is {json_data['type']} ")
        if self.match_status == enu.CStatus.HOST:
            match json_data['type']:
                case enu.Game.QUIT:
                    await self.lobby.clear
                case enu.Game.INVITE:
                    await self.lobby.invite(json_data['message'])
                case enu.Game.KICK:
                    await self.lobby.kick(json_data['message'])
                case enu.Game.READY:
                    if self.lobby.set_ready(self.username) is True:
                        await self.gaming({"message":"startButton"})
                    else:
                        await self.send_cs(self.lobby._challenger, json_data)
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
                    self.lobby = Lobby(self.username)
                    self.game_state = GameState()
                case enu.Game.JOIN:
                    if json_data['message'] in self.invitations:
                        self.invitations.discard(json_data['message'])
                        await self.send_cs(json_data['message'], json_data)

    # BOTH
    async def game_invite(self, data):
        self.invitations.add(data['author'])
        print(f"invited by {data['author']}")
        await self.send_json(data)

    async def game_ready(self, data):
        if self.match_status == enu.CStatus.HOST:
            if await self.lobby.set_ready(self.username) is True:
                await self.gaming({"message":"startButton"})
            else:
                await self.send_json(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    async def game_update(self, data):
        if self.match_status == enu.CStatus.HOST:
            await self.gaming(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    # HOST ONLY
    async def game_quit(self, data):
        self.lobby._challenger = None
        self.lobby.n_ready -= 1
        await self.send_json(data)

    async def game_join(self, data):
        if self.lobby.invited(data['author']) and self.lobby.full() is False:
            self.lobby._challenger = data['author']
            data['message'] = self.game_state.to_dict('none')
            await self.send_json(data)
            await self.send_cs(self.lobby._challenger, {"type":enu.Game.ACCEPTED, "message":self.game_state.to_dict('none')})
        else:
            await self.send_cs(data['author'], {"type":enu.Game.DENY})

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
            if self.game_state.status['game_running'] == False :
                self.game_state.status['game_running'] = True
                asyncio.create_task(self.loop_remote())
        elif message == "bonus":
            self.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.game_state.update_player_position(message))

    async def loop_remote(self):
        global reset
        while self.game_state.status['game_running']:
            message = self.game_state.update()
            await asyncio.sleep(0.02)
            asyncio.create_task(self.game_state.update_player_position(message))
            await self.send_json(self.game_state.to_dict('none'))
            await self.send_cs(self.game_state.to_dict('none'))
            if reset ==  2:
                time.sleep(0.5)
                reset = 0 
