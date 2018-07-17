#!/usr/sbin/python

import sys, pygame
import random

import robot as bots
import level
from level import TILE_SIZE, CHARGERS_PER_STATION
from sensor import SensorData

FRAME_RATE = 60
SENSOR_RATE = 20

class Warehouse(object):

    def __init__(self):
        self.running = True
        pygame.init()

    def quit(self):
        self.running = False

    def run(self):
        size = width, height = 970, 620
        viewport = pygame.Rect(0, -height + round((2.2+CHARGERS_PER_STATION)*TILE_SIZE), width, height)
        screen = pygame.display.set_mode(size)

        robots = [bots.Robot(x, y) for x in range(0, width//TILE_SIZE, 3) for y in range(-1-CHARGERS_PER_STATION, -1, 1)]
        #robots = [bots.Robot(2,0,self)]

        clock = pygame.time.Clock()
        self.paused = False
        self.tick = 0

        srates = {bot: round(SENSOR_RATE * (0.2 + 0.8 * random.random())) for bot in robots}

        from time import time
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT: sys.exit()
                if event.type == pygame.VIDEORESIZE:
                    viewport.size = event.size
                    size = event.size
                    screen = pygame.display.set_mode(size, pygame.RESIZABLE)
                if event.type == pygame.KEYDOWN and event.key == 32:
                    self.paused = not self.paused
            pressed = pygame.key.get_pressed()
            viewport.y += pressed[pygame.K_DOWN] - pressed[pygame.K_UP]
            viewport.x += pressed[pygame.K_RIGHT] - pressed[pygame.K_LEFT]

            """ LOGIC """


            if not self.paused:

                for idx, r in enumerate(robots):
                    modulus = FRAME_RATE//srates[r]
                    if self.tick % modulus == idx % modulus:
                        sd = SensorData(r, robots)
                        if False and sd.collided:
                            self.paused = True
                        r.sensorData(sd)
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
            self.tick += 1


if __name__=="__main__":
    warehouse = Warehouse()
    warehouse.run()
