# game/gamestate.py
import game.timer as tim
import game.power_up as pow
import game.enums as enu
import random, asyncio
import threading
import time
import sys

from channels.layers import get_channel_layer
from logging import getLogger
logger = getLogger('base')

BONUSED=True
DEFAULT_SCORE = 5
MIN_SCORE = 1
MAX_SCORE = 15

TIME_PAUSE_START = 3
TIME_PAUSE = 0.5
TIME_REFRESH = 0.016

WIDTH = 50
HEIGHT = 30

paddleWidth = 10

ballSpeedX = 0.8
ACCELERATION = 0.05

RESET = 0
COUNTER = -1
MAX_SPEED = 2

def getDefaultState():
    return {
        'x':0,
        'y':0,
        'speed':ballSpeedX,
        'collisionX':0,
        'collisionY':0,
        'radius': 1,
        'width' : WIDTH,
        'height' : HEIGHT,
        'leftPaddleY' : 0,
        'leftPaddleX' : -WIDTH,
        'rightPaddleY' : 0,
        'rightPaddleX' : WIDTH,
        'paddleWidth' : 1,
        'paddleHeightL' :10,
        'paddleHeightR' :10,
        'leftPlayerScore' : 0,
        'rightPlayerScore' : 0,
        'randomPointB': None,
        'randomPointM': None,
        'randomPointE': None,
        'bonus': None,
        'hitB': False,
        'hitM': False,
    }


