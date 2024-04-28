# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import ChatGroup, ChatUser
from chat.serializer import ChatGroupSerializer, ChatUserSerializer, ChatMessageSerializer, render_json
from chat.serializer import ContactEventSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError
# Get an instance of a logger
import logging
logger = logging.getLogger('django')
from channels.exceptions import DenyConnection

from . import models


from channels.db import database_sync_to_async

    # get from db conv list
    # group_add cs to conv (group)
    # send to cl chat history
    # limit to 10 old conv/active user
    # test active user : db/ping cs, middleware list, auth ?


EVENT_DOWN_TYPE = ['group.summary', 'group.update', 'contact.summary', 'contact.update', 'chat.message']
EVENT_CLIENT_TYPE = ['group.update', 'contact.update', 'chat.message']

# @database_sync_to_async
def get_serializer(type):
    serializers = {
        'chat.message' : ChatMessageSerializer,
        'contact.update' : ContactEventSerializer,
    }
    return serializers[type]

# handle db errors
# @database_sync_to_async
# def handle_message(username, data):
#     ser = get_serializer('chat.message')
#     ms = ser(data=data, author=username)
#     ms.is_valid(raise_exception=True)
#     ms.create(ms.validated_data)
#     return ms.data

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
    if type not in EVENT_CLIENT_TYPE:
        raise ValidationError("event type unknow")
    else:
        return type, get_serializer(type)

class ChatConsumer(AsyncJsonWebsocketConsumer):

    group_list = []

    @database_sync_to_async
    def auth(self):
        self.userName = self.scope['cookies'].get('userName')
        try:
            return ChatUser.objects.get(name=self.userName)
        except ObjectDoesNotExist:
            return None

    @database_sync_to_async
    def get_group_list(self):
        data = {}
        data['type'] = 'group.summary'
        data['data'] = ChatGroupSerializer(self.user.groups.all(), 
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
        ser = ChatUserSerializer(self.user).data['contact']


# contact -> username !! selfgroups ?? 
    async def event_handler(self, type, data):
        ms = {}
        ms['type'] = type
        ms['data'] = data
        print(ms)
        if type == 'chat.message':
            await self.channel_layer.group_send(ms['data']['group'], ms)
        elif type == 'contact.update':
            if ms['data']['name'] == 'self':
                contacts = self.get_contact_list();
                async for contact in contacts:
                    await self.channel_layer.group_send(contact, ms)

    async def receive_json(self, text_data):

        print(f'text : {text_data}')
        try :
            type, ser = await validate_data(username=self.userName, data=text_data)
            ser_data = await serializer_handler(ser, text_data['data'])
            await self.event_handler(type, ser_data)

        except ValidationError as e:
                print(e.args[0])
                await self.send_json({"message": "fck u"})


    # Receive message from room group
    async def chat_message(self, event):
        # logger.info(event)
        message = event

        # Send message to WebSocket
        await self.send_json(event)
