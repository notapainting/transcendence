# game/consumers/local.py

import random, asyncio
import game.enums as enu

from game.consumers.base import BaseConsumer
from game.lobby import getDefault, LocalTournament, LobbyException

from logging import getLogger
logger = getLogger('base')

class LocalConsumer(BaseConsumer):
    async def dispatch(self, message):
        try :
            await super().dispatch(message)
        except LobbyException as error:
            await self.send_json({'error':enu.Errors.LOBBY})
        except BaseException:
            raise 
    
    async def connect(self):
        await self.accept()
        self.username = 'Loyal'
        self.lobby = LocalTournament(host="Loyal", host_channel_name=self.channel_name)
        await self.lobby._init()
        await self.send_json({"type":enu.Game.SETTING, "message":getDefault()})
        self.status = enu.Game.LOCAL
        logger.info(f"JOIN: {self.username} ({self.status})")

    async def disconnect(self, close_code):
        await self.lobby.end()
        logger.info(f"QUIT: {self.username} ({self.status})")

    async def receive_json(self, json_data):
        await self.local(json_data)

    async def local(self, data):
        match data['type']:
            case enu.Game.DEFAULT:
                await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault()})
            case enu.Game.SETTING:
                self.lobby.changeSettings(data['message'])
            case enu.Game.START:
                await self.lobby.start(data['players'])
            case enu.Game.READY:
                await self.lobby.match_start()
            case enu.Match.UPDATE:
                await self.lobby.match_feed(data)
            case enu.Match.PAUSE:
                await self.lobby.match_pause()
            case enu.Game.NEXT:
                await self.lobby.next()
            case enu.Game.QUIT:
                await self.lobby.end()
            case _:
                logger.warn(f"local bad type")

    async def game_relay(self, data):
        await self.send_json(data["relay"])

    async def match_end(self, data):
        await self.send_json(data)
        if hasattr(self, "lobby"):
            await self.lobby.update_result(data)


