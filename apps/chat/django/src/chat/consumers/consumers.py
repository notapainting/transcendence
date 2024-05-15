# chat/consumers/consumers.py

from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.core.exceptions import ObjectDoesNotExist
from channels.exceptions import DenyConnection
from rest_framework.serializers import ValidationError as DrfValidationError

import chat.enums as enu
import chat.consumers.utils as cuti


from logging import getLogger
logger = getLogger('django')

CONTACT_ALL = 'contacts blockeds blocked_by invitations invited_by'


class ChatConsumer(AsyncJsonWebsocketConsumer):

    group_list = []
    contact_list = []

    async def connect(self):
        self.user = self.scope['user']
        if self.user is None:
            raise DenyConnection()

        #accept connectiont to client
        subprotocol = self.scope.get('subprotocol')
        await self.accept(subprotocol)
        logger.info("%s Connected!", self.user.name)

        self.group_list = await cuti.get_group_list(self.user)
        self.contact_list = await cuti.get_contact_list(self.user)

        print(f"clist {self.contact_list}")
        print(f"glist {self.group_list}")
        # send group summary
        group_summary = await cuti.get_group_summary(self.user, n_messages=2)
        await self.send_json(group_summary)

        # send contact summary
        contact_summary = await cuti.get_contact_summary(self.user)
        await self.send_json(contact_summary)


        # add user to channel groups,
        await self.channel_layer.group_add(self.user.name, self.channel_name)#attention au name
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

        #  send status, fetch status
        for contact in await cuti.get_contact_list(self.user):
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"o"}})
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.FETCH, "data":{"author":self.user.name}})

    async def disconnect(self, close_code):
        if self.user is None: #change to hasattr
            return

        for id in await cuti.get_group_list(self.user):
            await self.channel_layer.group_discard(id, self.channel_name)

        for contact in await cuti.get_contact_list(self.user):
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"d"}})
        await self.channel_layer.group_discard(self.user.name, self.channel_name)
        logger.info("%s Quit...", self.user.name)

    async def dispatch(self, message):
        logger.info(f"msg type : {message['type']}")
        await super().dispatch(message)


    async def send_back(self, type, data):
        targets, event = await cuti.get_targets(self.user, type, data)

        if targets[0] == enu.Self.LOCAL:
            local = targets.pop(0)
            await self.send_json(event)
        for target in targets:
            await self.channel_layer.group_send(target, event)


    async def receive_json(self, text_data):
        # logger.info(f'text : {text_data}')
        try :
            type = await cuti.validate_data(username=self.user.name, data=text_data)
            serial = await cuti.get_serializer(type)
            ser_data = await cuti.serializer_wrapper(serial, text_data['data'])
            await self.send_back(type, ser_data)

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

    async def message_read(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def status_update(self, event):
        # Send message to WebSocket
        logger.info(event)
        await self.send_json(event)

    async def status_fetch(self, event):
        logger.info(event)
        await self.channel_layer.group_send(event['data']['author'], {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"o"}})


    async def contact_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def group_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)
