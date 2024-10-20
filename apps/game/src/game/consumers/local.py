# game/consumers/local.py

import channels.exceptions as exchan


import game.enums as enu
from game.plaza import plaza, PlazaNotFound
from game.consumers.base import BaseConsumer
from game.lobby import getDefault, LocalTournament, LobbyException
from game.gamestate import getDefaultState

from logging import getLogger
logger = getLogger('base')

CHAN_EXCEPT = (exchan.AcceptConnection, exchan.DenyConnection,exchan.StopConsumer)

class LocalConsumer(BaseConsumer):
    async def dispatch(self, message):
        try :
            await super().dispatch(message)
        except LobbyException as error:
            logger.info(error)
            await self.send_json({'type':enu.Errors.DATA,'error':enu.Errors.LOBBY})
        except PlazaNotFound:
            await self.send_json({'type':enu.Errors.DATA, 'error':enu.Errors.NTF_404})
        except CHAN_EXCEPT:
            raise
        except BaseException as error:
            logger.info(f"ERROR: {self.username} ({self.status}): {error}")

    
    async def connect(self):
        await self.accept()
        self.username = 'Loyal'
        self.lobby = LocalTournament(host="Loyal", host_channel_name=self.channel_name)
        await self.lobby._init()
        await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault(), "state":getDefaultState()})
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
                await self.send_json({"type":enu.Game.DEFAULT, "message":getDefault(), "state":getDefaultState()})
            case enu.Game.SETTING:
                self.lobby.changeSettings(data['message'])
                await self.send_json({"type":enu.Game.SETTING, "message":self.lobby.getSettings(), "state":getDefaultState()})
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
                logger.warning(f"local bad type")

    async def game_relay(self, data):
        await self.send_json(data["relay"])

    async def match_end(self, data):
        logger.info(f"data: {data}")
        await self.send_json(data)
        if hasattr(self, "lobby"):
            await self.lobby.update_result(data)

    async def tournament_end(self, data):
        await self.send_json(data)

