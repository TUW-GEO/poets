'''
Created on Sep 15, 2014

@author: pydev
'''
import unittest
import os
import poets.image.geotiff as gt
import numpy as np
from PIL import Image


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.testfile = os.path.join(curpath(), 'data', 'test.tiff')
        self.img = Image.open(self.testfile)
        self.region = 'IT'
        self.fileExtension = '.tiff'

        self.lon = 10.5
        self.lat = 40.0

        self.lon_min = 6.623967170715332
        self.lon_max = 18.514442443847656
        self.lat_min = 36.64916229248047
        self.lat_max = 47.094581604003906

        self.row = 31.922637612099024
        self.col = 21.84052307386542

    def tearDown(self):
        pass

    def test_lonlat2px_gt(self):
        row, col = gt.lonlat2px_gt(self.img, self.lon, self.lat,
                                         self.lon_min, self.lat_min,
                                         self.lon_max, self.lat_max)

        assert self.row == row
        assert self.col == col

    def test_px2lonlat_gt(self):
        lon_array = np.array([self.col])
        lat_array = np.array([self.row])
        lon, lat = gt.px2lonlat_gt(self.img, lon_array, lat_array,
                                         self.lon_min, self.lat_min,
                                         self.lon_max, self.lat_max)

        assert self.lat == lat[0]
        assert self.lon == lon[0]

if __name__ == "__main__":
    unittest.main()
