from django.urls import path, include
from game.views import back_test_view


urlpatterns = [
	path('game/', back_test_view, name='back_test'),
]