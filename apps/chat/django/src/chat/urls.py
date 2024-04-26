# chat/urls.py
from django.urls import path, include
from django.views.generic.base import RedirectView 

from .UserViews import UserApiView, UserContactApiView, UserBlockedApiView
from .GroupView import GroupApiView
from .MessageView import MessageApiView

urls_user = [
    path("", UserApiView.as_view()),
    path("<name>/", UserApiView.as_view()),

    path("<id>/contacts/", UserContactApiView.as_view()),
    path("<id>/contacts/<target>/", UserContactApiView.as_view()),

    path("<id>/blockeds/", UserBlockedApiView.as_view()),
    path("<id>/blockeds/<target>/", UserBlockedApiView.as_view()),
]

urls_group = [
    path("", GroupApiView.as_view()),
    path("<uuid:id>/", GroupApiView.as_view()),
]

urls_message = [
    path("", MessageApiView.as_view()),
    # path("<uuid:id>", MessageApiView.as_view()), # -> return message data (author/date/group/body)

    # path("<uuid:id>/author/", MessageApiView.as_view()), # -> redirect to /users/id
    # path("<uuid:id>/conv/", MessageApiView.as_view()), # -> redirect to /groups/id

]

urlspatterns = [
    path('users/', include(urls_user)),
    path('groups/', include(urls_group)),
    path('messages/', include(urls_message))
]

urls = [
    path('v1/', include(urlspatterns))
]


# contact add/del
# groups/<id> POST/DELETE/GET
# users/<id>/block/<target> POST/DELETE
# users/<id>/conv/<target> POST/DELETE

# conv create/del/update
# group/create
# group/delete

# group/<id>/add/<id>
# group/<id>/remove/<id>
