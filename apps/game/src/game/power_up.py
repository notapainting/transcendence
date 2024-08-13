import random, math
import game.utils as utils

class PowerUpManager:
    def __init__(self, timer):
        self.timer = timer
        self.randB = None
        self.randM = None
        self.randE = None
        self.bonusTime = 2
        self.malusTime = 4
        self.effectTime = 30
        self.bonusStartTime = None
        self.malusStartTime = None
        self.last_update_timeB = None
        self.last_update_timeM = None
        self.reducingR = False
        self.reducingL = False
        self.maximizeR = False
        self.maximizeL = False
        # self.rand_bonus = ['longPaddle', 'boost']
        self.rand_bonus = ['longPaddle']
        # self.rand_malus = ['slow', 'shortPaddle', 'invertedKey']
        self.rand_malus = ['slow', 'shortPaddle']
        self.rand_effect = ['hurricane', 'earthquake', 'glitch']
        self.p1 = {'x': -45, 'y': -25}
        self.p2 = {'x': 45, 'y': -25}
        self.p3 = {'x': 45, 'y': 25}
        self.p4 = {'x': -45, 'y': 25}
        self.random_point_b = None
        self.random_point_m = None
        self.random_point_e = None
        self.hitB = False
        self.hitM = False
        self.hitE = False
    
    def hitBonus(self, data):
        if self.random_point_b != None:
            distance = 10
            ballX = float(data['ballX'])
            ballY = float(data['ballY'])
            random_point_b_x = self.random_point_b['x']
            random_point_b_y = self.random_point_b['y']
            distance = math.sqrt((ballX - random_point_b_x) ** 2 + (ballY - random_point_b_y) ** 2)
            if distance <= 5:
                return True
            else:
                return False
        else:
            return False

    def hitMalus(self, data):
        if self.random_point_m != None:
            distance = 10
            ballX = float(data['ballX'])
            ballY = float(data['ballY'])
            random_point_m_x = self.random_point_m['x']
            random_point_m_y = self.random_point_m['y']
            distance = math.sqrt((ballX - random_point_m_x) ** 2 + (ballY - random_point_m_y) ** 2)
            if distance <= 5:
                return True
            else:
                return False
        else:
            return False

    def addBonus(self, data):
        elapsed_time = self.timer.get_running_time()
        self.hitB = False
        if self.bonusTime != 0 and elapsed_time >= self.bonusTime and self.randB == None:
            self.random_point_b = utils.get_random_point_in_rectangle(self.p1, self.p2, self.p3, self.p4)
            self.last_update_timeB = self.timer.time()
            self.bonusTime = 0
        if self.last_update_timeB and self.timer.time() - self.last_update_timeB <= 10:
            if self.hitBonus(data) == True:
                self.randB = random.choice(self.rand_bonus)
                self.last_update_timeB = None
                self.random_point_b = None
                self.bonusTime = elapsed_time + random.randint(2, 7)
                self.hitB = True
        if self.last_update_timeB and self.timer.time() - self.last_update_timeB >= 10:
            self.hitB = False
            self.randB = None
            self.last_update_timeB = None
            self.random_point_b = None
            self.bonusTime = elapsed_time + random.randint(2, 7)

    def addMalus(self, data):
        elapsed_time = self.timer.get_running_time()
        self.hitM = False
        if self.malusTime != 0 and elapsed_time >= self.malusTime and self.randM == None:
            self.random_point_m = utils.get_random_point_in_rectangle(self.p1, self.p2, self.p3, self.p4)
            self.last_update_timeM = self.timer.time()
            self.malusTime = 0
        if self.last_update_timeM and self.timer.time() - self.last_update_timeM <= 10:
            if self.hitMalus(data) == True:
                self.randM = random.choice(self.rand_malus)
                self.last_update_timeM = None
                self.random_point_m = None
                self.malusTime = elapsed_time + random.randint(2, 7)
                self.hitM = True
        if self.last_update_timeM and self.timer.time() - self.last_update_timeM >= 10:
            self.hitM = False
            self.randM = None
            self.last_update_timeM = None
            self.random_point_m = None
            self.malusTime = elapsed_time + random.randint(2, 7)

    def longPaddle(self, data):
        # bonus increase paddle size
        if self.randB == 'longPaddle' and data['playerBonus'] == 0:
            self.randB = 'longPaddleR'
            self.bonusStartTime = self.timer.time()  
            self.reducingR = False  
        if self.randB == 'longPaddle' and data['playerBonus'] == 1:
            self.randB = 'longPaddleL'
            self.bonusStartTime = self.timer.time()  
            self.reducingL = False  

        # right player long paddle
        if self.randB == 'longPaddleR' and not self.reducingR:
            if data['paddleHeightR'] < 20:
                data['paddleHeightR'] += 0.2
            if data['paddleHeightR'] >= 20:
                elapsed_time = self.timer.time() - self.bonusStartTime
                if elapsed_time >= 10:
                    self.reducingR = True 

        if self.reducingR:
            if data['paddleHeightR'] > 10:
                data['paddleHeightR'] -= 0.2
            if data['paddleHeightR'] <= 10:
                data['paddleHeightR'] = 10
                self.randB = None
                self.reducingR = False

        # left player long paddle
        if self.randB == 'longPaddleL' and not self.reducingL:
            if data['paddleHeightL'] < 20:
                data['paddleHeightL'] += 0.2
            if data['paddleHeightL'] >= 20:
                elapsed_time = self.timer.time() - self.bonusStartTime
                if elapsed_time >= 10:  
                    self.reducingL = True  

        if self.reducingL:
            if data['paddleHeightL'] > 10:
                data['paddleHeightL'] -= 0.2
            if data['paddleHeightL'] <= 10:
                data['paddleHeightL'] = 10
                self.randB = None
                self.reducingL = False

    def shortPaddle(self, data):
        # bonus increase paddle size
        if self.randM == 'shortPaddle' and data['playerBonus'] == 0:
            self.randM = 'shortPaddleR'
            self.malusStartTime = self.timer.time()  
            self.maximizeR = False  
        if self.randM == 'shortPaddle' and data['playerBonus'] == 1:
            self.randM = 'shortPaddleL'
            self.malusStartTime = self.timer.time()  
            self.maximizeL = False  

        # right player long paddle
        if self.randM == 'shortPaddleR' and not self.maximizeR:
            if data['paddleHeightR'] > 5:
                data['paddleHeightR'] -= 0.1
            if data['paddleHeightR'] <= 5:
                elapsed_time = self.timer.time() - self.malusStartTime
                if elapsed_time >= 10:
                    self.maximizeR = True 

        if self.maximizeR:
            if data['paddleHeightR'] < 10:
                data['paddleHeightR'] += 0.1
            if data['paddleHeightR'] >= 10:
                data['paddleHeightR'] = 10
                self.randM = None
                self.maximizeR = False

        # left player long paddle
        if self.randM == 'shortPaddleL' and not self.maximizeL:
            if data['paddleHeightL'] > 5:
                data['paddleHeightL'] -= 0.1
            if data['paddleHeightL'] <= 5:
                elapsed_time = self.timer.time() - self.malusStartTime
                if elapsed_time >= 10:  
                    self.maximizeL = True  

        if self.maximizeL:
            if data['paddleHeightL'] < 10:
                data['paddleHeightL'] += 0.1
            if data['paddleHeightL'] >= 10:
                data['paddleHeightL'] = 10
                self.randM = None
                self.maximizeL = False

    def slow(self, data):
        if self.randM == 'slow' and data['playerBonus'] == 0:
            self.randM = 'slowR'
            self.malusStartTime = self.timer.time()
        if self.randM == 'slow' and data['playerBonus'] == 1:
            self.randM = 'slowL'
            self.malusStartTime = self.timer.time()
        
        if self.randM == 'slowR':
            data['paddleSpeedR'] = 0.5
            elapsed_time = self.timer.time() - self.malusStartTime
            if elapsed_time >= 10:
                data['paddleSpeedR'] = 1.2
        
        if self.randM == 'slowL':
            data['paddleSpeedL'] = 0.5
            elapsed_time = self.timer.time() - self.malusStartTime
            if elapsed_time >= 10:
                data['paddleSpeedL'] = 1.2 

    def boost(self, data):
        if self.randB == 'boost' and data['playerBonus'] == 0:
            self.randB = 'boostR'
            self.bonusStartTime = self.timer.time()
        if self.randB == 'boost' and data['playerBonus'] == 1:
            self.randB = 'boostL'
            self.bonusStartTime = self.timer.time()
        
        # if self.randB == 'boostR':
            # elapsed_time = self.timer.time() - self.bonusStartTime
            # if elapsed_time >= 10:
            #     data['paddleSpeedR'] = 1.2
        
        # if self.randB == 'boostL':
        #     elapsed_time = self.timer.time() - self.bonusStartTime
        #     if elapsed_time >= 10:
        #         data['paddleSpeedL'] = 1.2 