# game/consumers.py
import json, random, asyncio

from channels.generic.websocket import AsyncWebsocketConsumer

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

rightPlayerScore = 0
leftPlayerScore = 0

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        await self.accept()
        init()
        await self.send(json.dumps(get_ball_info('none')))

    async def disconnect(self, close_code):
        init()

    async def receive(self, text_data):
        global game_running, upPressed, downPressed, wPressed, sPressed
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        # print(message)
        if message == "startButton":
            if game_running == False :
                game_running = True
                asyncio.create_task(loop(self))
                response = get_ball_info('none')
                await self.send(json.dumps(response))
        elif message == "stopButton":
            game_running = False
        elif message == "wPressed":
            wPressed = True
        elif message == "sPressed":
            sPressed = True
        elif message == "upPressed":
            upPressed = True
        elif message == "downPressed":
            downPressed = True
        elif message == "wRelease":
            wPressed = False
        elif message == "sRelease":
            sPressed = False
        elif message == "upRelease":
            upPressed = False
        elif message == "downRelease":
            downPressed = False
    
def get_ball_info(message):
    ball_info = {
        'x': ballX,
        'y': ballY,
        'radius': ballRadius,
        'speed_x': ballSpeedX,
        'speed_y': ballSpeedY,
        'width' : width,
        'height' : height,
        'leftPaddleY' : leftPaddleY,
        'rightPaddleY' : rightPaddleY,
        'paddleWidth' : paddleWidth,
        'paddleHeight' : paddleHeight,
        'leftPlayerScore' : leftPlayerScore,
        'rightPlayerScore' : rightPlayerScore,
        'winner' : message
    }
    return ball_info

async def loop(consumer):
    while game_running:
        message = update(consumer)
        await asyncio.sleep(0.02)
        await consumer.send(json.dumps(get_ball_info('none')))
        if (message == 'leftWin' or message == 'righttWin') :
            await consumer.send(json.dumps(get_ball_info(message)))

def update(consumer):
    global ballX, ballY, ballSpeedX, ballSpeedY, rightPaddleY, leftPaddleY, rightPlayerScore, leftPlayerScore
    global game_running

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
        rightPlayerScore += 1
        reset()
    elif ballX > width:
        leftPlayerScore += 1
        reset()
    if leftPlayerScore == maxScore:
        reset()
        game_running = False
        return 'leftWin'
    elif rightPlayerScore == maxScore:
        reset()
        game_running = False
        return 'rightWin'
    return 'none'

def reset():
    global ballX, ballY, ballSpeedX, ballSpeedY

    ballX = width / 2
    ballY = height / 2
    ballSpeedX = -ballSpeedX
    ballSpeedY = random.uniform(-5, 5)

def init():
    global ballX, ballY, ballSpeedX, ballSpeedY, rightPaddleY, leftPaddleY, rightPlayerScore, leftPlayerScore
    global game_running, upPressed, downPressed, wPressed, sPressed, ballRadius, paddleWidth, paddleSpeed

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
    ballSpeedX = 10
    ballSpeedY = 10

    rightPlayerScore = 0
    leftPlayerScore = 0
