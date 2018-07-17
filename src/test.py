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

if __name__ == '__main__':
    unittest.main()
