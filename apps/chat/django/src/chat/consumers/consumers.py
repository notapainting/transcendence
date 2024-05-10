# chat/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import DenyConnection
from rest_framework.serializers import ValidationError as DrfValidationError



from logging import getLogger
logger = getLogger('django')


import chat.serializers as ser
import chat.models as mod
import chat.enums as enu
import chat.utils.asynchonous as uas
import chat.utils.db as udb
import chat.consumers.handler as handler

from channels.db import database_sync_to_async


CONTACT_ALL = 'contacts blockeds blocked_by invitations invited_by'



class ChatConsumer(AsyncJsonWebsocketConsumer):

    group_list = []
    contact_list = []
    user = None

    async def connect(self):
        self.user = await udb.auth(self.scope['cookies'].get('userName'))

        #accept connectiont to client
        subprotocol = self.scope.get('subprotocol')
        await self.accept(subprotocol)
        logger.info("%s Connected!", self.user.name)

        # send group summary
        self.group_list, group_summary = await udb.get_group_summary(self.user)
        await self.send_json(group_summary)

        # add user to channel groups,
        await self.channel_layer.group_add(self.user.name, self.channel_name)#attention au name
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

        #  send status, fetch status

        for contact in await udb.get_contact_list(self.user):
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"o"}})
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.FETCH, "data":{"author":self.user.name}})

    async def disconnect(self, close_code):
        if self.user is None: #change to hasattr
            return
        for id in self.group_list:
            await self.channel_layer.group_discard(id, self.channel_name)

        for contact in await udb.get_contact_list(self.user):
            await self.channel_layer.group_send(id, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"d"}})
        await self.channel_layer.group_discard(self.user.name, self.channel_name)
        logger.info("%s Quit...", self.user.name)

    async def dispatch(self, message):
        logger.info(f"msg type : {message['type']}")
        await super().dispatch(message)


    

# contact -> username !! selfgroups ?? 
    async def client_event_handler(self, type, data):
        ms = {}
        ms['type'] = type
        ms['data'] = data
        if type == enu.Event.Message.TEXT:
            await self.channel_layer.group_send(ms['data']['group'], ms)
        elif type == enu.Event.Message.FETCH:
            pass
        elif type == enu.Event.Message.GAME:
            pass
        elif type ==  enu.Event.Status.UPDATE:
            for contact in await udb.get_contact_list(self.user):
                await self.channel_layer.group_send(contact, ms)
                await self.channel_layer.group_send(self.user.name, ms)
        elif type ==  enu.Event.Status.FETCH:
            pass
        elif type ==  enu.Event.Contact.UPDATE:
            ms['data'] = await handler.contact_handler(self.user, ms['data'])
            await self.send_json(ms)
            await self.channel_layer.group_send(ms['data']['name'], ms)
        elif type == enu.Event.Group.CREATE:
            await handler.group_create_handler(self.user, ms['data'])
        elif type == enu.Event.Group.CREATE_PRIVATE:
            ms['type'] = enu.Event.Group.UPDATE
            target, ms['data'] = await handler.group_create_private_handler(self.user, ms['data'])
            await self.channel_layer.group_send(target, ms)
        elif type == enu.Event.Group.UPDATE:
            pass


    async def receive_json(self, text_data):
        logger.info(f'text : {text_data}')
        try :
            type = await uas.validate_data(username=self.user.name, data=text_data)
            serial = await uas.get_serializer(type)
            ser_data = await udb.serializer_wrapper(serial, text_data['data'])
            await self.client_event_handler(type, ser_data)

        except DrfValidationError as e:
                logger.info(e.args[0])
                await self.send_json({"data": "fck u"})


    # Receive message from room group
    async def message_text(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def message_game(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def status_update(self, event):
        # Send message to WebSocket
        logger.info(event)
        await self.send_json(event)

    async def status_fetch(self, event):
        logger.info(event)
        await self.channel_layer.group_send(event['data']['author'], {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"o"}})

        # Send message to WebSocket
        # should send back status_update
        # await self.send_json(event)

    async def contact_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def group_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)
