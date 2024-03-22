
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers, serializers, viewsets

width = 900
height = 600
maxScore = 5

game_running = False

# Create your views here.
class Ball() :
	ballRadius = 10
	ballX = width / 2
	ballY = height / 2
	ballSpeedX = 7
	ballSpeedY = 7

class PlayerR() :
	score = 0

class PlayerL() :
	score = 0

def back_test_view(request):
    return JsonResponse({'message': 'bouton back test click!'})

@csrf_exempt
def paddle_view(request):
    return JsonResponse({'message': 'paddle move!'})

@csrf_exempt
def start_game_view(request):
    if request.method == 'POST':
        game_running = json.loads(request.body).get('gameRunning')
        if game_running == True:
            return JsonResponse({'message': 'Start click'})
        elif game_running == False:
            return JsonResponse({'message': 'Stop click'})
        else:
            return JsonResponse({'error': 'Paramètre de requête incorrect'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée'}, status=405)
