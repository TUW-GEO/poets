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
# Creation date: 2014-07-08

import unittest
import os
import numpy as np
import numpy.testing as nptest
from datetime import datetime
from poets.image.netcdf import save_image, write_tmp_file, clip_bbox, \
    read_image, get_properties
from netCDF4 import Dataset


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.sp_res = 90
        self.region = 'global'
        self.testfilename = os.path.join(curpath(), 'data', 'tests.nc')
        self.metadata = {'data': {'Attribute1': 'Value1'}}
        self.timestamp = datetime.today()
        self.start_date = datetime.today()
        self.temp_res = 'day'
        self.fill_value = -99
        self.variable = 'data'

        self.shape = (2, 4)
        self.mask = [[1, 0, 1, 0], [0, 1, 0, 1]]

        self.image = {}
        self.data = np.ma.array(np.ones(self.shape), mask=self.mask,
                                fill_value=self.fill_value)
        self.image['data'] = self.data

        self.bbox = np.ma.array(np.ones((1, 2)), mask=self.mask[0][0:2],
                                fill_value=self.fill_value)

        self.lon = np.array([-135., -45., 45., 135.])
        self.lat = np.array([45., -45.])
        self.lon_new = np.array([-135., -45.])
        self.lat_new = np.array([45.])

        if not os.path.exists(os.path.join(curpath(), 'data')):
            os.mkdir(os.path.join(curpath(), 'data'))

        if os.path.exists(self.testfilename):
            os.remove(self.testfilename)

    def tearDown(self):
        os.remove(self.testfilename)

    def test_save_image(self):

        save_image(self.image, self.timestamp, self.region, self.metadata,
                   self.testfilename, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        with Dataset(self.testfilename) as nc_data:
            data = nc_data.variables[self.variable]
            mask = np.array(self.mask, dtype=bool)
            nptest.assert_array_equal(self.data, data[0])
            nptest.assert_array_equal(mask, data[0].mask)
            assert data.getncattr('_FillValue') == self.fill_value
            assert data.getncattr('Attribute1') == \
                self.metadata[self.variable]['Attribute1']

    def test_write_tmp_file(self):
        write_tmp_file(self.image, self.timestamp, self.region, self.metadata,
                       self.testfilename, self.start_date, self.sp_res)

        with Dataset(self.testfilename) as nc_data:
            data = nc_data.variables[self.variable]
            mask = np.array(self.mask, dtype=bool)
            nptest.assert_array_equal(self.data, data[0])
            nptest.assert_array_equal(mask, data[0].mask)
            assert data.getncattr('_FillValue') == self.fill_value
            assert data.getncattr('Attribute1') == \
                self.metadata[self.variable]['Attribute1']

    def test_clip_bbox(self):
        lon_min = -180
        lon_max = 0
        lat_min = 0
        lat_max = 90

        write_tmp_file(self.image, self.timestamp, self.region, self.metadata,
                       self.testfilename, self.start_date, self.sp_res)

        data, lon_new, lat_new, timestamp, metadata = clip_bbox(
            self.testfilename, lon_min, lat_min, lon_max, lat_max)

        timediff = self.timestamp - timestamp

        nptest.assert_array_equal(self.bbox, data[self.variable])
        nptest.assert_array_equal(self.lon_new, lon_new)
        nptest.assert_array_equal(self.lat_new, lat_new)
        assert timediff.days == 0
        assert metadata == self.metadata

    def test_read_image(self):

        save_image(self.image, self.timestamp, self.region, self.metadata,
                   self.testfilename, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        image, lon, lat, metadata = read_image(self.testfilename,
                                               self.variable,
                                               self.timestamp)

        nptest.assert_array_equal(image, self.data)
        nptest.assert_array_equal(lon, self.lon)
        nptest.assert_array_equal(lat, self.lat)
        assert metadata == self.metadata[self.variable]

    def test_get_properties(self):

        save_image(self.image, self.timestamp, self.region, self.metadata,
                   self.testfilename, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        variables, dimensions, period = get_properties(self.testfilename)

        timediff1 = self.timestamp - period[0]
        timediff2 = self.timestamp - period[1]

        assert variables[0] == self.variable
        assert dimensions == ['lat', 'lon', 'time']
        assert timediff1.days == 0
        assert timediff2.days == 0


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
