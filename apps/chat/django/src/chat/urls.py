# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("user/create", views.create_user),
    path("user/delete", views.delete_user),
]