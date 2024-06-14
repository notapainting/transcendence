import json, asyncio, time



import game.enums as enu

from game.consumers import GameState, loop_remote_ultime
from game.lobby import Lobby
from game.match import Match

import channels.exceptions as exchan

from logging import getLogger
logger = getLogger(__name__)


from game.base import BaseConsumer

# chg OK but del not

class RemoteGamer(BaseConsumer):

    def __init__(self):
        super().__init__()
        self.username = "Anon"
        self.invitations = set()
        self.match_status = enu.CStatus.IDLE
        self.match = None
        self.host = None
        self.tournament_status = enu.CStatus.IDLE


    async def connect(self):
        self.username = str(self.scope.get('user', 'Anon'))
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        await self.channel_layer.group_add(self.username, self.channel_name)
        lost = Match.is_lost(self.username)
        if lost is False:
            pass
        elif lost is True:
            self.match_status = enu.CStatus.HOST
            self.match = Match.current_match[self.username]
            # implemente reste
        else:
            self.match_status = enu.CStatus.GUEST
            self.host = Match.recover(self.username)
            await self.send_cs(self.host, {"type":enu.Game.RECOVER})
        print(f"hello {self.username} ({self.match_status})!")


    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(self.username, self.channel_name)
        print(f"bye {self.username} ({self.match_status})...")
        if self.match_status == enu.CStatus.HOST:
            self.match.end
            if self.match.task is not None:
                self.match.task.cancel()
            del self.match
        elif self.match_status == enu.CStatus.GUEST:
            Match.broke(host=self.host, guest=self.username)
            await self.send_cs(self.host, {"type":enu.Game.LOST})

    async def send_cs(self, target, data):
        data['author'] = self.username
        await self.channel_layer.group_send(target, data)

    async def receive_json(self, json_data):
        
        if json_data.get('type') == None: # enu.Errors.DECODE
            return await self.send_json({'type':enu.Errors.TYPE})
        print(f"{self.username} ({self.match_status}): type is {json_data['type']} ")
        
        if json_data['type'] == enu.Errors.DECODE:
            return await self.send_json({'type':enu.Errors.DECODE})
        
        if self.match_status == enu.CStatus.HOST:
            match json_data['type']:
                case enu.Game.QUIT:
                    self.match.end
                    del self.match
                case enu.Game.INVITE:
                    await self.match.lobby.invite(json_data['message'])
                case enu.Game.KICK:
                    await self.match.lobby.kick(json_data['message'])
                case enu.Game.READY:
                    if await self.match.lobby.set_ready(self.username) is True:
                        await self.gaming({"message":"startButton"})
                    else:
                        await self.send_cs(self.match.lobby._challenger, json_data)
                case enu.Game.UPDATE: 
                    await self.gaming(json_data)

        elif self.match_status == enu.CStatus.GUEST:
            match json_data['type']:
                case enu.Game.QUIT:
                    self.match_status = enu.CStatus.IDLE
                    await self.send_cs(self.host, json_data)
                    self.host = None
                case enu.Game.READY:
                    await self.send_cs(self.host, json_data)
                case enu.Game.UPDATE: 
                    await self.send_cs(self.host, json_data)

        else:
            match json_data['type']:
                case enu.Game.CREATE:
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
            if self.match.lobby.set_ready(data['message']) is True:
                await self.gaming({"message":"startButton"})
            else:
                await self.send_json(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    async def game_start(self, data):
        await self.send_json(data)

    # async def game_unready(self, data):
    #     if self.match_status == enu.CStatus.HOST:
    #         if self.match.lobby.unready(data['message']):
    #             await self.send_json(data)
    #     elif self.match_status == enu.CStatus.GUEST:
    #         await self.send_json(data)

    async def game_update(self, data):
        if self.match_status == enu.CStatus.HOST:
            await self.gaming(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    # HOST ONLY
    async def game_lost(self, data):
        pass

    async def game_recover(self, data):
        pass

    async def game_quit(self, data):
        self.match.lobby.set_ready.discard(self.match.lobby._challenger)
        self.match.lobby._challenger = None
        await self.send_json(data)

    async def game_join(self, data):
        if self.match.lobby.invited(data['author']) and self.match.lobby.full() is False:
            self.match.lobby._challenger = data['author']
            data['message'] = self.match.game_state.to_dict('none')
            await self.send_json(data)
            await self.send_cs(self.match.lobby._challenger, {"type":enu.Game.ACCEPTED, "message":self.match.game_state.to_dict('none')})
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


    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            if self.match.game_state.status['game_running'] == False :
                self.match.game_state.status['game_running'] = True
                self.match.task = asyncio.create_task(loop_remote_ultime(self))
        elif message == "bonus":
            self.match.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.match.game_state.update_player_position(message))

    # async def loop_remote(self):
    #     global reset
    #     while self.match.game_state.status['game_running']:
    #         message = self.match.game_state.update()
    #         await asyncio.sleep(0.02)
    #         asyncio.create_task(self.match.game_state.update_player_position(message))
    #         await self.send_json(self.match.game_state.to_dict('none'))
    #         await self.send_cs(self.match.game_state.to_dict('none'))
    #         if reset ==  2:
    #             time.sleep(0.5)
    #             reset = 0 
