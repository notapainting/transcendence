# chat/urls.py
from django.urls import path

from . import views


urlpatterns = [
    path("user/list", views.list_user),
    path("user/list/<opt>", views.list_user),

    path("user/create", views.create_user),
    path("user/create/<id>", views.create_user),
    path("user/delete/<id>", views.delete_user),

    path("user/id/<id>", views.get_user_by_id),
    path("user/<name>", views.get_user_by_name),
	
    path("user/<id>/contact/<target>", views.contact_add)
]

# contact add/del
# user/<id>/contact/<target> POST/DELETE
# user/<id>/block/<target> POST/DELETE

# conv create/del/update
# group/create
# group/delete

# group/<id>/add/<uid>
# group/<id>/remove/<uid>
