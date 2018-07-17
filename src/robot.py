
from math import pi, sin, cos
import random
import pygame

from level import TILE_SIZE, CHARGERS_PER_STATION, tilepos_to_screenpos
from level import NORTH, EAST, SOUTH, WEST
from sensor import tiles_to
from main import FRAME_RATE

texture = pygame.image.load("res/robot{}.png".format(TILE_SIZE))
texture_unloading = pygame.image.load("res/robot_unloading{}.png".format(TILE_SIZE))
texture_loaded = pygame.image.load("res/robot_loaded{}.png".format(TILE_SIZE))

class Processor(object):

    BATTERY_LOW = 0.5
    BATTERY_HIGH = 1.0

    def __init__(self, robot):
        self.robot = robot
        self.robot.processor = self
        self.state = 'charging'
        self.chargeport_pos = self.robot.rect.left//3*3, self.robot.rect.bottom
        self.station_entrance_pos = self.chargeport_pos[0] + 1, 0
        self.station_exit_pos = self.chargeport_pos[0] + 2, 0

    def tick(self):
        if self.state == 'charging':
            self.robot.battery += 0.12 / FRAME_RATE
            if self.robot.battery >= Processor.BATTERY_HIGH:
                self.enque()

    def enque(self):
        self.robot.driveTo(self.station_exit_pos)
        self.state = 'queueing'

    def arrived(self):
        if self.state == 'queueing':
            self.deliver()
        elif self.state == 'delivering':
            self.robot.loaded = False
            self.robot.unload()
        elif self.state == 'returning_to_station':
            if self.robot.battery < Processor.BATTERY_LOW:
                self.charge()
            else:
                self.enque()
        elif self.state == 'returning_to_charging':
            self.state = 'charging'

    def charge(self):
        self.robot.driveTo(self.chargeport_pos)
        self.state = 'returning_to_charging'

    def return_to_station(self):
        self.state = 'returning_to_station'
        self.robot.driveTo(self.station_entrance_pos)

    def unloaded(self):
        self.return_to_station()

    def deliver(self):
        self.state = 'delivering'
        self.robot.loaded = True
        x = 0 + 3 * random.randint(0,12)
        y = 1 + 3 * random.randint(1,CHARGERS_PER_STATION)
        self.robot.driveTo((x,y))


