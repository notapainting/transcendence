
import random

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