# chat/urls.py
from django.urls import path, include


from .views import UserApiView, UserContactApiView, UserBlockedApiView
from .GroupView import GroupApiView

urls_user = [
    path("", UserApiView.as_view()),
    path("<id>/", UserApiView.as_view()),

    path("<id>/contacts/", UserContactApiView.as_view()),
    path("<id>/contacts/<target>/", UserContactApiView.as_view()),

    path("<id>/blockeds/", UserBlockedApiView.as_view()),
    path("<id>/blockeds/<target>/", UserBlockedApiView.as_view()),
]

urls_group = [
    path("", GroupApiView.as_view()),
    path("<uuid:gid>/", GroupApiView.as_view()),

    path("<uuid:gid>/members/", GroupApiView.as_view()),
    path("<uuid:gid>/members/<uuid:uid>/", GroupApiView.as_view()), # -> redirect to /users/mid

    path("<uuid:gid>/message", GroupApiView.as_view()),
    path("<uuid:gid>/message/<uuid:mid>/", GroupApiView.as_view()), # -> redirect to /message/mid
]

urls_message = [
    # path("", MessageApiView.as_view()),
    # path("<uuid:gid>", MessageApiView.as_view()), -> return message data (author/date/group/body)
    # path("<uuid:gid>/body/", MessageApiView.as_view()), -> return message body

    # path("<uuid:gid>/author/", MessageApiView.as_view()),  -> redirect to /users/mid
    # path("<uuid:gid>/conv/", MessageApiView.as_view()), -> redirect to /groups/mid

]

urlspatterns = [
    path('users/', include(urls_user)),
    path('groups/', include(urls_group))
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

# group/<id>/add/<uid>
# group/<id>/remove/<uid>
