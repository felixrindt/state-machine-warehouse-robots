
from level import tile_type, station_relative_pos, STATION_WALLS
from level import NORTH, EAST, WEST, SOUTH
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

def pos_at(origin, heading, direction, rounded=True):
    tx, ty = origin[0] + direction[0], origin[1] + direction[1]
    tx, ty = rotate_point((rx,ry), origin, heading)
    if rounded:
        return round(tx), round(ty)
    else:
        return tx, ty


def float_pos(robot):
    return (robot.rect.left + robot.offset[0], robot.rect.bottom + robot.offset[1])

def dist(here, there):
    return max(abs(here[0]-there[0]), abs(here[1]-there[1]))

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

        # station logic
        station_pos = station_relative_pos(self.pos)
        if tile_type(station_pos) == 'station':
            for wall in STATION_WALLS[station_pos]:
                wall= (wall - robot.heading) % 360
                if wall == NORTH:
                    self.blocked_front = True
                elif wall == WEST:
                    self.blocked_left = True
                elif wall == EAST:
                    self.blocked_right = True

        # sensors detecting robots
        for other in robots:
            if other is robot:
                continue
            if dist(self.pos, (other.rect.left, other.rect.bottom)) > 4:
                pass #continue
            to = tiles_to(float_pos(robot), robot.heading, float_pos(other), rounded=False)
            if dist(to, (0,0)) < 0.7 and robot.id < other.id:
                print("collision detected!")
                print("dist:", dist(to,(0,0)))
                print("robots where in states:")
                print(robot.state, other.state, sep="\n")
                print("robots where in positions:")
                print(robot.rect, other.rect, sep="\n")
                print("floatpos")
                print(float_pos(robot), float_pos(other), sep="\n")
                print("to:", to)

            # dont be a helpful sensor if robot is moving
            if robot.moving:
                continue

            # subtracting 0.05 because of rounding errors
            if dist(to, (0,1)) < 0.95:
                self.blocked_front = True
            if dist(to, (-1,0)) < 0.95:
                self.blocked_left = True
            if dist(to, (1,0)) < 0.95:
                self.blicked_right = True
            if dist(to, (-1,3)) < 0.95:
                self.blocked_waypoint_ahead = True
            if dist(to, (-2,1)) < 0.95:
                self.blocked_waypoint_left = True
            if dist(to, (1,2)) < 0.95:
                self.blocked_waypoint_right = True
            if dist(to, (-0.5,1.5)) < 1.45:
                self.blocked_crossroad_ahead = True
            if dist(to, (1.5,0.5)) < 1.45:
                self.blocked_crossroad_right = True

