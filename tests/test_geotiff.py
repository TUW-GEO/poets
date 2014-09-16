'''
Created on Sep 15, 2014

@author: pydev
'''
import unittest
import os
from poets.image.imagefile import bbox_img
import numpy as np
import numpy.testing as nptest


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.testfilename = os.path.join(curpath(), 'data', 'test.tiff')
        self.region = 'IT'
        self.fileExtension = '.tiff'

        self.lon = np.array([6.,   7.,   8.,   9.,  10.,  11.,  12.,  13.,
                             14.,  15.,  16., 17.,  18.])

        self.lat = np.array([48.,  47.,  46.,  45.,  44.,  43.,  42.,  41.,
                             40.,  39.,  38., 37.])

    def tearDown(self):
        pass

    def test_bbox_img(self):

        datamean = 5.2756410256410255
        datamin = 0
        datamax = 11

        data, lon_new, lat_new, _, _ = bbox_img(self.testfilename, self.region,
                                                self.fileExtension)

        nptest.assert_array_equal(lon_new, self.lon)
        nptest.assert_array_equal(lat_new, self.lat)
        assert data['dataset'].mean() == datamean
        assert data['dataset'].min() == datamin
        assert data['dataset'].max() == datamax

if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()