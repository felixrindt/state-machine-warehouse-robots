
import pygame
from math import floor, ceil

TILE_SIZE = 32

TILE_TYPES = {
        'station': (250,150,150),
        'waypoint': (150,150,250),
        'crossroads': (150,250,150),
        'hole': (50,50,50),
}

NORTH, WEST, SOUTH, EAST = range(0,360, 90)
STATION_WALLS = {
        (1,0): [EAST, WEST],
        (1,-1): [EAST, WEST],
        (1, -5): [WEST, SOUTH],
        (2, -5): [SOUTH, EAST],
}
STATION_WALLS.update({
        (1, y): [EAST] for y in range(-4,-1)
})
STATION_WALLS.update({
        (0, y): [NORTH, WEST, SOUTH] for y in range(-4,-1)
})
STATION_WALLS.update({
        (2,y): [EAST, WEST] for y in range(-4,0)
})

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
    for y in range(miny, miny + height):
        for x in range(minx, minx + width):
            if tile_type((x,y)) == 'station':
                draw_station_walls(screen, viewport, (x,y))

def station_relative_pos(pos):
    return pos[0] % 3, pos[1]


def draw_tile(screen, viewport, pos):
    x, y = pos
    rx, ry = tilepos_to_screenpos((x,y), viewport)
    rect = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)
    pygame.draw.rect(screen, TILE_TYPES[tile_type(pos)], rect)


def draw_station_walls(screen, viewport, pos):
    x, y = pos
    rx, ry = tilepos_to_screenpos((x,y), viewport)
    rect = pygame.Rect(rx, ry, TILE_SIZE, TILE_SIZE)
    for wall in STATION_WALLS[station_relative_pos(pos)]:
        if wall == NORTH:
            start, end = rect.topleft, rect.topright
        elif wall == EAST:
            start, end = rect.topright, rect.bottomright
        elif wall == SOUTH:
            start, end = rect.bottomright, rect.bottomleft
        elif wall == WEST:
            start, end = rect.bottomleft, rect.topleft
        pygame.draw.line(screen, TILE_TYPES['hole'], start, end, 2)

def tile_type(pos):
    x, y = pos
    if x%3 == y%3 == 0 and y>=0:
        return 'hole'
    elif y<0 or y==0 and x%3 == 1:
        return 'station' if station_relative_pos(pos) in STATION_WALLS.keys() else 'hole'
    elif x%3 == 0 or y%3 == 0:
        return 'waypoint'
    else:
        return 'crossroads'

