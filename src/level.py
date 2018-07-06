
import pygame
from math import floor, ceil

TILE_SIZE = 32

TILE_TYPES = {
        'station': (250,150,150),
        'waypoint': (150,150,250),
        'crossroads': (150,250,150),
        'hole': (100,100,100),
}

def tilepos_to_screenpos(tpos, viewport):
    rx, ry = tpos
    rx = round(rx * TILE_SIZE - viewport.x)
    ry = round((-ry-1) * TILE_SIZE - viewport.y)
    return rx, ry

def draw_tiles(screen, viewport):
    minx = floor(viewport.x / TILE_SIZE)
    miny = -ceil(viewport.bottom / TILE_SIZE)
    width = ceil(viewport.w / TILE_SIZE + 1)
    height = ceil(viewport.h / TILE_SIZE + 1)
    for y in range(miny, miny + height):
        for x in range(minx, minx + width):
            draw_tile(screen, viewport, (x,y))


def draw_tile(screen, viewport, pos):
    x, y = pos
    rx, ry = tilepos_to_screenpos((x,y), viewport)
    rect = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, TILE_TYPES[tile_type(pos)], rect)

def tile_type(pos):
    x, y = pos
    if x%3 == y%3 == 0:
        return 'hole'
    elif y<0 or y==0 and x%3 == 1:
        return 'station'
    elif x%3 == 0 or y%3 == 0:
        return 'waypoint'
    else:
        return 'crossroads'