class Robot(object):

    ROBOCOUNT = 0

    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y-1, 1, 1)
        self.state = "stopped"
        self.offset = [0,0]
        self.heading = 0
        self.unloading = False
        self.moving = False
        self.target = None
        self.moves = []
        self.data = None
        self.processor = Processor(self)
        Robot.ROBOCOUNT += 1
        self.id = Robot.ROBOCOUNT

        self.loaded = False
        self.battery = 0.8
        self.speed = 4.0  # tiles per second
        self.unload_time = 0.5  # seconds

    def __str__(self):
        return "Robot {}".format(self.id)

    def draw(self, screen, viewport):
        if self.target:
            self._draw_line_to(screen, viewport, self.target, (250,250,250))

        x, y = self.rect.left, self.rect.bottom
        x += self.offset[0]
        y += self.offset[1]
        rx, ry = tilepos_to_screenpos((x,y), viewport)
        rect = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)

        t = texture
        if self.unloading:
            t = texture_unloading
        elif self.loaded:
            t = texture_loaded

        surface = pygame.transform.rotate(t, self.heading)
        srect = surface.get_rect()
        srect.center = rect.center
        screen.blit(surface, srect)

        pygame.draw.arc(screen, (250,250,250), rect.inflate(-16,-16), 0, max(0,self.battery)*2*pi, 4)
        # if self.data.blocked_crossroad_ahead: pygame.draw.circle(screen, (255,0,0), (rx+16,ry+16), 8, 2)

    def _draw_line_to(self, screen, viewport, pos, color):
        rx, ry = self.rect.left, self.rect.bottom
        rx += self.offset[0] + 0.5
        ry += self.offset[1] - 0.5
        rx, ry = tilepos_to_screenpos((rx,ry), viewport)
        
        tx, ty = pos[0] + 0.5, pos[1] - 0.5
        tx, ty = tilepos_to_screenpos((tx,ty), viewport)

        pygame.draw.line(screen, color, (rx,ry), (tx,ty))


    def tick(self):
        self.processor.tick()

        self.moving = len(self.moves) > 0
        if len(self.moves):
            finished = self.moves[0].tick(self)
            if finished:
                self.battery -= 0.005
                del self.moves[0]
                self.offset[0] = round(self.offset[0])
                self.offset[1] = round(self.offset[1])
                dx, self.offset[0] = self.offset[0] // 1, self.offset[0] % 1
                dy, self.offset[1] = self.offset[1] // 1, self.offset[1] % 1
                self.rect.move_ip(dx, dy)

    def driveForward(self):
        def forward(robot, data):
            steps, remaining = data
            if robot.heading == NORTH:
                robot.offset[1] = 1 - remaining/steps
            elif robot.heading == WEST:
                robot.offset[0] = -1 + remaining/steps
            elif robot.heading == SOUTH:
                robot.offset[1] = -1 + remaining/steps
            elif robot.heading == EAST:
                robot.offset[0] = 1 - remaining/steps
            return remaining==0, (steps, remaining -1 )

        steps = FRAME_RATE // self.speed
        self.moves.append(Move(forward, (steps, steps)))

    def turnLeft(self):
        steps = FRAME_RATE // self.speed
        def left(robot, data):
            steps, remaining = data
            robot.heading += 90 / steps
            if remaining == 1: 
                robot.heading = round(robot.heading) % 360
            return remaining==1, (steps, remaining -1 )
        self.moves.append(Move(left, (steps, steps)))

    def turnRight(self):
        steps = FRAME_RATE // self.speed
        def right(robot, data):
            steps, remaining = data
            robot.heading -= 90 / steps
            if remaining == 1: 
                robot.heading = round(robot.heading) % 360
            return remaining==1, (steps, remaining -1 )
        self.moves.append(Move(right, (steps, steps)))

    def start_unloading(self):
        steps = FRAME_RATE * self.unload_time
        def unload(robot, data):
            steps, remaining = data
            if steps == remaining:
                robot.unloading = True
            elif remaining == 1: 
                robot.unloading = False
                robot.unloaded()
                return True, (steps, remaining -1 )
            return False, (steps, remaining -1 )
        self.moves.append(Move(unload, (steps, steps)))

    def driveTo(self, target):
        if self.state != 'stopped':
            return
        self.target = target
        self.state = 'driving.initial'

    def unloaded(self):
        if self.state == 'unloading':
            self.state = 'stopped'
            self.processor.unloaded()

    def unload(self):
        # movements are blocking
        if self.moving:
            return
        if self.state == 'stopped':
            self.start_unloading()
            self.state = 'unloading'

    def sensorData(self, data):
        self.data = data
        # movements are blocking
        if self.moving:
            return

        if self.state == 'stopped':
            pass
        elif self.state == 'unloading':
            pass
        elif self.state == 'driving.initial':
            if self._target_reached():
                self.state = 'stopped'
                self.target = None
                self.processor.arrived()
            else:
                if data.pos_type == 'waypoint':
                    self.state = 'driving.waypoint.initial'
                elif data.pos_type == 'station':
                    self._station_behavior()
        elif self.state.startswith('driving.waypoint'):
            return self._states_waypoint()
        else:
            print("unknown state", self.state)

    def _station_behavior(self):
        to_charging_below = self.target[0]%3 ==0 and self.target[0] + 1 == self.data.pos[0] and self.target[1] <= self.data.pos[1]
        if to_charging_below:
            if self.data.pos[1] == self.target[1] and self.data.pos_orientation != WEST:
                self.turnRight()
            elif not self.data.blocked_front:
                self.driveForward()
        else:
            direction, left = self._station_traffic_direction()
            if self.data.pos_orientation != direction:
                if left:
                    self.turnLeft()
                else:
                    self.turnRight()
            elif not self.data.blocked_front:
                self.driveForward()
                
    def _station_traffic_direction(self):
        """ return tuple of which direction to go and wether to use left turns for doing so (else use right turns) """
        xmod3 = self.data.pos[0] % 3
        if xmod3 == 0 or self.data.pos[1] == -2-CHARGERS_PER_STATION and xmod3 == 1:
            return EAST, True
        elif xmod3 == 1:
            return SOUTH, False
        else:
            return NORTH, True

    def _states_waypoint(self):
        direction = self._target_direction()
        if self.state == 'driving.waypoint.initial':
            if direction == 'behind':
                if self.data.blocked_left:
                    self.state = 'driving.waypoint.checkpriority'
                else:
                    self.turnLeft()
                    self.state = 'driving.waypoint.turnaround.wait'
            else:
                self.state = 'driving.waypoint.checkpriority'
        elif self.state == 'driving.waypoint.turnaround.wait':
            if not (self.data.blocked_crossroad_right or self.data.blocked_front):
                self.driveForward()
                self.turnLeft()
            else:
                self.turnRight()
            self.state = 'driving.initial'
        elif self.state == 'driving.waypoint.checkpriority':
            right_before_left = not self.data.blocked_waypoint_right
            stalemate = self.data.blocked_waypoint_right and self.data.blocked_waypoint_ahead and self.data.blocked_waypoint_left and self.data.pos_orientation in [NORTH, SOUTH]
            crossroad_free = not self.data.blocked_crossroad_ahead
            if (right_before_left or stalemate) and crossroad_free:
                self.driveForward()
                if direction == 'right':
                    self.turnRight()
                    self.state = 'driving.waypoint.leavecrossroad'
                elif direction == 'ahead' or direction == 'behind':
                    self.driveForward()
                    self.state = 'driving.waypoint.leavecrossroad'
                elif direction == 'left':
                    self.driveForward()
                    self.turnLeft()
                    self.state = 'driving.waypoint.finishleftturn'
        elif self.state == 'driving.waypoint.finishleftturn':
            if not self.data.blocked_front:
                self.driveForward()
                self.state = 'driving.waypoint.leavecrossroad'
        elif self.state == 'driving.waypoint.leavecrossroad':
            if not self.data.blocked_front:
                self.driveForward()
                self.state = 'driving.initial'
            else:
                self.turnLeft()
                self.state = 'driving.waypoint.finishleftturn'


    def _target_reached(self):
        return self.target == self.data.pos

    def _target_direction(self):
        tx, ty= tiles_to(self.data.pos, self.heading, self.target)
        result = None

        if ty > 3 or ty == 3 and tx in [-1, 0]:
            result = 'ahead'
        elif ty == 0 and tx == -1:
            result = 'behind'
        elif ty < 0:
            result = 'behind'
        elif tx > 0:
            result = 'right'
        elif tx < -1:
            result = 'left'
        return result


class Move(object):

    function = None
    data = None

    def __init__(self, function, initial_data):
        self.function = function
        self.data = initial_data

    def tick(self, robot):
        """return true when finished"""
        finished, new_data = self.function(robot, self.data)
        self.data = new_data
        return finished
