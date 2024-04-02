
import json, random

from django.shortcuts import render
from django.http import JsonResponse, HttpRequest
from django.views.decorators.csrf import csrf_exempt
from rest_framework import routers, serializers, viewsets
from channels.generic.websocket import WebsocketConsumer

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
ballX = height / 2
ballY = width / 2
ballSpeedX = 7
ballSpeedY = 7

class PlayerR() :
	score = 0

class PlayerL() :
	score = 0

class ChatConsumer(WebsocketConsumer):
    def connect(self):
        self.accept()
    def disconnect(self, close_code):
        pass
    def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        self.send(text_data=json.dumps({
            'message': message
        }))

@csrf_exempt
def paddle_view(request):
    if request.method == 'POST':
        key_pressed = json.loads(request.body).get('keyPressed')
        if key_pressed == "up":
            upPressed = True
            # return JsonResponse({'message': 'up!'})
        elif key_pressed == "down":
            downPressed = True
            # return JsonResponse({'message': 'down!'})
        elif key_pressed == "w":
            wPressed = True
            # return JsonResponse({'message': 'w!'})
        elif key_pressed == "s":
            sPressed = True
            # return JsonResponse({'message': 's!'})
        key_release = json.loads(request.body).get('keyRelease')
        if key_release == "up":
            upPressed = False
            # return JsonResponse({'message': 'up stop!'})
        elif key_release == "down":
            downPressed = False
            # return JsonResponse({'message': 'down stop!'})
        elif key_release == "w":
            wPressed = False
            # return JsonResponse({'message': 'w stop!'})
        elif key_release == "s":
            sPressed = False
            # return JsonResponse({'message': 's stop!'})
        else:
            return JsonResponse({'message': 'none'})
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée'}, status=405)

@csrf_exempt
def start_game_view(request):
    global game_running
    if request.method == 'POST':
        gameRunning = json.loads(request.body).get('gameRunning')
        if gameRunning == True:
            game_running = True
            print(game_running)
            return JsonResponse({'message': 'Start click'})
        elif gameRunning == False:
            game_running = False
            return JsonResponse({'message': 'Stop click'})
        else:
            return JsonResponse({'error': 'Paramètre de requête incorrect'}, status=400)
    else:
        return JsonResponse({'error': 'Méthode HTTP non autorisée'}, status=405)

@csrf_exempt
def update(request):
    global ballX, ballY, ballSpeedX, ballSpeedY, rightPaddleY, leftPaddleY

    if upPressed and rightPaddleY > 0:
        rightPaddleY -= paddleSpeed
    elif downPressed and rightPaddleY + paddleHeight < height:
        rightPaddleY += paddleSpeed

    if wPressed and leftPaddleY > 0:
        leftPaddleY -= paddleSpeed
    elif sPressed and leftPaddleY + paddleHeight < height:
        leftPaddleY += paddleSpeed
    ballX += ballSpeedX
    ballY += ballSpeedY
    if ballY - ballRadius < 0 or ballY + ballRadius > height:
        ballSpeedY = -ballSpeedY
    if (ballX - ballRadius < paddleWidth and
            ballY > leftPaddleY and
            ballY < leftPaddleY + paddleHeight):
        ballSpeedX = -ballSpeedX

    if (ballX + ballRadius > width - paddleWidth and
            ballY > rightPaddleY and
            ballY < rightPaddleY + paddleHeight):
        ballSpeedX = -ballSpeedX
    if ballX < 0:
        # rightPlayerScore += 1
        reset(request)
    elif ballX > width:
        # leftPlayerScore += 1
        reset(request)
    # if leftPlayerScore == maxScore:
    #     playerWin("Left player")
    # elif rightPlayerScore == maxScore:
    #     playerWin("Right player")


@csrf_exempt
def reset(request):
    global ballX, ballY, ballSpeedX, ballSpeedY

    ballX = width / 2
    ballY = height / 2
    ballSpeedX = -ballSpeedX
    ballSpeedY = random.uniform(-5, 5)


@csrf_exempt
def ball_info(request):
    print(game_running)
    if game_running == True :
        update(HttpRequest())
    ball_info = {
        'x': ballX,
        'y': ballY,
        'radius': ballRadius,
        'speed_x': ballSpeedX,
        'speed_y': ballSpeedY,
        'width' : width,
        'height' : height
    }
    return JsonResponse(ball_info)


# @csrf_exempt
# def loop(request):
#     if game_running == True :
#         update(request)
#     else :
#         print("game  not running")
