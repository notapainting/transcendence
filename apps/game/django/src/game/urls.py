from django.urls import path, include
from game.views import back_test_view, start_game_view, paddle_view, ball_info


urlpatterns = [
	path('api-game/game/', back_test_view, name='back_test'),
	path('api-game/paddle/', paddle_view, name='paddle'),
	path('api-game/ball-info/', ball_info, name='ball_info'),
	path('start-game/', start_game_view, name='start_game'),
]