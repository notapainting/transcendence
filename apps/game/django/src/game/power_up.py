import random, time, math
import game.utils as utils
import game.consumers as game

class PowerUpManager:
    randB = None
    randM = None
    randE = None
    bonusTime = 2
    malusTime = 4
    effectTime = 30
    bonusStartTime = None
    malusStartTime = None
    last_update_timeB = None
    last_update_timeM = None
    reducingR = False
    reducingL = False
    maximizeR = False
    maximizeL = False
    # rand_bonus = ['longPaddle', 'boost']
    rand_bonus = ['boost']
    # rand_malus = ['slow', 'shortPaddle', 'invertedKey']
    rand_malus = ['slow', 'shortPaddle']
    rand_effect = ['hurricane', 'earthquake', 'glitch']
    p1 = {'x': -45, 'y': -25}
    p2 = {'x': 45, 'y': -25}
    p3 = {'x': 45, 'y': 25}
    p4 = {'x': -45, 'y': 25}
    random_point_b = None
    random_point_m = None
    random_point_e = None
    hitB = False
    hitM = False
    hitE = False

    def __init__(self):
        pass
    
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

    def addBonus(self, timer, data):
        elapsed_time = timer.get_running_time()
        self.hitB = False
        if self.bonusTime != 0 and elapsed_time >= self.bonusTime and self.randB == None:
            self.random_point_b = utils.get_random_point_in_rectangle(self.p1, self.p2, self.p3, self.p4)
            self.last_update_timeB = time.time()
            self.bonusTime = 0
        if self.last_update_timeB and time.time() - self.last_update_timeB <= 10:
            if self.hitBonus(data) == True:
                self.randB = random.choice(self.rand_bonus)
                self.last_update_timeB = None
                self.random_point_b = None
                self.bonusTime = elapsed_time + random.randint(2, 7)
                self.hitB = True
        if self.last_update_timeB and time.time() - self.last_update_timeB >= 10:
            self.hitB = False
            self.randB = None
            self.last_update_timeB = None
            self.random_point_b = None
            self.bonusTime = elapsed_time + random.randint(2, 7)
        
    def addMalus(self, timer, data):
        elapsed_time = timer.get_running_time()
        self.hitM = False
        if self.malusTime != 0 and elapsed_time >= self.malusTime and self.randM == None:
            self.random_point_m = utils.get_random_point_in_rectangle(self.p1, self.p2, self.p3, self.p4)
            self.last_update_timeM = time.time()
            self.malusTime = 0
        if self.last_update_timeM and time.time() - self.last_update_timeM <= 10:
            if self.hitMalus(data) == True:
                self.randM = random.choice(self.rand_malus)
                self.last_update_timeM = None
                self.random_point_m = None
                self.malusTime = elapsed_time + random.randint(2, 7)
                self.hitM = True
        if self.last_update_timeM and time.time() - self.last_update_timeM >= 10:
            self.hitM = False
            self.randM = None
            self.last_update_timeM = None
            self.random_point_m = None
            self.malusTime = elapsed_time + random.randint(2, 7)
    
    def longPaddle(self, data):
        # bonus increase paddle size
        if self.randB == 'longPaddle' and data['playerBonus'] == 0:
            self.randB = 'longPaddleR'
            self.bonusStartTime = time.time()  
            self.reducingR = False  
        if self.randB == 'longPaddle' and data['playerBonus'] == 1:
            self.randB = 'longPaddleL'
            self.bonusStartTime = time.time()  
            self.reducingL = False  

        # right player long paddle
        if self.randB == 'longPaddleR' and not self.reducingR:
            if data['paddleHeightR'] < 20:
                data['paddleHeightR'] += 0.2
            if data['paddleHeightR'] >= 20:
                elapsed_time = time.time() - self.bonusStartTime
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
                elapsed_time = time.time() - self.bonusStartTime
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
            self.malusStartTime = time.time()  
            self.maximizeR = False  
        if self.randM == 'shortPaddle' and data['playerBonus'] == 1:
            self.randM = 'shortPaddleL'
            self.malusStartTime = time.time()  
            self.maximizeL = False  

        # right player long paddle
        if self.randM == 'shortPaddleR' and not self.maximizeR:
            if data['paddleHeightR'] > 5:
                data['paddleHeightR'] -= 0.1
            if data['paddleHeightR'] <= 5:
                elapsed_time = time.time() - self.malusStartTime
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
                elapsed_time = time.time() - self.malusStartTime
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
            self.malusStartTime = time.time()
        if self.randM == 'slow' and data['playerBonus'] == 1:
            self.randM = 'slowL'
            self.malusStartTime = time.time()
        
        if self.randM == 'slowR':
            data['paddleSpeedR'] = 0.5
            elapsed_time = time.time() - self.malusStartTime
            if elapsed_time >= 10:
                data['paddleSpeedR'] = 1.2
        
        if self.randM == 'slowL':
            data['paddleSpeedL'] = 0.5
            elapsed_time = time.time() - self.malusStartTime
            if elapsed_time >= 10:
                data['paddleSpeedL'] = 1.2 

    def boost(self, data):
        if self.randB == 'boost' and data['playerBonus'] == 0:
            self.randB = 'boostR'
            self.bonusStartTime = time.time()
        if self.randB == 'boost' and data['playerBonus'] == 1:
            self.randB = 'boostL'
            self.bonusStartTime = time.time()
        
        # if self.randB == 'boostR':
            # elapsed_time = time.time() - self.bonusStartTime
            # if elapsed_time >= 10:
            #     data['paddleSpeedR'] = 1.2
        
        # if self.randB == 'boostL':
        #     elapsed_time = time.time() - self.bonusStartTime
        #     if elapsed_time >= 10:
        #         data['paddleSpeedL'] = 1.2 