# chat/urls.py
from django.urls import path

from . import views
from .views import UserApiView
from .views import ContactApiView

urlpatterns = [
    path("user/list", UserApiView.list_user),
    path("user/list/<opt>", UserApiView.list_user),

    path("user/<id>", UserApiView.as_view()),


    # path("user/<id>/contact/<target>", views.contact_add),
    # path("user/<id>/contact/<target>", views.contact_add),
    # path("user/<id>/remove/<target>", views.contact_remove)
]

# contact add/del
# user/<id>/contact/<target> POST/DELETE
# user/<id>/block/<target> POST/DELETE

# conv create/del/update
# group/create
# group/delete

# group/<id>/add/<uid>
# group/<id>/remove/<uid>
