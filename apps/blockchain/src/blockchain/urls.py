# projet/urls.py

from django.http import HttpResponse
from django.urls import path
import logging
from . import views

def my_view(request):
    logging.debug('Debug message')
    logging.info('Info message')
    logging.warning('Warning message')
    logging.error('Error message')
    logging.critical('Critical message')
    return HttpResponse("Logging test")

urlpatterns = [
    path('log/', my_view),
    path('register_match/', views.register_match, name='register_match'),
]

