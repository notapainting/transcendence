# chat/urls.py

from django.urls import path, include

from chat.views.UserViews import UserApiView
from chat.views.GroupView import GroupApiView
from chat.views.MessageView import MessageApiView
from chat.views.SpecialView import RelationApiView

urls_user = [
    path("", UserApiView.as_view()),
    path("<name>/", UserApiView.as_view()),
]

urls_group = [
    path("", GroupApiView.as_view()),
    path("<uuid:id>/", GroupApiView.as_view()),
]

urls_message = [
    path("", MessageApiView.as_view()),
    path("<uuid:id>/", MessageApiView.as_view()),
]

urls_rel = [
    path("blocked/", RelationApiView.as_view()),
]


urlspatterns = [
    path('users/', include(urls_user)),
    path('groups/', include(urls_group)),
    path('messages/', include(urls_message)),
    path('relations/', include(urls_rel)),
]

urls = [
    path('v1/', include(urlspatterns))
]

