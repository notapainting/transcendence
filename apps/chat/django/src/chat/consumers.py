# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import ChatGroup, ChatUser
from chat.serializer import GroupSerializer, UserSerializer, MessageSerializer, render_json
from django.core.exceptions import ObjectDoesNotExist, ValidationError

# Get an instance of a logger
import logging
logger = logging.getLogger('django')


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
        data = GroupSerializer(self.user.groups.all(), many=True, fields='id name members messages').data
        for group in data:
            self.group_list.append(group['id'])
            group['messages'] = group['messages'][:2]
        return data


    async def connect(self):

        self.user = await self.auth()
        if self.user == None:
            await self.close(code=401)
            return

        #accept connectiont to client
        await self.accept()
        logger.info("%s Connected!", self.userName)

        # send group summary
        data = await self.get_group_list()
        await self.send_json({"group.summary": data})

        # add user to channel groups
        for id in self.group_list:
            await self.channel_layer.group_add(id, self.channel_name)

        #ptit hello comme ca gratos
        for id in self.group_list:
            await self.channel_layer.group_send(id, {"type": "chat.message", "message": f"Hello {self.userName}"})


    async def disconnect(self, close_code):
        #remove user from group at disconnect
        for id in self.group_list:
            await self.channel_layer.group_discard(id, self.channel_name)

        logger.info("%s Quit...", self.userName)


    # Receive message from WebSocket
    # check event type
    #  if message
    # find to which conv message is to 
    # send it to
    # log message in db
    async def receive_json(self, text_data):


        type = text_data['type']
        if type == 'message':
            await self.channel_layer.group_send(text_data['group'], {"type": "chat_message", "message": text_data["message"]})
            ChatGroup.object.get(id=text_data['group']).chatmessage_set.create(
                author=text_data['author'],
                respond_to=text_data['respond_to'],
                body=text_data['body']
            )
        elif type == 'room':
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
            self.room_group_name = text_data["room"]
            await self.channel_layer.group_add(self.room_group_name, self.channel_name)
            await self.channel_layer.group_send(self.room_group_name, {"type": "chat_message", "message": f"{self.userName} enter the room {self.room_group_name}! Hello dear"})
        else:
            await self.send_json({'type': 'message', 'message': 'error'})


    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        logger.info(message)
        # Send message to WebSocket
        await self.send_json({"message": message})
