# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import ChatGroup, ChatUser
from chat.serializer import ChatGroupSerializer, ChatUserSerializer, ChatMessageSerializer, render_json, EventSerializer,MessageEventSerializer
from django.core.exceptions import ObjectDoesNotExist
from rest_framework.serializers import ValidationError
# Get an instance of a logger
import logging
logger = logging.getLogger('django')
from channels.exceptions import DenyConnection

from . import models

# c = ChatGroup.objects.get(id='edc6e65a-65bd-4eb7-8d99-832410c54965').messages.all()[:3]
# m = ms(c, many=True)
# m.data -> [OrdreDcit]

from channels.db import database_sync_to_async

    # get from db conv list
    # group_add cs to conv (group)
    # send to cl chat history
    # limit to 10 old conv/active user
    # test active user : db/ping cs, middleware list, auth ?

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
        data = ChatGroupSerializer(self.user.groups.all(), 
                               many=True, 
                               fields='id name members messages'
                               ).data
        for group in data:
            self.group_list.append(group['id'])
            group['messages'] = group['messages'][:2]
        data.insert(0, {'type': 'group.summary'})
        return data


    async def connect(self):
        self.user = await self.auth()
        if self.user == None:
            raise DenyConnection
            # await self.close(code=401)
            # return

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

        # #ptit hello comme ca gratos
        # for id in self.group_list:
        #     await self.channel_layer.group_send(id, {"type": "chat.message", "message": f"Hello {self.userName}"})


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

    # handle db errors
    @database_sync_to_async
    def handle_message(self, data):
        data['author'] = self.userName
        ms = ChatMessageSerializer(data=data)
        ms.is_valid(raise_exception=True)
        print("mssss")
        print(ms.data)
        ms.create(ms.validated_data)

    async def receive_json(self, text_data):
        se = EventSerializer(data=text_data)
        try :
            se.is_valid(raise_exception=True)
            print("sedata")
            print(se.data['data'])
            if se.validated_data['type'] == 'chat.message':
                await self.handle_message(se.validated_data['data'])
                await self.channel_layer.group_send(se.data['data']['group'], se.data)


        except ValidationError as e:
                print(e.args[0])
                await self.send_json({"message": "fck u"})





    # Receive message from room group
    async def chat_message(self, event):
        # logger.info(event)
        message = event

        # Send message to WebSocket
        await self.send_json({"message": message})
