from django.urls import path, include
from game.views import back_test_view, start_game_view, paddle_view


urlpatterns = [
	path('api-game/game/', back_test_view, name='back_test'),
	path('api-game/paddle/', paddle_view, name='paddle'),
	path('start-game/', start_game_view, name='start_game'),
]