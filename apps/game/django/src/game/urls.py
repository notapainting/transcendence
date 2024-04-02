

from django.urls import path, include
from . import views


urlpatterns = [
	path('api-game/paddle/', views.paddle_view, name='paddle'),
	path('api-game/ball-info/', views.ball_info, name='ball_info'),
	path('start-game/', views.start_game_view, name='start_game'),
]