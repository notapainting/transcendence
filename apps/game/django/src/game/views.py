
import json

from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers, serializers, viewsets

# Create your views here.

width = 900
height = 600
maxScore = 5

game_running = False

upPressed = False
downPressed = False
wPressed = False
sPressed = False

paddleHeight = 80
paddleWidth = 10
leftPaddleY = height / 2 - paddleHeight / 2
rightPaddleY = height / 2 - paddleHeight / 2
paddleSpeed = 10

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
    if request.method == 'POST':
        key_pressed = json.loads(request.body).get('keyPressed')
        if key_pressed == "up":
            return JsonResponse({'message': 'up!'})
        elif key_pressed == "down":
            return JsonResponse({'message': 'down!'})
        elif key_pressed == "w":
            return JsonResponse({'message': 'w!'})
        elif key_pressed == "s":
            return JsonResponse({'message': 's!'})
        else:
            return JsonResponse({'message': 'none'})
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée'}, status=405)

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
