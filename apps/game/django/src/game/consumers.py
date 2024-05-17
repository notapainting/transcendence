# game/consumers.py
import json, random, asyncio, time
import sys

from channels.generic.websocket import AsyncWebsocketConsumer

width = 50
height = 30
maxScore = 50
paddleHeight = 80
paddleWidth = 10
ballSpeedX = 0.8
acceleration = 0.05
reset = 0
counter = 0
max_speed = 2
# randB = None
# playerBonus = -1 # 0 for right and 1 for left

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
        elif message == "bonus":
            self.game_state.status['randB'] = text_data_json["bonus"]

        else :
            asyncio.create_task(self.game_state.update_player_position(message))


class GameState:
    def __init__(self):
        self.status = {
        'ballX': 0,
        'ballY': 0,
        'collisionX': 0,
        'collisionY': 0,
        'ballRadius': 1,
        'ballSpeedX': ballSpeedX,
        'ballSpeedY': 0.2,
        'width' : 150,
        'height' : 50,
        'leftPaddleY' : 0,
        'leftPaddleX' : -width,
        'rightPaddleX' : width,
        'rightPaddleY' : 0,
        'paddleWidth' : 1,
        'paddleHeightL' : 10, 
        'paddleHeightR' : 10, 
        'paddleSpeedR' : 1.2,
        'paddleSpeedL' : 1.2,
        'leftPlayerScore' : 0,
        'rightPlayerScore' : 0,
        'winner' : 'none',
        'upPressed' : False,
        'downPressed' : False,
        'wPressed' : False,
        'sPressed' : False,
        'game_running' : False,
        'randB': 'none',
        'playerBonus' : -1,
        'bonusStartTime': None,
        'malusStartTime': None,
        'reducingR': False,
        'reducingL': False,
        'maximizeR': False,
        'maximizeL': False
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
        'speed': self.status['ballSpeedX'],
        'collisionX': self.status['collisionX'],
        'collisionY': self.status['collisionY'],
        'radius': self.status['ballRadius'],
        'width' : width,
        'height' : height,
        'leftPaddleY' : self.status['leftPaddleY'],
        'leftPaddleX' : self.status['leftPaddleX'],
        'rightPaddleY' : self.status['rightPaddleY'],
        'rightPaddleX' : self.status['rightPaddleX'],
        'paddleWidth' : self.status['paddleWidth'],
        'paddleHeightL' : self.status['paddleHeightL'],
        'paddleHeightR' : self.status['paddleHeightR'],
        'leftPlayerScore' : self.status['leftPlayerScore'],
        'rightPlayerScore' : self.status['rightPlayerScore'],
        'winner' : self.status['winner']
    }

    def longPaddle(self):
        # bonus increase paddle size
        if self.status['randB'] == 'longPaddle' and self.status['playerBonus'] == 0:
            self.status['randB'] = 'longPaddleR'
            self.status['bonusStartTime'] = time.time()  
            self.status['reducingR'] = False  
        if self.status['randB'] == 'longPaddle' and self.status['playerBonus'] == 1:
            self.status['randB'] = 'longPaddleL'
            self.status['bonusStartTime'] = time.time()  
            self.status['reducingL'] = False  

        # right player long paddle
        if self.status['randB'] == 'longPaddleR' and not self.status['reducingR']:
            if self.status['paddleHeightR'] < 20:
                self.status['paddleHeightR'] += 0.2
            if self.status['paddleHeightR'] >= 20:
                elapsed_time = time.time() - self.status['bonusStartTime']
                if elapsed_time >= 10:
                    self.status['reducingR'] = True 

        if self.status['reducingR']:
            if self.status['paddleHeightR'] > 10:
                self.status['paddleHeightR'] -= 0.2
            if self.status['paddleHeightR'] <= 10:
                self.status['paddleHeightR'] = 10
                self.status['randB'] = 'none'
                self.status['reducingR'] = False

        # left player long paddle
        if self.status['randB'] == 'longPaddleL' and not self.status['reducingL']:
            if self.status['paddleHeightL'] < 20:
                self.status['paddleHeightL'] += 0.2
            if self.status['paddleHeightL'] >= 20:
                elapsed_time = time.time() - self.status['bonusStartTime']
                if elapsed_time >= 10:  
                    self.status['reducingL'] = True  

        if self.status['reducingL']:
            if self.status['paddleHeightL'] > 10:
                self.status['paddleHeightL'] -= 0.2
            if self.status['paddleHeightL'] <= 10:
                self.status['paddleHeightL'] = 10
                self.status['randB'] = 'none'
                self.status['reducingL'] = False
        
    def shortPaddle(self):
        # bonus increase paddle size
        if self.status['randB'] == 'shortPaddle' and self.status['playerBonus'] == 0:
            self.status['randB'] = 'shortPaddleR'
            self.status['malusStartTime'] = time.time()  
            self.status['maximizeR'] = False  
        if self.status['randB'] == 'shortPaddle' and self.status['playerBonus'] == 1:
            self.status['randB'] = 'shortPaddleL'
            self.status['malusStartTime'] = time.time()  
            self.status['maximizeL'] = False  

        # right player long paddle
        if self.status['randB'] == 'shortPaddleR' and not self.status['maximizeR']:
            if self.status['paddleHeightR'] > 5:
                self.status['paddleHeightR'] -= 0.1
            if self.status['paddleHeightR'] <= 5:
                elapsed_time = time.time() - self.status['malusStartTime']
                if elapsed_time >= 10:
                    self.status['maximizeR'] = True 

        if self.status['maximizeR']:
            if self.status['paddleHeightR'] < 10:
                self.status['paddleHeightR'] += 0.1
            if self.status['paddleHeightR'] >= 10:
                self.status['paddleHeightR'] = 10
                self.status['randB'] = 'none'
                self.status['maximizeR'] = False

        # left player long paddle
        if self.status['randB'] == 'shortPaddleL' and not self.status['maximizeL']:
            if self.status['paddleHeightL'] > 5:
                self.status['paddleHeightL'] -= 0.1
            if self.status['paddleHeightL'] <= 5:
                elapsed_time = time.time() - self.status['malusStartTime']
                if elapsed_time >= 10:  
                    self.status['maximizeL'] = True  

        if self.status['maximizeL']:
            if self.status['paddleHeightL'] < 10:
                self.status['paddleHeightL'] += 0.1
            if self.status['paddleHeightL'] >= 10:
                self.status['paddleHeightL'] = 10
                self.status['randB'] = 'none'
                self.status['maximizeL'] = False
    
    def slow(self):
        if self.status['randB'] == 'slow' and self.status['playerBonus'] == 0:
            self.status['randB'] = 'slowR'
            self.status['malusStartTime'] = time.time()
        if self.status['randB'] == 'slow' and self.status['playerBonus'] == 1:
            self.status['randB'] = 'slowL'
            self.status['malusStartTime'] = time.time()
        
        if self.status['randB'] == 'slowR':
            self.status['paddleSpeedR'] = 0.5
            elapsed_time = time.time() - self.status['malusStartTime']
            if elapsed_time >= 10:
                self.status['paddleSpeedR'] = 1.2
        
        if self.status['randB'] == 'slowL':
            self.status['paddleSpeedL'] = 0.5
            elapsed_time = time.time() - self.status['malusStartTime']
            if elapsed_time >= 10:
                self.status['paddleSpeedL'] = 1.2 


    def update(self):
        global reset, max_speed

        if reset == 1:
            reset = 2

        self.longPaddle()
        self.shortPaddle()
        self.slow()

        # paddle displacement
        if self.status['upPressed'] and self.status['rightPaddleY'] + self.status['paddleHeightR'] / 2 < height:
            self.status['rightPaddleY'] += self.status['paddleSpeedR']
        elif self.status['downPressed'] and self.status['rightPaddleY'] - self.status['paddleHeightR'] / 2 > -height:
            self.status['rightPaddleY'] -= self.status['paddleSpeedR']

        if self.status['wPressed'] and self.status['leftPaddleY'] + self.status['paddleHeightL'] / 2 < height:
            self.status['leftPaddleY'] += self.status['paddleSpeedL']
        elif self.status['sPressed'] and self.status['leftPaddleY'] - self.status['paddleHeightL'] / 2 > -height:
            self.status['leftPaddleY'] -= self.status['paddleSpeedL']

        # ball displacement
        self.status['ballX'] += self.status['ballSpeedX']
        self.status['ballY'] += self.status['ballSpeedY']

        # collision up and down
        if self.status['ballY'] <= -height + self.status['ballRadius'] or self.status['ballY'] >= height - self.status['ballRadius']:
            self.status['ballSpeedY'] *= -1

        right_paddle_top = self.status['rightPaddleY'] + self.status['paddleHeightR'] / 2
        right_paddle_bottom = self.status['rightPaddleY'] - self.status['paddleHeightR'] / 2

        left_paddle_top = self.status['leftPaddleY'] + self.status['paddleHeightL'] / 2
        left_paddle_bottom = self.status['leftPaddleY'] - self.status['paddleHeightL'] / 2

        # collision with paddles
        if (self.status['ballX'] + self.status['ballRadius'] > self.status['rightPaddleX'] - self.status['paddleWidth'] and
                self.status['ballY'] >= right_paddle_bottom and
                self.status['ballY'] <= right_paddle_top and 
                self.status['ballSpeedX'] > 0):
            self.status['ballSpeedX'] *= -1 - acceleration
            
            hit_pos = (self.status['rightPaddleY'] - self.status['ballY']) / self.status['paddleHeightR']
            self.status['ballSpeedY'] = hit_pos * max_speed
            self.status['playerBonus'] = 0

        if (self.status['ballX'] - self.status['ballRadius'] < self.status['leftPaddleX'] + self.status['paddleWidth'] and
                self.status['ballY'] >= left_paddle_bottom and
                self.status['ballY'] <= left_paddle_top and
                self.status['ballSpeedX'] < 0):
            self.status['ballSpeedX'] *= -1 - acceleration

            hit_pos = (self.status['leftPaddleY'] - self.status['ballY']) / self.status['paddleHeightL']
            self.status['ballSpeedY'] = hit_pos * max_speed
            self.status['playerBonus'] = 1
    
        if self.status['ballX'] <= self.status['leftPaddleX']: # a changer pour le bug des paddle
            self.status['rightPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reset()
        elif self.status['ballX'] >= self.status['rightPaddleX']: # a changer pour le bug des paddle
            self.status['leftPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
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
        global reset, counter

        self.status['ballX'] = 0
        self.status['ballY'] = 0
        self.status['playerBonus'] = -1
        if counter % 2 == 0:
            self.status['ballSpeedX'] = -ballSpeedX 
        else:
            self.status['ballSpeedX'] = ballSpeedX 
        counter += 1
        self.status['ballSpeedY'] = random.uniform(-1, 1)
        reset = 1


async def loop(self):
    global reset
    while self.game_state.status['game_running']:
        message = self.game_state.update()
        await asyncio.sleep(0.02)
        asyncio.create_task(self.game_state.update_player_position(message))
        await self.send(json.dumps(self.game_state.to_dict('none')))
        if reset ==  2:
            time.sleep(0.5)
            reset = 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
