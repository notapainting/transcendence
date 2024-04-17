# game/consumers.py
import json, random, asyncio, time
import sys

from channels.generic.websocket import AsyncWebsocketConsumer

width = 50
height = 30
maxScore = 2
paddleHeight = 80
paddleWidth = 10
ballSpeedX = 0.8

class GameConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.game_state = GameState()
        await self.accept()
        # self.game_state.__init__()
        await self.send(json.dumps(self.game_state.to_dict('none')))

    async def disconnect(self, close_code):
        del self.game_state

    async def receive(self, text_data):
        global game_running, upPressed, downPressed, wPressed, sPressed
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        if message == "startButton":
             if self.game_state.status['game_running'] == False :
                self.game_state.status['game_running'] = True
                asyncio.create_task(loop(self))
        else :
            asyncio.create_task(self.game_state.update_player_position(message))


class GameState:
    def __init__(self):
        self.status = {
        'ballX': 0,
        'ballY': 0,
        'ballRadius': 1,
        'ballSpeedX': ballSpeedX,
        'ballSpeedY': 0.1,
        'width' : 150,
        'height' : 50,
        'leftPaddleY' : 0,
        'rightPaddleY' : 0,
        'paddleWidth' : 1,
        'paddleHeight' : 10, 
        'paddleSpeed' : 1.2,
        'leftPlayerScore' : 0,
        'rightPlayerScore' : 0,
        'winner' : 'none',
        'upPressed' : False,
        'downPressed' : False,
        'wPressed' : False,
        'sPressed' : False,
        'game_running' : False
    }

    async def update_player_position(self, message):
        if message == "stopButton":
            self.status['game_running'] = False
        elif message == "wPressed":
            self.status['wPressed'] = True
        elif message == "sPressed":
            self.status['sPressed'] = True
        elif message == "upPressed":
            self.status['upPressed'] = True
        elif message == "downPressed":
            self.status['downPressed'] = True
        elif message == "wRelease":
            self.status['wPressed'] = False
        elif message == "sRelease":
            self.status['sPressed'] = False
        elif message == "upRelease":
            self.status['upPressed'] = False
        elif message == "downRelease":
            self.status['downPressed'] = False

    def to_dict(self, winner): #mise en forme
        return {
        'x': self.status['ballX'],
        'y': self.status['ballY'],
        'radius': self.status['ballRadius'],
        'width' : width,
        'height' : height,
        'leftPaddleY' : self.status['leftPaddleY'],
        'rightPaddleY' : self.status['rightPaddleY'],
        'paddleWidth' : self.status['paddleWidth'],
        'paddleHeight' : self.status['paddleHeight'],
        'leftPlayerScore' : self.status['leftPlayerScore'],
        'rightPlayerScore' : self.status['rightPlayerScore'],
        'winner' : self.status['winner']
    }
    
    def update(self):
        if self.status['upPressed'] and self.status['rightPaddleY'] + self.status['paddleHeight'] / 2 < height:
            self.status['rightPaddleY'] += self.status['paddleSpeed']
        elif self.status['downPressed'] and self.status['rightPaddleY'] - self.status['paddleHeight'] / 2 > -height:
            self.status['rightPaddleY'] -= self.status['paddleSpeed']

        if self.status['wPressed'] and self.status['leftPaddleY'] + self.status['paddleHeight'] / 2 < height:
            self.status['leftPaddleY'] += self.status['paddleSpeed']
        elif self.status['sPressed'] and self.status['leftPaddleY'] - self.status['paddleHeight'] / 2 > -height:
            self.status['leftPaddleY'] -= self.status['paddleSpeed']

        self.status['ballX'] += self.status['ballSpeedX']
        self.status['ballY'] += self.status['ballSpeedY']

        if self.status['ballY'] - self.status['ballRadius'] < -height  or self.status['ballY'] + self.status['ballRadius'] > height :
            self.status['ballSpeedY'] *= -1

        if (self.status['ballX'] + self.status['ballRadius'] > width - 5 - self.status['paddleWidth'] and
                self.status['ballY'] > self.status['rightPaddleY'] - self.status['paddleHeight'] / 2 and
                self.status['ballY'] < self.status['rightPaddleY'] + self.status['paddleHeight'] / 2):
            self.status['ballSpeedX'] *= -1.05

        if (self.status['ballX'] - self.status['ballRadius'] < -width + 5 + self.status['paddleWidth'] and
                self.status['ballY'] > self.status['leftPaddleY'] - self.status['paddleHeight'] / 2 and
                self.status['ballY'] < self.status['leftPaddleY'] + self.status['paddleHeight'] / 2):
            self.status['ballSpeedX'] *= -1.05

        if self.status['ballX'] < -width + 2:
            self.status['rightPlayerScore'] += 1
            # time.sleep(0.2)
            self.reset()
        elif self.status['ballX'] > width  - 2:
            self.status['leftPlayerScore'] += 1
            # time.sleep(0.2)
            self.reset()
        if self.status['leftPlayerScore'] == maxScore:
            self.reset()
            self.status['winner'] = 'leftWin'
            self.status['game_running'] = False
        elif self.status['rightPlayerScore'] == maxScore:
            self.reset()
            self.status['winner'] = 'rightWin'
            self.status['game_running'] = False
    
    def reset(self):
        self.status['ballX']  = 0
        self.status['ballY']  = 0
        self.status['ballSpeedX'] = -ballSpeedX
        self.status['ballSpeedY'] = random.uniform(-1, 1)

async def loop(self):
    while self.game_state.status['game_running']:
        message = self.game_state.update()
        await asyncio.sleep(0.02)
        asyncio.create_task(self.game_state.update_player_position(message))
        await self.send(json.dumps(self.game_state.to_dict('none')))                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                        
