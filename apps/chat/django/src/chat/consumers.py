# chat/consumers.py
import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import AsyncWebsocketConsumer

# from urllib.parse import parse_qsl
from requests.structures import CaseInsensitiveDict



import logging
# Get an instance of a logger
logger = logging.getLogger('django')


# use cookiemiddleware for cookie -> scope['cookie']
class ChatConsumer(AsyncWebsocketConsumer):
    userName = "Anonymous"

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = "chat_%s" % self.room_name
        # dictQuery = parse_qsl(self.scope["query_string"].decode('utf-8'))
        # self.userName = dictQuery[0][1]
        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        raw = dict(self.scope['headers'])[b'cookie'].decode()
        test = CaseInsensitiveDict(i.split('=', 1) for i in raw.split('; '))
        self.userName = test.get('username', 'Anon')
        logger.info("%s Connected!", self.userName)
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)
        logger.info("%s Quit...", self.userName)



    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]

        # Send message to room group
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat_message", "message": message})

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]

        # Send message to WebSocket
        logger.info(message)
        await self.send(text_data=json.dumps({"message": message}))