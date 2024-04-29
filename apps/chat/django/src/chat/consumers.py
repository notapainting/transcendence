# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError
# Get an instance of a logger
import logging
logger = logging.getLogger('django')
from channels.exceptions import DenyConnection

from . import models

import chat.serializer as ser
import chat.models as mod

from channels.db import database_sync_to_async

    # get from db conv list
    # group_add cs to conv (group)
    # send to cl chat history
    # limit to 10 old conv/active user
    # test active user : db/ping cs, middleware list, auth ?

# handle db errors
# @database_sync_to_async
# def handle_message(username, data):
#     ser = get_serializer('chat.message')
#     ms = ser(data=data, author=username)
#     ms.is_valid(raise_exception=True)
#     ms.create(ms.validated_data)
#     return ms.data

EVENT_DOWN_TYPE = ['group.summary', 'group.update', 'contact.summary', 'contact.update', 'chat.message']
EVENT_CLIENT_TYPE = ['group.update', 'contact.update', 'status.update', 'chat.message']


async def get_serializer(type):
    serializers = {
        'chat.message' : ser.ChatMessage,
        'contact.update' : ser.EventContact,
        'status.update' : ser.EventStatus,
    }
    return serializers[type]



@database_sync_to_async
def serializer_handler(serializer, data):
    ser = serializer(data=data)
    ser.is_valid(raise_exception=True)
    ser.create(ser.validated_data)
    return ser.data


async def validate_data(username, data):
    type = data.get('type', None)
    data = data.get('data', None)
    if type is None or data is None:
        raise ValidationError("invalid event")
    data['author'] = username
    if type in EVENT_CLIENT_TYPE:
        return type
    else:
        raise ValidationError(f"event type unknow : {type}")

class ChatConsumer(AsyncJsonWebsocketConsumer):

    group_list = []

    @database_sync_to_async
    def auth(self):
        self.userName = self.scope['cookies'].get('userName')
        try:
            return mod.ChatUser.objects.get(name=self.userName)
        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def get_group_list(self):
        data = {}
        data['type'] = 'group.summary'
        data['data'] = ser.ChatGroup(self.user.groups.all(), 
                               many=True, 
                               fields='id name members messages'
                               ).data
        for group in data['data']:
            self.group_list.append(group['id'])
            group['messages'] = group['messages'][:2]
        return data


    async def connect(self):
        self.user = await self.auth()
        if self.user == None:
            raise DenyConnection
        #accept connectiont to client
        subprotocol = self.scope.get('subprotocol')
        await self.accept(subprotocol)
        logger.info("%s Connected!", self.userName)

        # send group summary
        data = await self.get_group_list()
        await self.send_json(data)

        # add user to channel groups
        await self.channel_layer.group_add(self.userName, self.channel_name)
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

    async def disconnect(self, close_code):
        for id in self.group_list:
            await self.channel_layer.group_discard(id, self.channel_name)
        logger.info("%s Quit...", self.userName)


    async def dispatch(self, message):
        print(f'msg type : {message['type']}')
        await super().dispatch(message)

    # Receive message from WebSocket
    # check event type
    #  if message
    # find to which conv message is to 
    # send it to
    # log message in db

    @database_sync_to_async
    def get_contact_list(self):
        contacts = ser.ChatUser(self.user).data['contacts']
        return contacts

    @database_sync_to_async
    def contact_handler(self, data):
        try :
            if data['rel'] == 'contact':#add invitation system
                if data['op'] == 'add':
                    t = mod.ChatUser.objects.get(name=data['name'])
                    self.user.contacts.add(t)
                elif data['op'] == 'remove':
                    t = self.user.contacts.get(name=data['name'])
                    self.user.contacts.remove(t)

            elif data['rel'] == 'block':
                if data['op'] == 'add':
                    t = mod.ChatUser.objects.get(name=data['name'])
                    self.user.blockes.add(t)
                elif data['op'] == 'remove':
                    t = self.user.blockeds.get(name=data['name'])
                    self.user.blockeds.remove(t)
            return True
        except ObjectDoesNotExist:
            return False

# contact -> username !! selfgroups ?? 
    async def event_handler(self, type, data):
        ms = {}
        ms['type'] = type
        ms['data'] = data
        print(ms)
        if type == 'chat.message':
            await self.channel_layer.group_send(ms['data']['group'], ms)
        elif type == 'status.update':
            contacts = await self.get_contact_list();
            for contact in contacts:
                print(contact)
                await self.channel_layer.group_send(contact, ms)
        elif type == 'contact.update':
            if await self.contact_handler(ms['data']) is True:
                await self.send_json(ms)


    async def receive_json(self, text_data):
        print(f'text : {text_data}')
        try :
            type = await validate_data(username=self.userName, data=text_data)
            serial = await get_serializer(type)
            ser_data = await serializer_handler(serial, text_data['data'])
            await self.event_handler(type, ser_data)

        except ValidationError as e:
                print(e.args[0])
                await self.send_json({"message": "fck u"})


    # Receive message from room group
    async def chat_message(self, event):
        # Send message to WebSocket
        await self.send_json(event)

    async def status_update(self, event):
        # Send message to WebSocket
        await self.send_json(event)
