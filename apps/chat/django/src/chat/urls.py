# chat/urls.py
from django.urls import path

from . import views
from .views import UserApiView
from .views import ContactApiView

urlpatterns = [
    path("users", UserApiView.list_user),
    path("users/list/<opt>", UserApiView.list_user),

    path("users/<id>", UserApiView.as_view()),


    path("users/<id>/contacts", ContactApiView.as_view()),
    path("users/<id>/contacts/<target>", ContactApiView.as_view()),
    # path("users/<id>/block/<target>", ContactApiView.as_view()),
]

# contact add/del
# users/<id>/contact/<target> POST/DELETE
# users/<id>/block/<target> POST/DELETE
# users/<id>/conv/<target> POST/DELETE

# conv create/del/update
# group/create
# group/delete

# group/<id>/add/<uid>
# group/<id>/remove/<uid>
