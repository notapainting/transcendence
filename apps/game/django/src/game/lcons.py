import json, asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

from game.consumers import GameState, loop

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
            await self.send_json({'type':enu.Event.Errors.TYPE})
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
        logger.info('bytes received')


    async def error_decode(self, data):
        logger.info(data)

    async def error_encode(self, data):
        logger.info(data)




class Gamer(BaseConsumer):

    game = enu.CStatus.IDLE
    game_lobby = None
    tounament = enu.CStatus.IDLE
    username = "Anon"

    async def connect(self):
        # self.game_state = GameState()
        self.username = self.scope.get('user', 'Anon')
        if self.username is None:
            raise exchan.DenyConnection()


        await self.accept()
        await self.channel_layer.group_add(self.channel_name, self.username)
        await self.send(self.game_state.to_dict('none'))

    async def disconnect(self, close_code):
        del self.game_state

    async def receive_json(self, json_data):
        message = json_data.get('message', None)
        if message is not None:
            return await self.gaming()

        key = json_data['type']
        json_data['author'] = self.username
        match key:
            case enu.Game.CREATE: await self.create_game(json_data)
            case enu.Game.QUIT : await self.game_quit(json_data)
            case enu.Game.INVITE : await self.game_invite(json_data)
            case enu.Game.JOIN : await self.game_join(json_data)
            # case enu.Game.READY : await self.game_join(json_data)

    async def game_create(self, data):
        """
        put consumer in host mode
        create a gamestate and a lobby
        """
        if self.game == enu.CStatus.IDLE:
            self.game = enu.CStatus.HOST
            self.game_state = GameState()
            self.game_lobby = Lobby(self.username)
        else:
            raise RuntimeError(f"can't create game, already in lobby as {self.game}")

    async def game_quit(self, data):
        if self.game == enu.CStatus.HOST:
            for user in self.game_lobby.invitation_list:
                await self.channel_layer.send(user, {"type":"game.deny"})
            if self.game_lobby.challenger is not None:
                await self.channel_layer.send(self.game_lobby.challenger, {"type":"game.deny"})
            del self.game_state
            del self.game_lobby
        elif self.game == enu.CStatus.JOIN:
            pass

    async def game_invite(self, data):
        """
        if consumer is host, send a game invite to target
        if consumer is idle or in game, forward game invite to front 
        """
        if self.game == enu.CStatus.HOST:
            self.game_lobby.invite(data['data'])
            await self.channel_layer.send(data['data'], data)
        else:
            await self.send(data)

    async def game_join(self, data):
        if self.game == enu.CStatus.HOST:
            if self.game_lobby.challenger is None:
                self.game_lobby.challenger = data['author']
                await self.send(data)
                for user in self.game_lobby.invitation_list:
                    await self.channel_layer.send(user, {"type":"game.deny"})
                self.game_lobby.invitation_list.clear()
            else:
                await self.channel_layer.send(data['author'], {"type":"game.deny"})
        else :
            await self.channel_layer.send(data['author'], data)


    async def game_update(self, data):
        await self.send(self.game_state.to_dict('none'))



    async def gaming(self, text_data):
        global game_running, upPressed, downPressed, wPressed, sPressed
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if message == "startButton":
            if self.game_state.status['game_running'] == False :
                self.game_state.status['game_running'] = True
                asyncio.create_task(loop(self))
        elif message == "bonus":
            self.game_state.status['randB'] = text_data_json["bonus"]

        else :
            asyncio.create_task(self.game_state.update_player_position(message))
