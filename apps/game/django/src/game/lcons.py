import json, asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

from game.consumers import GameState

import game.enums as enu
from game.tournament import Lobby


import channels.exceptions as exchan
from logging import getLogger
logger = getLogger(__name__)


class BaseConsumer(AsyncWebsocketConsumer):
    async def dispatch(self, message):
        logger.info(f"msg type : {message['type']}")
        try :
            await super().dispatch(message)
        except ValueError as error:
            logger.warning(error)
            await self.send_json({'type':enu.Errors.TYPE})
        except BaseException:
            raise

    @classmethod
    async def decode_json(cls, text_data):
        try :
            return json.loads(text_data)
        except:
            return {'type':enu.Errors.DECODE}

    @classmethod
    async def encode_json(cls, content):
        try:
            return json.dumps(content)
        except:
            return json.dumps({'type':enu.Errors.ENCODE})

    async def send_json(self, content, close=False):
        await super().send(text_data=await self.encode_json(content), close=close)


    async def websocket_receive(self, message):
        if "text" in message:
            await self.receive_json(json_data=await self.decode_json(message["text"]))
        else:
            await self.receive_bytes(bytes_data=message["bytes"])

    async def receive_json(self, json_data, **kwargs):
        pass

    async def receive_bytes(self, bytes_data, **kwargs):
        pass


    async def error_decode(self, data):
        logger.info(data)

    async def error_encode(self, data):
        logger.info(data)




class RemoteGameConsumer(BaseConsumer):
    def __init__(self):
        self.username = "Anon"
        self.match_status = enu.CStatus.IDLE
        self.tournament_status = enu.CStatus.IDLE
        self.lobby = None
        self.invitations = set()

    async def connect(self):
        self.username = self.scope.get('user', 'Anon')
        if self.username is None:
            raise exchan.DenyConnection()
        await self.accept()
        await self.channel_layer.group_add(self.channel_name, self.username)

    async def disconnect(self, close_code):
        del self.game_state

    async def send_cs(self, target, data):
        data['type'] = data['message']
        self.channel_layer.send(target, data)

    async def receive_json(self, json_data):
        json_data['author'] = self.username
        if self.match_status == enu.CStatus.HOST:
            json_data['host'] = True
            match json_data['message']:
                case enu.Game.QUIT: 
                    await self.send_cs(self.lobby.challenger, {"message":enu.Game.KICK})
                    for user in self.lobby.invitation_list:
                        await self.send_cs(user, {"message":enu.Game.CANCEL})
                    del self.lobby
                case enu.Game.INVITE : 
                    self.lobby.invite(json_data['target'])
                    await self.send_cs(json_data['target'], json_data)
                case enu.Game.CANCEL : 
                    self.lobby.uninvite(json_data['target'])
                    await self.send_cs(json_data['target'], json_data)
                case enu.Game.KICK :
                    self.lobby.challenger = None
                    await self.send_cs(json_data['target'], json_data)
                case enu.Game.READY : 
                    self.lobby.n_ready += 1
                    if self.lobby.n_ready is 2:
                        await self.gaming({"message":"startButton"})
                        await self.send_cs(self.lobby.challenger, {"message":enu.Game.START})
                    else:
                        await self.send_cs(self.lobby.challenger, json_data)
                case '_': 
                    await self.gaming(json_data)

        elif self.match_status == enu.CStatus.GUEST:
            json_data['host'] = False
            match json_data['message']:
                case enu.Game.JOIN : 
                    self.invitations.discard(data['author'])
                    await self.send_cs(json_data['target'], json_data)
                case enu.Game.QUIT: 
                    self.match_status = enu.CStatus.IDLE
                    await self.send_cs(json_data['target'], json_data)
                case enu.Game.READY :
                    await self.send_cs(json_data['target'], json_data)

        else:
            match json_data['message']:
                case enu.Game.CREATE : 
                    self.match_status = enu.CStatus.HOST
                    self.lobby = Lobby(self.username)
                case enu.Game.JOIN: 
                    self.match_status = enu.CStatus.GUEST

    # BOTH
    async def game_invite(self, data):
        self.invitations.add(data['author'])
        await self.send_json(data)

    async def game_ready(self, data):
        if self.match_status == enu.CStatus.HOST:
            self.lobby.n_ready += 1
            if self.lobby.n_ready is 2:
                # start game
                await self.send_cs(self.lobby.challenger, {"message":enu.Game.START})
            else:
                await self.send_json(json_data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    async def game_update(self, data):
        if self.match_status == enu.CStatus.HOST:
            self.gaming(data)
        elif self.match_status == enu.CStatus.GUEST:
            await self.send_json(data)

    # HOST ONLY
    async def game_quit(self, data):
        self.lobby.challenger = None
        self.lobby.n_ready -= 1
        await self.send_json(data)

    async def game_join(self, data):
        if self.lobby.invited(data['author']) is True:
            self.lobby.challenger = data['author']
            await self.send_cs(self.lobby.challenger, {"message":enu.Game.ACCEPTED})
            await self.send_json(data)
        else:
            await self.send_cs(data['author'], {"message":enu.Game.DENY})

    # GUEST ONLY
    async def game_busy(self, data):
        await self.send_json(data)

    async def game_cancel(self, data):
        self.invitations.discard(data['author'])
        await self.send_json(data)

    async def game_accepted(self, data):
        await self.send_json(data)

    async def game_kick(self, data):
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
                asyncio.create_task(loop_remote(self))
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
