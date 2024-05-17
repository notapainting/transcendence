# projet/urls.py

from http.client import HTTPResponse
from django.urls import path, include
from chat.urls import urls
import logging

def my_view(request):
    logging.debug('Debug message')
    logging.info('Info message')
    logging.warning('Warning message')
    logging.error('Error message')
    logging.critical('Critical message')
    return HTTPResponse("Logging test")

urlpatterns = [
    path('api/', view=include(urls)),
    path('log/', my_view),
]

