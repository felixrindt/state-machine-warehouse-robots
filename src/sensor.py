
from level import tile_type
from math import pi, sin, cos


def rotate_point(point, around, degrees):
    x, y = point[0] - around[0], point[1] - around[1]
    rad = degrees * pi / 180
    a, b = cos(rad), -sin(rad)
    c, d = sin(rad), cos(rad)
    x, y = a*x+b*y, c*x + d*y
    return x+around[0], y+around[1]


def tiles_to(origin, heading, target, rounded=True):
    rx, ry = origin
    tx,ty = rotate_point(target, origin, -heading)
    if rounded:
        return round(tx-rx), round(ty-ry)
    else:
        return tx-rx, ty-ry

def float_pos(robot):
    return (robot.rect.left + robot.offset[0], robot.rect.bottom + robot.offset[1])

def dist(here, there):
    return abs(here[0]-there[0]) + abs(here[1]-there[1])

class SensorData(object):
    
    def __init__(self, robot, robots):
        self.pos = (robot.rect.left, robot.rect.bottom)
        self.pos_type = tile_type(self.pos)
        self.pos_orientation = robot.heading
        self.pos_float = float_pos(robot)
        self.blocked_front = False
        self.blocked_left = False
        self.blicked_right = False
        self.blocked_waypoint_ahead = False
        self.blocked_waypoint_left = False
        self.blocked_waypoint_right = False
        self.blocked_crossroad_ahead = False
        self.blocked_crossroad_right = False

        # TODO implement tile type check
        for other in robots:
            if other is robot:
                continue
            to = tiles_to(self.pos, robot.heading, float_pos(other), rounded=False)
            if dist(to, (0,1)) < 1:
                self.blocked_front = True
            if dist(to, (-1,0)) < 1:
                self.blocked_left = True
            if dist(to, (1,0)) < 1:
                self.blicked_right = True
            if dist(to, (-1,3)) < 1:
                self.blocked_waypoint_ahead = True
            if dist(to, (-2,1)) < 1:
                self.blocked_waypoint_left = True
            if dist(to, (1,2)) < 1:
                self.blocked_waypoint_right = True
            if dist(to, (-0.5,1.5)) < 2:
                self.blocked_crossroad_ahead = True
            if dist(to, (1.5,0.5)) < 1:
                self.blocked_crossroad_right = True
