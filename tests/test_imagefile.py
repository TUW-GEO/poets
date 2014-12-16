# Copyright (c) 2014, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Vienna University of Technology - Department of
#   Geodesy and Geoinformation nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-08-14

import unittest
import os
import poets.image.imagefile as imf
import numpy as np
import numpy.testing as nptest
from PIL import Image


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.testfile = os.path.join(curpath(), 'data', 'test')
        self.img = Image.open(os.path.join(self.testfile + '.png'))
        self.region = ['NZ', 'US', 'RS', 'IT']
        self.fileExtension = ['.png', '.tif']

        self.lon_array = [np.array([165.5, 166.5, 167.5, 168.5, 169.5, 170.5,
                                   171.5, 172.5, 173.5, 174.5, 175.5, 176.5,
                                   177.5, 178.5, 179.5, -179.5, -178.5, -177.5,
                                   - 176.5, -175.5]), np.array([]),
                          np.array([]), np.array([6.5, 7.5, 8.5, 9.5,
                                                  10.5, 11.5, 12.5, 13.5,
                                                  14.5, 15.5, 16.5, 17.5,
                                                  18.5])]

        self.lat_array = [np.array([-34.5, -35.5, -36.5, -37.5, -38.5, -39.5,
                                   - 40.5, -41.5, -42.5, -43.5, -44.5, -45.5,
                                   - 46.5, -47.5, -48.5, -49.5, -50.5, -51.5,
                                   - 52.5]), np.array([]), np.array([]),
                          np.array([47.5, 46.5, 45.5, 44.5, 43.5, 42.5,
                                    41.5, 40.5, 39.5, 38.5, 37.5, 36.5])]

        self.row_array = np.array([10, 20, 30, 40])
        self.col_array = np.array([10, 20, 30, 40])

        self.lon = 170
        self.lat = -45

        self.row = 135.0
        self.col = 350.0

        self.row_rearr = 135.0
        self.col_rearr = 170.0

    def tearDown(self):
        pass

    def test_get_layer_extent(self):
            lon_min, lat_min, lon_max, lat_max = \
                imf.get_layer_extent(os.path.join(self.testfile + '.png'))

            assert (lon_min, lon_max) == (0.0, 360.0)
            assert (lat_min, lat_max) == (180.0, 0.0)

    def test_bbox_img(self):

        datamean = [244.88947368421051, [], [], 224.75]
        datamin = [112, [], [], 141]
        datamax = [255, [], [], 255]

        for fExt in self.fileExtension:
            for ind in [0, 3]:
                if fExt == '.tif':
                    datamean = [0.94736842105263153, [], [],
                                     5.2756410256410255]
                    datamin = [0, [], [], 0]
                    datamax = [12, [], [], 11]

                data, lon_new, lat_new, _, _ = imf.bbox_img(os.path.join(self\
                                                            .testfile + fExt),
                                                            self.region[ind],
                                                            fExt)

                nptest.assert_array_equal(lon_new, self.lon_array[ind])
                nptest.assert_array_equal(lat_new, self.lat_array[ind])
                assert data['dataset'].mean() == datamean[ind]
                assert data['dataset'].min() == datamin[ind]
                assert data['dataset'].max() == datamax[ind]

    def test_lonlat2px(self):

        row, col = imf.lonlat2px(self.img, self.lon, self.lat)

        assert row == self.row
        assert col == self.col

    def test_lonlat2px_rearr(self):

        row, col = imf.lonlat2px_rearr(self.img, self.lon, self.lat)

        assert row == self.row_rearr
        assert col == self.col_rearr

    def test_px2lonlat(self):
        lon1 = np.array([-170., -160., -150., -140.])
        lat1 = np.array([80., 70., 60., 50.])
        lon, lat = imf.px2lonlat(self.img, self.col_array, self.row_array)

        nptest.assert_array_equal(lon1, lon)
        nptest.assert_array_equal(lat1, lat)

    def test_px2lonlat_rearr(self):
        lon1 = np.array([10, 20, 30, 40])
        lat1 = np.array([80., 70., 60., 50.])
        lon, lat = imf.px2lonlat_rearr(self.img, self.col_array,
                                       self.row_array)

        nptest.assert_array_equal(lon1, lon)
        nptest.assert_array_equal(lat1, lat)

    def test_rearrange_img(self):
        greyval = 139
        img_rearr = imf.rearrange_img(self.img)

        assert greyval == img_rearr.getpixel((self.col_rearr, self.row_rearr))

    def test_dateline_country(self):
        lon_min1 = [165.87, 173.18333333333334, 19.633333333333333]
        lon_max1 = [-175.83333333333334, -66.98353057222222, -169.065]

        for ind, region in enumerate(self.region[0:-1]):
            lon_min, lon_max = imf.dateline_country(region)

            assert lon_min == lon_min1[ind]
            assert lon_max == lon_max1[ind]

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
