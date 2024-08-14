# game/gamestate.py
import game.utils as utils
import game.timer as tim
import game.power_up as pow
import game.enums as enu
import random, asyncio, time

from channels.layers import get_channel_layer


BONUSED=True
DEFAULT_SCORE = 1
MIN_SCORE = 1
MAX_SCORE = 15

TIME_REFRESH = 0.02
WIDTH = 50
HEIGHT = 30

paddleWidth = 10

ballSpeedX = 0.8
ACCELERATION = 0.05

RESET = 0
COUNTER = -1
MAX_SPEED = 2


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
            'upPressed' : False, # change to host and guest paddles
            'downPressed' : False,
            'wPressed' : False,
            'sPressed' : False,
            'game_running' : False,
            'playerBonus' : -1,
            'startTime': 0,
            'totalTime': 0
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

    def to_dict(self): #mise en forme
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

    def computeMovementPaddle(self):
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

    def computeMovementBall(self):
        self.status['ballX'] += self.status['ballSpeedX']
        self.status['ballY'] += self.status['ballSpeedY']

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
            await self._send({"type":enu.Match.END, "winner":self.leftPlayer, "loser":self.leftPlayer})
            return False
        elif self.status['rightPlayerScore'] == self.scoreToWin:
            self.reseting()
            self.result = {
                "winner":self.rightPlayer,
                "loser":self.leftPlayer,
                "score_w":self.status['rightPlayerScore'],
                "score_l":self.status['leftPlayerScore'],
            }
            await self._send({"type":enu.Match.END, "winner":self.leftPlayer, "loser":self.rightPlayer})
            return False
        return True

    async def update(self):
        if self.reset == 1:
            self.reset = 2

        self.applyBonus()
        self.computeMovementPaddle()
        self.computeMovementBall()
        self.computeCollisionBallWall()
        if self.computeCollisionPaddleBall() is False:
            await self.computeScore()
        return await self.computeWin()

    def reseting(self):
        self.status['ballX'] = 0
        self.status['ballY'] = 0
        self.status['playerBonus'] = -1
        self.status['ballSpeedX'] = self.counter * ballSpeedX 
        self.counter *= -1
        self.status['ballSpeedY'] = random.uniform(-1, 1)
        self.reset = 1

    async def _loop(self):
        try :
            while self.running:
                if self.reset ==  2:
                    await asyncio.sleep(0.5)
                    self.reset = 0
                await asyncio.sleep(TIME_REFRESH)
                await self._send({"type":enu.Game.RELAY, "relay":{"type": enu.Match.UPDATE, "message":self.to_dict()}})
                self.running = await self.update()
        except asyncio.CancelledError as error:
            print(f"task cancellation")
            print(f"error is {error}")
        except BaseException as error:
            print(f"error is {error}")

    async def start(self):
        self.running = True
        self.timer.resume()
        self.task = asyncio.create_task(self._loop())

    async def stop(self):
        self.running = False
        self.timer.pause()
        if self.task is not None:
            self.task.cancel()
            await self.task

    async def pause(self):
        if self.running:
            await self.stop()
            await self._send({"type":enu.Match.PAUSE})
        else:
            await self.start()
            await self._send({"type":enu.Game.RELAY, "relay":{"type":enu.Match.RESUME}})

    async def feed(self, key):
        if self.running:
            await self.update_player_position(key)

    async def feed_bonus(self, bonus):
        if self.running:
            self.status['randB'] = bonus

    async def _end(self):
        if self.task is not None:
            self.task.cancel()
            await self.task






async def remote_loop(self):
    global reset
    try :
        while self.match.game_state.status['game_running']:
            end, score = self.match.game_state.update()
            if score is not None:
                score['players'] = list(self.match._players)
                print(f"score is {score}")
                await self.match.broadcast({"type":enu.Game.SCORE, "message":score})
            if end is not None:
                message = {"type":enu.Game.END, "author":self.username, "message":self.match.compute()}
                return await self.match.broadcast(message)
            await self.match.broadcast({'type':enu.Game.UPDATE, 'author': self.username, 'message':self.match.game_state.to_dict()})
            if reset==  2:
                time.sleep(0.5)
                reset= 0 
            await asyncio.sleep(TIME_REFRESH)
    except asyncio.CancelledError as error:
        print(error)

"""
    global reset
    while self.local_game_state.status['game_running']:
        message = self.local_game_state.update()
        await asyncio.sleep(0.02)
        asyncio.create_task(self.local_game_state.update_player_position(message))
        await self.send(json.dumps(self.local_game_state.to_dict('none')))
        if reset ==  2:
            time.sleep(0.5)
            reset = 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
"""
