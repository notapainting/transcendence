# game/consumers.py
import json, random, asyncio, time
import sys

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.exceptions import StopConsumer
import game.utils as utils
import game.power_up as pow
import game.enums as enu

TOURNAMENT_MAX_PLAYER = 16


MAX_SCORE = 50
width = 50
height = 30
maxScore = MAX_SCORE
paddleHeight = 80
paddleWidth = 10
ballSpeedX = 0.8
acceleration = 0.05
reset = 0
counter = 0
max_speed = 2

from game.base import BaseConsumer

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
                self.game_state.timer.resume()
                asyncio.create_task(loop(self))
        else :
            asyncio.create_task(self.game_state.update_player_position(message))


import random
import enum

class Local(enum.StrEnum):
    PLAYERS = "local.tournament.players"
    PHASE = "local.tournament.phase"
    MATCH = "local.tournament.match"
    UPDATE = "local.game.update"
    NEXT = "local.game.next"

class TournamentConsumer(BaseConsumer):
    async def connect(self):
        await self.accept()
        self.players = []
        self.losers = []
        self.task = None

    async def disconnect(self, close_code):
        if self.task is not None:
            self.task.cancel()

    async def receive_json(self, json_data):
        match json_data['type']:
            case Local.PLAYERS: 
                self.players = list(json_data['message'])
                await self.matchmake()
                await self.announce_next()
            case Local.UPDATE:
                await self.gaming(json_data)
            case Local.NEXT:
                await self.announce_next()
            case _:
                print(f"error in local trn: wrong type")

    async def matchmake(self):
        random.suffle(self.players)
        self.current = [(self.players[i],self.players[i + 1]) for i in range(0, len(self.players), 2)]
        self.matchIdx = -1
        await self.send_json({"type":Local.PHASE, "message":self.current})

    async def announce_next(self):
        self.matchIdx += 1
        if self.matchIdx == len(self.current):
            await self.machmake()
            await self.announce_next()
            return
        match = self.current[self.matchIdx]
        await self.send_json({"type":Local.MATCH, "message":match})
        self.game_state = GameState()

    async def game_end(self, data):
        await self.send(json.dumps(self.game_state.to_dict('none')))
        winner = self.game_state.status['winner']
        if winner == 'leftWin':
            loser = self.current[self.matchIdx][1]
        else:
            loser = self.current[self.matchIdx][0]
        self.losers.append(loser)
        self.players.remove(loser)
        if len(self.current) == 1:
            raise StopConsumer

    async def gaming(self, data):
        message = data["message"]
        if message == "startButton":
            if self.game_state.status['game_running'] == False :
                self.game_state.status['game_running'] = True
                self.task = asyncio.create_task(loop(self))
        elif message == "bonus":
            self.game_state.status['randB'] = data["bonus"]
        else :
            asyncio.create_task(self.game_state.update_player_position(message))


class GameState:
    def __init__(self):
        self.timer = utils.Timer(verbose=False)
        self.p = pow.PowerUpManager()
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
        'upPressed' : False, # change to host and guest paddles
        'downPressed' : False,
        'wPressed' : False,
        'sPressed' : False,
        'game_running' : False,
        'playerBonus' : -1,
        'startTime': 0,
        'totalTime': 0
    }

    async def update_player_position(self, message):
        if message == "stopButton":
            self.status['game_running'] = False
            self.timer.pause()
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
        'winner' : self.status['winner'],
        'randomPointB': self.p.random_point_b,
        'randomPointM': self.p.random_point_m,
        'randomPointE': self.p.random_point_e,
        'bonus': self.p.randB,
        'hitB': self.p.hitB,
        'hitM': self.p.hitM
    }

    def update(self):
        global reset, max_speed

        if reset == 1:
            reset = 2

        self.p.addBonus(self.timer, self.status)
        self.p.addMalus(self.timer, self.status)
        
        self.p.longPaddle(self.status)
        self.p.shortPaddle(self.status)
        self.p.slow(self.status)
        self.p.boost(self.status)

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
    
        if self.status['ballX'] <= self.status['leftPaddleX']:
            self.status['rightPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reset()
        elif self.status['ballX'] >= self.status['rightPaddleX']:
            self.status['leftPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reset()
        if self.status['leftPlayerScore'] == maxScore:
            self.reset()
            self.status['winner'] = 'leftWin'
            self.status['game_running'] = False
            return True
        elif self.status['rightPlayerScore'] == maxScore:
            self.reset()
            self.status['winner'] = 'rightWin'
            self.status['game_running'] = False
            return False

        return None

    
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
    try :
        while self.game_state.status['game_running']:
            end = self.game_state.update()
            if end is not None:
                await self.channel_layer.send(self.channel_name, {"type":enu.Game.END})
                return
            await asyncio.sleep(0.02)
            await self.send(json.dumps(self.game_state.to_dict('none')))
            if reset ==  2:
                time.sleep(0.5)
                reset = 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
    except asyncio.CancelledError as error:
        print(error)


async def loop_remote_ultime(self):
    global reset
    try :
        while self.match.game_state.status['game_running']:
            end = self.match.game_state.update()
            if end is not None:
                message = {"type":enu.Game.END, "message":self.match.compute()}
                await self.match.broadcast()
                return 
            await self.send_json({'type':enu.Game.UPDATE, 'message':self.match.game_state.to_dict('none')})
            await self.send_cs(self.match.lobby._challenger, {'type':enu.Game.UPDATE, 'message':self.match.game_state.to_dict('none')})
            if reset==  2:
                time.sleep(0.5)
                reset= 0 
            await asyncio.sleep(0.5)
    except asyncio.CancelledError as error:
        print(error)

"""
    global reset
    while self.game_state.status['game_running']:
        message = self.game_state.update()
        await asyncio.sleep(0.02)
        asyncio.create_task(self.game_state.update_player_position(message))
        await self.send(json.dumps(self.game_state.to_dict('none')))
        if reset ==  2:
            time.sleep(0.5)
            reset = 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
"""
