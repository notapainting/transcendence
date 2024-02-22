from django.shortcuts import render
from django.http import JsonResponse


width = 900
height = 600
maxscore = 5

gamerunning = False

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