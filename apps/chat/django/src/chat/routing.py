# chat/routing.py
from django.urls import re_path, path

from chat.consumers.consumers import ChatConsumer

websocket_urlpatterns = [
    re_path(r"ws/chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    re_path(r"chat/(?P<room_name>\w+)/$", ChatConsumer.as_asgi()),
    path("chat/", ChatConsumer.as_asgi()),
]
