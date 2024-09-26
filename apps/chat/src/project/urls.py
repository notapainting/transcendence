# projet/urls.py

from django.urls import path, include
from chat.urls import urls


urlpatterns = [
    path('api/', view=include(urls)),
]