# host == left
# guest == right
class GameState:
    def __init__(self, group, leftPlayer, rightPlayer, bonused=True, scoreToWin=DEFAULT_SCORE):
        self._chlayer = get_channel_layer()
        self._group_id = group

        self.scoreToWin = scoreToWin
        self.bonused = bonused

        self.leftPlayer = leftPlayer
        self.rightPlayer = rightPlayer
        self.result = {
                "winner":self.rightPlayer,
                "loser":self.rightPlayer,
                "score_w":0,
                "score_l":0,
            }

        self.reset  = RESET
        self.counter  = COUNTER
        self.running = False
        self.paused = False
        self.timer = tim.ATimer(verbose=False)
        self.p = pow.PowerUpManager(self.timer)
        self._statused()

    def _statused(self):
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
            'leftPaddleX' : -WIDTH,
            'rightPaddleX' : WIDTH,
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
            'playerBonus' : -1,
            'startTime': 0,
            'totalTime': 0,
            'last_update_time' : 0
        }
        self.right_paddle_top = self.status['rightPaddleY'] + self.status['paddleHeightR'] / 2
        self.right_paddle_bottom = self.status['rightPaddleY'] - self.status['paddleHeightR'] / 2
        self.left_paddle_top = self.status['leftPaddleY'] + self.status['paddleHeightL'] / 2
        self.left_paddle_bottom = self.status['leftPaddleY'] - self.status['paddleHeightL'] / 2

    async def _send(self, message):
        message['author'] = "system"
        await self._chlayer.group_send(self._group_id, message)

    async def update_player_position(self, message):
        if message == "wPressed":
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

    def to_dict(self):
        return {
            'x': self.status['ballX'],
            'y': self.status['ballY'],
            'speed': self.status['ballSpeedX'],
            'collisionX': self.status['collisionX'],
            'collisionY': self.status['collisionY'],
            'radius': self.status['ballRadius'],
            'width' : WIDTH,
            'height' : HEIGHT,
            'leftPaddleY' : self.status['leftPaddleY'],
            'leftPaddleX' : self.status['leftPaddleX'],
            'rightPaddleY' : self.status['rightPaddleY'],
            'rightPaddleX' : self.status['rightPaddleX'],
            'paddleWidth' : self.status['paddleWidth'],
            'paddleHeightL' : self.status['paddleHeightL'],
            'paddleHeightR' : self.status['paddleHeightR'],
            'leftPlayerScore' : self.status['leftPlayerScore'],
            'rightPlayerScore' : self.status['rightPlayerScore'],
            'randomPointB': self.p.random_point_b,
            'randomPointM': self.p.random_point_m,
            'randomPointE': self.p.random_point_e,
            'bonus': self.p.randB,
            'hitB': self.p.hitB,
            'hitM': self.p.hitM
        }

    def changeSettings(self, data):
        setattr(self, data['param'], data['value'])
        return self.getSettings()

    def getSettings(self):
        return ({
            "scoreToWin": self.scoreToWin,
            "bonused":self.bonused,
        })

    def applyBonus(self):
        if self.bonused:
            self.p.addBonus(self.status)
            self.p.addMalus(self.status)
            self.p.longPaddle(self.status)
            self.p.shortPaddle(self.status)
            self.p.slow(self.status)
            self.p.boost(self.status)

    def computeMovementPaddle(self, delta_time):
        if self.status['upPressed'] and self.status['rightPaddleY'] + self.status['paddleHeightR'] / 2 < HEIGHT:
            self.status['rightPaddleY'] += self.status['paddleSpeedR']
            self.right_paddle_top = self.status['rightPaddleY'] + self.status['paddleHeightR'] / 2
            self.right_paddle_bottom = self.status['rightPaddleY'] - self.status['paddleHeightR'] / 2
        elif self.status['downPressed'] and self.status['rightPaddleY'] - self.status['paddleHeightR'] / 2 > -HEIGHT:
            self.status['rightPaddleY'] -= self.status['paddleSpeedR']
            self.right_paddle_top = self.status['rightPaddleY'] + self.status['paddleHeightR'] / 2
            self.right_paddle_bottom = self.status['rightPaddleY'] - self.status['paddleHeightR'] / 2

        if self.status['wPressed'] and self.status['leftPaddleY'] + self.status['paddleHeightL'] / 2 < HEIGHT:
            self.status['leftPaddleY'] += self.status['paddleSpeedL']
            self.left_paddle_top = self.status['leftPaddleY'] + self.status['paddleHeightL'] / 2
            self.left_paddle_bottom = self.status['leftPaddleY'] - self.status['paddleHeightL'] / 2
        elif self.status['sPressed'] and self.status['leftPaddleY'] - self.status['paddleHeightL'] / 2 > -HEIGHT:
            self.status['leftPaddleY'] -= self.status['paddleSpeedL']
            self.left_paddle_top = self.status['leftPaddleY'] + self.status['paddleHeightL'] / 2
            self.left_paddle_bottom = self.status['leftPaddleY'] - self.status['paddleHeightL'] / 2

    def computeMovementBall(self, delta_time):
        self.status['ballX'] += self.status['ballSpeedX'] * delta_time
        self.status['ballY'] += self.status['ballSpeedY'] * delta_time

    def computeCollisionBallWall(self):
        if self.status['ballY'] <= -HEIGHT + self.status['ballRadius'] or self.status['ballY'] >= HEIGHT - self.status['ballRadius']:
            self.status['ballSpeedY'] *= -1

    def computeCollisionPaddleBall(self):
        if (self.status['ballSpeedX'] > 0 and
                self.status['ballX'] + self.status['ballRadius'] > self.status['rightPaddleX'] - self.status['paddleWidth'] and
                self.status['ballY'] >= self.right_paddle_bottom and self.status['ballY'] <= self.right_paddle_top):
            self.status['ballSpeedX'] *= -1 - ACCELERATION

            hit_pos = (self.status['rightPaddleY'] - self.status['ballY']) / self.status['paddleHeightR']
            self.status['ballSpeedY'] = hit_pos * MAX_SPEED
            self.status['playerBonus'] = 0
            return True
        elif (self.status['ballSpeedX'] < 0 and
                self.status['ballX'] - self.status['ballRadius'] < self.status['leftPaddleX'] + self.status['paddleWidth'] and
                self.status['ballY'] >= self.left_paddle_bottom and self.status['ballY'] <= self.left_paddle_top):
            self.status['ballSpeedX'] *= -1 - ACCELERATION

            hit_pos = (self.status['leftPaddleY'] - self.status['ballY']) / self.status['paddleHeightL']
            self.status['ballSpeedY'] = hit_pos * MAX_SPEED
            self.status['playerBonus'] = 1
            return True
        return False

    async def computeScore(self):
        if self.status['ballX'] <= self.status['leftPaddleX']:
            self.status['rightPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reseting()
            await self._send({
                "type":enu.Game.RELAY,
                "relay":{
                    "type":enu.Match.SCORE, 
                    "players":[self.leftPlayer,self.rightPlayer],
                    "score":[self.status['leftPlayerScore'],self.status['rightPlayerScore']]
                    }})
        elif self.status['ballX'] >= self.status['rightPaddleX']:
            self.status['leftPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reseting()
            await self._send({
                "type":enu.Game.RELAY,
                "relay":{
                    "type":enu.Match.SCORE, 
                    "players":[self.leftPlayer,self.rightPlayer],
                    "score":[self.status['leftPlayerScore'],self.status['rightPlayerScore']]
                    }})

    async def computeWin(self):
        if self.status['leftPlayerScore'] == self.scoreToWin:
            self.reseting()
            self.result = {
                "winner":self.leftPlayer,
                "loser":self.rightPlayer,
                "score_w":self.status['leftPlayerScore'],
                "score_l":self.status['rightPlayerScore'],
            }
            await self._send({"type":enu.Match.END, "winner":self.result['winner'], "loser":self.result['loser']})
            return False
        elif self.status['rightPlayerScore'] == self.scoreToWin:
            self.reseting()
            self.result = {
                "winner":self.rightPlayer,
                "loser":self.leftPlayer,
                "score_w":self.status['rightPlayerScore'],
                "score_l":self.status['leftPlayerScore'],
            }
            await self._send({"type":enu.Match.END, "winner":self.result['winner'], "loser":self.result['loser']})
            return False
        return self.running

    async def update(self):
        current_time = time.time()
        if (self.status['last_update_time'] == 0):
            delta_time = 1
        else:
            delta_time = (current_time - self.status['last_update_time']) * 30 
        self.status['last_update_time'] = current_time

        self.applyBonus()
        self.computeMovementPaddle(delta_time)
        self.computeMovementBall(delta_time)
        self.computeCollisionBallWall()
        if self.computeCollisionPaddleBall() is False:
            await self.computeScore()
        return await self.computeWin()

    def reseting(self):
        self.status['last_update_time'] = 0
        self.status['ballX'] = 0
        self.status['ballY'] = 0
        self.status['playerBonus'] = -1
        self.status['ballSpeedX'] = self.counter * ballSpeedX 
        self.counter *= -1
        self.status['ballSpeedY'] = random.uniform(-1, 1)
        self.reset = 2

    async def _loop(self):
        try :
            await asyncio.sleep(TIME_PAUSE_START)
            # while self.running:
            while True:
                if (self.running == False):
                    await asyncio.sleep(0.5)
                    continue
                await asyncio.sleep(TIME_REFRESH)
                if (self.paused == False):
                    self.running = await self.update()
                    await self._send({"type":enu.Game.RELAY, "relay":{"type": enu.Match.UPDATE, "message":self.to_dict()}})
                if self.reset ==  2:
                    await asyncio.sleep(TIME_PAUSE)
                    self.reset = 0
        except asyncio.CancelledError:
            pass
        except BaseException as error:
            logger.critical(f"internal : {error}")

    async def start(self):
        self.running = True
        self.timer.resume()
        # self.task = asyncio.create_task(self._loop())
        # self.status['last_update_time'] = time.time()
        self.task = threading.Thread(target=lambda: asyncio.run(self._loop()))
        self.task.start()

    async def stop(self):
        self.running = False
        self.timer.pause()
        # if self.task is not None:
        #     # self.task._stop()
        #     await self.task

    async def pause(self):
        # if self.running == False
        #     return
        if self.paused == False:
            self.status['last_update_time'] = 0
            self.running = False
            self.paused = True
            self.timer.pause()
            # await self.stop()
            await self._send({"type":enu.Match.PAUSE})
        else:
            self.paused = False
            self.running = True
            self.timer.resume()
            # await self.start()
            await self._send({"type":enu.Game.RELAY, "relay":{"type":enu.Match.RESUME}})

    async def feed(self, key):
        if self.running and self.paused == False:
            await self.update_player_position(key)

    async def feed_bonus(self, bonus):
        if self.running:
            self.status['randB'] = bonus

    async def _end(self):
        if self.task is not None:
            # self.task.cancel()
            self.task._stop()
            # await self.task


