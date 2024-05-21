"""
URL configuration for user_managment project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from user_managment.views import UserCreate, GetUserInfos, UpdateClientInfo, MatchsInfos, UserMatchsInfos
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
	path('signup/', UserCreate.as_view(), name='signup'),
	path('getuserinfo/', GetUserInfos.as_view(), name='get-user-info'),
    path('update_client/', UpdateClientInfo.as_view(), name='get-user-info'),
    path('matchsinfos/', MatchsInfos.as_view(), name='infos-matchs'),
    path('matchsinfos/<name>/', UserMatchsInfos.as_view(), name='user-matchs'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)