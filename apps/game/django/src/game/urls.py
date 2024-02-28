from django.urls import path, include
from game.views import back_test_view, start_game_view


urlpatterns = [
	path('game/', back_test_view, name='back_test'),
	path('start-game/', start_game_view, name='start_game'),
]