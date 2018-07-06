#!/usr/sbin/python

import sys, pygame
import random

import robot as bots
import level
from sensor import SensorData

FRAME_RATE = 60
pygame.init()

class Warehouse(object):

    def run(self):
        size = width, height = 960, 620
        viewport = pygame.Rect(0, -height, width, height)

        screen = pygame.display.set_mode(size)

        clock = pygame.time.Clock()

        robots = [bots.Robot(x, y, self) for x in range(2, 28, 3) for y in range(0, 6, 3)]

        #robots = [bots.Robot(2,0,self)]

        for r in robots:
            self.assign_random_target(r)

        while 1:
            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()

            """ LOGIC """

            for r in robots:
                r.sensorData(SensorData(r, robots))

            """ ANIMATION """

            for robot in robots:
                robot.tick()

            """ DRAWING """
            screen.fill((0,0,0))
            level.draw_tiles(screen, viewport)
            for r in robots:
                r.draw(screen, viewport)

            """ DISPLAY AND TIMING"""
            pygame.display.flip()
            clock.tick(FRAME_RATE)

    def arrived(self, robot):
        robot.unload()

    def unloaded(self, robot):
        self.assign_random_target(robot)

    def assign_random_target(self, robot):
        x = 0 + 3 * random.randint(0,9)
        y = 1 + 3 * random.randint(0,5)
        robot.driveTo((x,y))


if __name__=="__main__":
    w = Warehouse()
    w.run()
