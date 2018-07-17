#!/usr/sbin/python3

import unittest
import level
import sensor


class TestLevel(unittest.TestCase):

    def test_tiletype_waypoint(self):
        self.assertEqual(level.tile_type((2,0)), 'waypoint')
        self.assertEqual(level.tile_type((0,1)), 'waypoint')


class TestSensor(unittest.TestCase):

    def test_tiles_to(self):
        self.assertEqual(sensor.tiles_to((1,1), 0, (-4,3)), (-5,2))
        self.assertEqual(sensor.tiles_to((1,1), 90, (-4,3)), (2,5))

    def test_rotate_point(self):
        self.assertEqual(sensor.rotate_point((-4,3), (1,1), -90), (3,6))

if __name__ == '__main__':
    unittest.main()
