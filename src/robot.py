
from math import pi, sin, cos
import pygame

from level import TILE_SIZE, tilepos_to_screenpos
from sensor import tiles_to
from main import FRAME_RATE

texture = pygame.image.load("res/robot{}.png".format(TILE_SIZE))
texture_unloading = pygame.image.load("res/robot_unloading{}.png".format(TILE_SIZE))


class Robot(object):

    ROBOCOUNT = 0

    def __init__(self, x, y, processor):
        self.rect = pygame.Rect(x, y-1, 1, 1)
        self.state = "stopped"
        self.offset = [0,0]
        self.heading = 0
        self.unloading = False
        self.moving = False
        self.target = None
        self.moves = []
        self.data = None
        self.processor = processor
        Robot.ROBOCOUNT += 1
        self.id = Robot.ROBOCOUNT

        self.speed = 4.0  # tiles per second
        self.unload_time = 0.5  # seconds

    def __str__(self):
        return "Robot {}".format(self.id)

    def draw(self, screen, viewport):
        x, y = self.rect.left, self.rect.bottom
        x += self.offset[0]
        y += self.offset[1]
        rx, ry = tilepos_to_screenpos((x,y), viewport)
        rect = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)
        t = texture_unloading if self.unloading else texture
        surface = pygame.transform.rotate(t, self.heading)
        srect = surface.get_rect()
        srect.center = rect.center
        screen.blit(surface, srect)

        self._draw_target_line(screen, viewport)

        if self.data.blocked_crossroad_ahead:
            pygame.draw.circle(screen, (255,0,0), (rx+16,ry+16), 8, 2)

    def _draw_target_line(self, screen, viewport):
        rx, ry = self.rect.left, self.rect.bottom
        rx += self.offset[0] + 0.5
        ry += self.offset[1] - 0.5
        rx, ry = tilepos_to_screenpos((rx,ry), viewport)
        
        tx, ty = self.target[0] + 0.5, self.target[1] - 0.5
        tx, ty = tilepos_to_screenpos((tx,ty), viewport)

        pygame.draw.line(screen, (250,250,250), (rx,ry), (tx,ty))


    def tick(self):
        self.moving = len(self.moves) > 0
        if len(self.moves):
            finished = self.moves[0].tick(self)
            if finished:
                del self.moves[0]
                self.offset[0] = round(self.offset[0])
                self.offset[1] = round(self.offset[1])
                dx, self.offset[0] = self.offset[0] // 1, self.offset[0] % 1
                dy, self.offset[1] = self.offset[1] // 1, self.offset[1] % 1
                self.rect.move_ip(dx, dy)

    def driveForward(self):
        def forward(robot, data):
            steps, remaining = data
            if robot.heading == 0:
                robot.offset[1] = 1 - remaining/steps
            elif robot.heading == 90:
                robot.offset[0] = -1 + remaining/steps
            elif robot.heading == 180:
                robot.offset[1] = -1 + remaining/steps
            elif robot.heading == 270:
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
            self.processor.unloaded(self)

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

        # print(str(self), "is in state", self.state)

        if self.state == 'stopped':
            pass
        elif self.state == 'unloading':
            pass
        elif self.state == 'driving.initial':
            if self._target_reached():
                self.state = 'stopped'
                self.processor.arrived(self)
            else:
                if data.pos_type == 'waypoint':
                    self.state = 'driving.waypoint.initial'
                # TODO add other tile types
                if data.pos_type == 'station':
                    self.turnLeft()
                    self.state = 'driving.waypoint.turnaround.wait'
        elif self.state.startswith('driving.waypoint.'):
            return self._waypoint()

    def _waypoint(self):
        if self.state == 'driving.waypoint.initial':
            direction = self._target_direction()
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
            stalemate = self.data.blocked_waypoint_right and self.data.blocked_waypoint_ahead and self.data.blocked_waypoint_left and self.data.pos_orientation in [0, 180]
            crossroad_free = not self.data.blocked_crossroad_ahead
            if (right_before_left or stalemate) and crossroad_free:
                self.driveForward()
                direction = self._target_direction()
                if direction == 'right':
                    self.turnRight()
                    self.state = 'driving.waypoint.leavecrossroad'
                elif direction == 'ahead' or direction == 'behind':
                    self.driveForward()
                    self.state = 'driving.waypoint.leavecrossroad'
                elif direction == 'left':
                    self.driveForward()
                    self.turnLeft()
                    self.driveForward()
                    self.state = 'driving.waypoint.leavecrossroad'
        elif self.state == 'driving.waypoint.leavecrossroad':
            if not self.data.blocked_front:
                self.driveForward()
                self.state = 'driving.initial'
            else:
                self.turnLeft()
                self.driveForward()



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
