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

        # send group summary
        self.group_list, group_summary = await cuti.get_group_summary(self.user)
        await self.send_json(group_summary)

        # send contact summary
        self.contact_list = await cuti.get_contact_list(self.user)
        contact_summary = await cuti.get_contact_list(self.user, fields='contacts blockeds blocked_by invitations invited_by')
        print(contact_summary)
        await self.send_json(contact_summary)


        # add user to channel groups,
        await self.channel_layer.group_add(self.user.name, self.channel_name)#attention au name
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

        #  send status, fetch status
        for contact in  self.contact_list:
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"o"}})
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.FETCH, "data":{"author":self.user.name}})

    async def disconnect(self, close_code):
        if self.user is None: #change to hasattr
            return
        for id in self.group_list:
            await self.channel_layer.group_discard(id, self.channel_name)

        for contact in await cuti.get_contact_list(self.user):
            await self.channel_layer.group_send(contact, {"type":enu.Event.Status.UPDATE, "data":{"author":self.user.name,"status":"d"}})
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
            targets = [ms['data']['group']]
        elif type == enu.Event.Message.FIRST:
            targets = ms["data"]["members"]
        elif type == enu.Event.Message.FETCH:
            print(ms['data'])
            await self.send_json(ms)
            targets = 'self.local'
            return
        elif type == enu.Event.Message.GAME:
            await self.send_json(ms)
            targets = 'self.local, cible'
            return
        elif type == enu.Event.Status.UPDATE:
            targets = cuti.get_contact_list(self.user) + [self.user.name]
        elif type == enu.Event.Contact.UPDATE:
            targets = [self.user.name, ms['data']['name']]
        elif type in enu.Event.Group.values:
            ms['type'] = enu.Event.Group.UPDATE
            targets = ms["data"]["owner"] + ms["data"]["members"] + ms["data"]["admins"] + ms["data"]["restricts"]

        for target in targets:
            await self.channel_layer.group_send(target, ms)


    async def receive_json(self, text_data):
        # logger.info(f'text : {text_data}')
        try :
            type = await cuti.validate_data(username=self.user.name, data=text_data)
            serial = await cuti.get_serializer(type)
            ser_data = await cuti.serializer_wrapper(serial, text_data['data'])
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
