'''
Created on Sep 15, 2014

@author: pydev
'''
import unittest
import os
import poets.image.geotiff as gt
import numpy as np
import numpy.testing as nptest


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.testfile = os.path.join(curpath(), 'data', 'test.tiff')
        self.region = 'IT'
        self.fileExtension = '.tiff'

        self.lon = (-28, 39)
        self.lat = (32, 39)

    def tearDown(self):
        pass

    def test_lonlat2px_gt(self):
        pass

    def test_px2lonlat_gt(self):
        pass

if __name__ == "__main__":
    unittest.main()
