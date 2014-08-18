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
import numpy.testing as nptest
import numpy as np
import pandas as pd
from pandas.util.testing import assert_frame_equal
from datetime import datetime
from poets.image.netcdf import save_image
from poets.image.resampling import resample_to_shape, resample_to_gridpoints, \
    average_layers


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.sp_res = 60
        self.region = 'UG'
        self.testfilename = os.path.join(curpath(), 'data', 'tests.nc')
        self.metadata = {'data': {'Attribute1': 'Value1'}}
        self.timestamp = datetime.today()
        self.start_date = datetime.today()
        self.temp_res = 'day'
        self.fill_value = -99
        self.variable = 'data'

        self.shape = (3, 6)
        self.mask = np.array([[1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1],
                              [1, 0, 1, 0, 1, 0]])

        self.image = {}
        self.data = np.ma.array(np.ones(self.shape), mask=self.mask,
                                fill_value=self.fill_value)
        self.image['data'] = self.data

        if not os.path.exists(os.path.join(curpath(), 'data')):
            os.mkdir(os.path.join(curpath(), 'data'))

        if os.path.exists(self.testfilename):
            os.remove(self.testfilename)

    def tearDown(self):
        if os.path.exists(self.testfilename):
            os.remove(self.testfilename)

    def test_resample_to_shape(self):

        reslon = np.array([[30.]])
        reslat = np.array([[0.]])

        resimg = {'data': np.ma.array([[self.data[1][3].data]],
                                      mask=self.mask[1][3],
                                      fill_value=self.fill_value)}

        save_image(self.image, self.timestamp, 'global', self.metadata,
                   self.testfilename, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        data, dest_lon, dest_lat, gpis, timestamp, metadata = \
            resample_to_shape(self.testfilename, self.region, self.sp_res,
                              nan_value=self.fill_value,
                              dest_nan_value=self.fill_value)

        timediff = self.timestamp - timestamp

        nptest.assert_array_equal(data, resimg)
        assert dest_lon[0][0] == reslon
        assert dest_lat[0][0] == reslat
        assert gpis[0] == 0
        assert timediff.days == 0
        assert metadata == self.metadata

    def test_resample_to_gridpoints(self):

        resgp = pd.DataFrame(np.array(([[30., 0., self.fill_value]])),
                             columns=['lon', 'lat', 'data'])

        save_image(self.image, self.timestamp, 'global', self.metadata,
                   self.testfilename, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        gridpoints = resample_to_gridpoints(self.testfilename, self.region,
                                            self.sp_res)

        assert_frame_equal(gridpoints, resgp)

    def test_average_layers(self):

        avgimg = self.image['data'] * 2

        image = np.ma.array([self.image['data'], self.image['data'] * 3])

        img = average_layers(image, self.fill_value)

        nptest.assert_array_equal(img, avgimg)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
