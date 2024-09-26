# chat/routing.py

from django.urls import  path

from chat.consumers.consumers import ChatConsumer

websocket_urlpatterns = [
    path("chat/", ChatConsumer.as_asgi()),
]
 