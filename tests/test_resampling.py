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
import h5py
import numpy.testing as nptest
import numpy as np
import poets.grid.grids as gr
import matplotlib.pyplot as plt
from datetime import datetime
from poets.image.netcdf import save_image
from poets.image.resampling import resample_to_shape, average_layers


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.sp_res = 60
        self.region = 'UG'
        self.timestamp = datetime.today()
        self.start_date = datetime.today()
        self.temp_res = 'day'
        self.fill_value = -99
        self.variable = 'data'

        # create image
        self.shape = (3, 6)
        self.mask = np.array([[1, 0, 1, 0, 1, 0], [0, 1, 0, 1, 0, 1],
                              [1, 0, 1, 0, 1, 0]])

        self.image = {}
        self.data = np.ma.array(np.ones(self.shape), mask=self.mask,
                                fill_value=self.fill_value)
        self.data.data[np.where(self.mask == 1)] = self.fill_value

        self.image['data'] = self.data
        self.image['data2'] = self.data * 2

        # create metadata
        self.metadata = {'data': {'Attribute1': 'Value1'},
                         'data2': {'Attribut2': 'Value2'},
                         'data3': {'Attribut3': 'Value3'}}

        if not os.path.exists(os.path.join(curpath(), 'data')):
            os.mkdir(os.path.join(curpath(), 'data'))

        self.grid = gr.ShapeGrid(self.region, self.sp_res)
        self.globalgrid = gr.RegularGrid(sp_res=self.sp_res)

        # Build NetCDF testfile
        self.ncfile = os.path.join(curpath(), 'data', 'test_nc.nc')
        if os.path.exists(self.ncfile):
            os.remove(self.ncfile)

        save_image(self.image, self.timestamp, 'global', self.metadata,
                   self.ncfile, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        # Build HDF5 testfile
        self.h5file = os.path.join(curpath(), 'data', 'tests_hdf5.h5')
        if os.path.exists(self.h5file):
            os.remove(self.h5file)

        with h5py.File(self.h5file, 'w') as hdf5_file:

            group = hdf5_file.create_group('group')
            for dataset_name in self.image.keys():
                attributes = self.metadata[dataset_name]
                write_data = self.image[dataset_name]
                dataset = group.create_dataset(dataset_name,
                                               write_data.shape,
                                               write_data.dtype,
                                               write_data)
                for key in attributes:
                    dataset.attrs[key] = attributes[key]

        # Build png Testfile
        self.pngfile = os.path.join(curpath(), 'data', 'test_png.png')
        if os.path.exists(self.pngfile):
            os.remove(self.pngfile)

        n = 60
        pngimg = np.kron(np.copy(self.data), np.ones((n, n)))
        pngimg[pngimg == self.fill_value] = np.NAN
        plt.imsave(self.pngfile, pngimg)

    def tearDown(self):

        if os.path.exists(self.ncfile):
            os.remove(self.ncfile)

        if os.path.exists(self.h5file):
            os.remove(self.h5file)

        if os.path.exists(self.pngfile):
            os.remove(self.pngfile)

    def test_resample_to_shape(self):

        # Test global with png
        datamean = 15.875
        data, dest_lon, dest_lat, gpis, _, _ = \
            resample_to_shape(self.pngfile, 'global', self.sp_res,
                              self.globalgrid, nan_value=self.fill_value,
                              dest_nan_value=self.fill_value, prefix='prefix')

        # nptest.assert_array_equal(data, resimg)
        assert datamean == data['prefix_dataset'].mean()
        assert dest_lon.shape == self.data.shape
        assert dest_lat.shape == self.data.shape
        assert (gpis[0], gpis[-1]) == (0, 17)

        # Test local with hdf5
        resimg = {'data': np.ma.array([[self.data[1][3].data]],
                                      mask=self.mask[1][3],
                                      fill_value=self.fill_value),
                  'data2': np.ma.array([[self.data[1][3].data]],
                                       mask=self.mask[1][3],
                                       fill_value=self.fill_value)}

        data, _, _, _, _, metadata = \
            resample_to_shape(self.h5file, self.region, self.sp_res,
                              self.grid, nan_value=self.fill_value,
                              dest_nan_value=self.fill_value)

        nptest.assert_array_equal(data, resimg)
        assert metadata == {'data': self.metadata['data'],
                            'data2': self.metadata['data2']}

        # Test local with only one variable with netcdf
        reslon = np.array([[30.]])
        reslat = np.array([[0.]])
        resimg = {'data': np.ma.array([[self.data[1][3].data]],
                                      mask=self.mask[1][3],
                                      fill_value=self.fill_value)}

        data, dest_lon, dest_lat, gpis, timestamp, metadata = \
            resample_to_shape(self.ncfile, self.region, self.sp_res,
                              self.grid, nan_value=self.fill_value,
                              dest_nan_value=self.fill_value,
                              variables=['data'])

        timediff = self.timestamp - timestamp

        nptest.assert_array_equal(data, resimg)
        assert dest_lon[0][0] == reslon
        assert dest_lat[0][0] == reslat
        assert gpis[0] == 0
        assert timediff.days == 0
        assert metadata == {'data': self.metadata['data']}

    def test_average_layers(self):

        avgimg = self.image['data'] * 2

        image = np.ma.array([self.image['data'], self.image['data'] * 3])

        img = average_layers(image, self.fill_value)

        nptest.assert_array_equal(img, avgimg)

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
