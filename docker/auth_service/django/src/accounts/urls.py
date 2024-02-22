from django.urls import path
from accounts.views import UserCreate
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('signin/', UserCreate.as_view(), name='signup'),
	path('login/', obtain_auth_token, name='login'),
]