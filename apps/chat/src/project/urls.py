# projet/urls.py

from django.http import HttpResponse
from django.urls import path, include
from chat.urls import urls
import logging

def my_view(request):
    logging.debug('Debug message')
    logging.info('Info message')
    logging.warning('Warning message')
    logging.error('Error message')
    logging.critical('Critical message')
    return HttpResponse("Logging test")

urlpatterns = [
    path('api/', view=include(urls)),
    path('log/', my_view),
]

