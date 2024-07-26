# game/gamestate.py
import game.utils as utils
import game.power_up as pow
import game.enums as enu
import random, asyncio, time


DEFAULT_SCORE = 1
MAX_SCORE = 15
TIME_REFRESH = 0.5
width = 50
height = 30
paddleHeight = 80
paddleWidth = 10
ballSpeedX = 0.8
acceleration = 0.05
reset = 0
counter = 0
max_speed = 2

class GameState:
    def __init__(self, bonused=True, scoreToWin=DEFAULT_SCORE):
        self.timer = utils.Timer(verbose=False)
        self.p = pow.PowerUpManager()
        self.scoreToWin = scoreToWin
        self.bonused = bonused
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

    def changeSettings(self, data):
        setattr(self, data['param'], data['value'])
        return self.getSettings()

    def getSettings(self):
        return ({
            "scoreToWin": self.scoreToWin,
            "bonused":self.bonused,
        })

    def update(self):
        global reset, max_speed

        if reset == 1:
            reset = 2
        if self.bonused:
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

        # compute score
        score = None
        if self.status['ballX'] <= self.status['leftPaddleX']:
            self.status['rightPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reset()
            score = {"score":[self.status['leftPlayerScore'], self.status['rightPlayerScore']]}
        elif self.status['ballX'] >= self.status['rightPaddleX']:
            self.status['leftPlayerScore'] += 1
            self.status['collisionX'] = self.status['ballX']
            self.status['collisionY'] = self.status['ballY']
            self.reset()
            score = {"score":[self.status['leftPlayerScore'], self.status['rightPlayerScore']]}

        # compute win
        if self.status['leftPlayerScore'] == self.scoreToWin:
            self.reset()
            self.status['winner'] = 'leftWin'
            self.status['game_running'] = False
            return True, score
        elif self.status['rightPlayerScore'] == self.scoreToWin:
            self.reset()
            self.status['winner'] = 'rightWin'
            self.status['game_running'] = False
            return False, score

        return None, score

    
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

async def local_loop(self):
    global reset
    try :
        while self.local_game_state.status['game_running']:
            end, score = self.local_game_state.update()
            if score is not None:
                score['players'] = self.local_current[self.local_matchIdx]
                await self.send_json({"type":enu.Game.SCORE, "message":score})
            if end is not None:
                return await self.channel_layer.send(self.channel_name, {"type":enu.Game.END})
            await self.send_json({"type": enu.Local.UPDATE, "message":self.local_game_state.to_dict('none')})
            if reset ==  2:
                time.sleep(0.5)
                reset = 0                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                    
            await asyncio.sleep(TIME_REFRESH)
    except asyncio.CancelledError as error:
        print(error)


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
            await self.match.broadcast({'type':enu.Game.UPDATE, 'author': self.username, 'message':self.match.game_state.to_dict('none')})
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
