# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncJsonWebsocketConsumer

from chat.models import ChatGroup, ChatUser

# Get an instance of a logger
import logging
logger = logging.getLogger('django')


from . import models


#add :
# a way to add/del someone in contact list
# a way to sent message to a conv (someone)

class ChatConsumer(AsyncJsonWebsocketConsumer):

    # get from db conv list
    # group_add cs to conv (group)
    # send to cl chat history
    # limit to 10 old conv/active user
    # test active user : db/ping cs, middleware list, auth ?
    async def connect(self):
        #"auth"
        self.userName = self.scope['cookies'].get('userName')
        user = ChatUser.object.get(self.userName)
        if user == None:
            await self.close(code=401)
        
        #connect to group and load group history
        for group in user.groups.all():
            chat_history = group.message.all().order_by("-date_save")[:2].__str__() #last 10 or last 20? unread
            await self.send_json({"history": chat_history})
            await self.channel_layer.group_add(group.id, self.channel_name)


        #accept connectiont to client when everythings is good
        await self.accept()
        logger.info("%s Connected!", self.userName)

        #ptit hello comme ca gratos
        for group in user.groups.all():
            await self.channel_layer.group_send(group.name, {"type": "chat_message", "message": f"Hello {self.userName}"})
        

    async def disconnect(self, close_code):
        #remove user from group at disconnect
        for group in user.groups.all():
            await self.channel_layer.group_discard(group.id, self.channel_name)

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
