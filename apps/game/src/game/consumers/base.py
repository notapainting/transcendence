# game/base.py

from channels.generic.websocket import AsyncWebsocketConsumer

import game.enums as enu
import json

from logging import getLogger
logger = getLogger(__name__)

class BaseConsumer(AsyncWebsocketConsumer):
    async def dispatch(self, message):
        if message['type'] == enu.Game.RELAY:
            pass
        else:
            if hasattr(self, "username") and hasattr(self, "status"):
                print(f"{self.username} ({self.status}) received : {message}")
        try :
            await super().dispatch(message)
        except ValueError as error:
            logger.warning(error)
            await self.send_json({'type':enu.Errors.HANDLER})
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