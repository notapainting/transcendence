# chat/consumers/consumers.py

from channels.generic.websocket import  AsyncWebsocketConsumer

import channels.exceptions as exchan
from rest_framework.exceptions import APIException

import chat.enums as enu
import chat.models as mod
import chat.consumers.utils as cuti
import json

from logging import getLogger
logger = getLogger('base')

CONTACT_ALL = 'contacts blockeds blocked_by invitations invited_by'
CHAN_EXCEPT = (exchan.AcceptConnection, exchan.DenyConnection,exchan.StopConsumer)


class BaseConsumer(AsyncWebsocketConsumer):
    async def dispatch(self, message):
        try :
            await super().dispatch(message)
        except ValueError as error:
            logger.warning(error)
            await self.send_json({'type':enu.Event.Errors.HANDLER})
        except CHAN_EXCEPT:
            raise
        except BaseException as error:
            logger.info(f"ERROR: {self.username} ({self.status}): {error}")
            await self.send_json({'type':enu.Event.Errors.DATA})

    @classmethod
    async def decode_json(cls, text_data):
        try :
            return json.loads(text_data)
        except:
            return {'type':enu.Event.Errors.DECODE}

    @classmethod
    async def encode_json(cls, content):
        try:
            return json.dumps(content)
        except BaseException as e:
            logger.debug(e)
            return json.dumps({'type':enu.Event.Errors.ENCODE})

    async def send_json(self, content, close=False):
        await super().send(text_data=await self.encode_json(content), close=close)


    async def websocket_receive(self, message):
        if "text" in message:
            await self.receive_json(json_data=await self.decode_json(message["text"]))
        else:
            await self.receive_bytes(bytes_data=message["bytes"])

    async def receive_json(self, bytes_data, **kwargs):
        pass

    async def receive_bytes(self, bytes_data, **kwargs):
        logger.info('bytes received')


    async def error_decode(self, data):
        logger.info(data)

    async def error_encode(self, data):
        logger.info(data)


class ChatConsumer(BaseConsumer):
    async def connect(self):
        self.user = self.scope['user']
        if self.user is None:
            raise exchan.DenyConnection()

        #accept connectiont to client
        await self.accept(self.scope.get('subprotocol', None))
        logger.info("%s Connected!", self.user.name)

        await self.send_json(await cuti.get_group_summary(self.user))
        await self.send_json(await cuti.get_contact_summary(self.user))

        await self.channel_layer.group_add(self.user.name, self.channel_name)

        # add user to channel groups
        self.group_list = await cuti.get_group_list(self.user)
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

        #  send status, fetch status
        self.contact_list = await cuti.get_contact_list(self.user)
        for contact in self.contact_list :
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":mod.User.Status.ONLINE}})
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.FETCH, "data":{"author":self.user.name}})

    async def disconnect(self, close_code):
        if self.user is None: #change to hasattr
            return

        for id in await cuti.get_group_list(self.user):
            await self.channel_layer.group_discard(id, self.channel_name)

        for contact in await cuti.get_contact_list(self.user):
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":mod.User.Status.DISCONNECTED}})
        await self.channel_layer.group_discard(self.user.name, self.channel_name)
        logger.info("%s Quit...", self.user.name)

    async def receive_json(self, json_data, **kwargs):
        if json_data['type'] == enu.Event.Errors.DECODE:
            await self.send_json(json_data)
            return
        try :
            type = await cuti.validate_data(username=self.user.name, data=json_data)
            serial = await cuti.get_serializer(type)
            ser_data = await cuti.serializer_wrapper(serial, json_data['data'])
            if type == enu.Event.Message.FIRST:
                targets, event = await cuti.get_targets(self.user, type, ser_data)
                self.group_list = await cuti.get_group_list(self.user)
                await self.channel_layer.group_add(ser_data['id'], self.channel_name)
            else:
                targets, event = await cuti.get_targets(self.user, type, ser_data)
        except APIException as error:
            logger.info(error)
            await self.send_json({"type": enu.Event.Errors.DATA, "code":error.status_code})
        else:
            if targets == enu.Self.LOCAL:
                await self.send_json(event)
            else:
                for target in targets:
                    await self.channel_layer.group_send(target, event)

    async def status_fetch(self, event):
        logger.info(event)
        await self.channel_layer.group_send(event['data']['author'], {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":mod.User.Status.ONLINE}})

    async def message_text(self, event):
        await self.send_json(event)

    async def message_game(self, event):
        await self.send_json(event)

    async def message_read(self, event):
        await self.send_json(event)

    async def status_update(self, event):
        await self.send_json(event)

    async def contact_update(self, event):
        self.contact_list = await cuti.get_contact_list(self.user)
        for contact in self.contact_list:
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":mod.User.Status.ONLINE}})
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.FETCH, "data":{"author":self.user.name}})
        await self.send_json(event)

    async def group_update(self, event):
        self.group_list = await cuti.get_group_list(self.user)
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)
        await self.send_json(event)

    async def group_delete(self, event):
        self.group_list = await cuti.get_group_list(self.user)
        await self.channel_layer.group_discard(event['data'], self.channel_name)
        await self.send_json(event)
