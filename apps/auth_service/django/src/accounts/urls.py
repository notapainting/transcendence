from django.urls import path
from accounts.views import UserCreate

urlpatterns = [
    path('signup/', UserCreate.as_view(), name='signup'),
]