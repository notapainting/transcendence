
import random, time

class Timer:
    _startTime = None
    _pauseTime = None
    _pause = True

    def __init__(self, verbose=False) -> None:
        self.verbose = verbose

    def paused(self):
        return self._pause

    def get_running_time(self):
        if self._startTime is None:
            value = 0.0
        elif self._pause is True:
            value = self._pauseTime - self._startTime
        else:
            value = time.time() - self._startTime
        if self.verbose is True:
            print(f"time is : {value:.3f}")
        return value

    def pause(self):
        if self._pause is False:
            self._pauseTime = time.time()
            self._pause = True
            if self.verbose is True:
                self.get_running_time()

    def resume(self):
        if self._startTime is None:
            self._startTime = time.time()
            self._pause = False
            if self.verbose is True:
                print(f"start timer")
        else:
            if self._pause is True:
                self._startTime += (time.time() - self._pauseTime)
                self._pause = False

def is_clockwise(points):
    p1, p2, p3, p4 = points
    sum = (p2['x'] - p1['x']) * (p2['y'] + p1['y']) + \
          (p3['x'] - p2['x']) * (p3['y'] + p2['y']) + \
          (p4['x'] - p3['x']) * (p4['y'] + p3['y']) + \
          (p1['x'] - p4['x']) * (p1['y'] + p4['y'])
    return sum > 0

def get_random_point_in_rectangle(p1, p2, p3, p4):
    r1 = random.random()
    r2 = random.random()

    points = [p1, p2, p3, p4]
    if is_clockwise(points):
        points.reverse()

    a, b, c, d = points

    x1 = a['x'] + r1 * (b['x'] - a['x'])
    y1 = a['y'] + r1 * (b['y'] - a['y'])
    x2 = d['x'] + r1 * (c['x'] - d['x'])
    y2 = d['y'] + r1 * (c['y'] - d['y'])

    x = x1 + r2 * (x2 - x1)
    y = y1 + r2 * (y2 - y1)

    return {'x': x, 'y': y}