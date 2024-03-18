from django.urls import path, include
from game.views import back_test_view, start_game_view, launch_ball_view


urlpatterns = [
	path('api-game/game/', back_test_view, name='back_test'),
	path('api-game/launch-ball/', launch_ball_view, name='launch_ball'),
	path('start-game/', start_game_view, name='start_game'),
]