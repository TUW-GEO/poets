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

from datetime import datetime
from poets.poet import Poet
from poets.timedate.dateindex import get_dtindex
import numpy as np
import os
import shutil
import unittest


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.rootpath = os.path.join(curpath(), 'data', 'src_test')
        self.nan_value = -99
        self.regions = ['AU']
        self.spatial_resolution = 1
        self.temporal_resolution = 'week'
        self.start_date = datetime(2013, 1, 7)
        self.enddate = datetime(2013, 1, 13)
        self.testdate = datetime(2013, 1, 10)

        if os.path.exists(self.rootpath):
            shutil.rmtree(self.rootpath)

        os.mkdir(self.rootpath)
        os.mkdir(os.path.join(self.rootpath, 'DATA'))
        os.mkdir(os.path.join(self.rootpath, 'TMP'))

        self.poet = Poet(self.rootpath, self.regions, self.spatial_resolution,
                         self.temporal_resolution, self.start_date,
                         self.nan_value)

        # setup test png files
        self.pngdir = os.path.join(curpath(), 'data', 'testpngs')
        if os.path.exists(self.pngdir):
            shutil.rmtree(self.pngdir)
        os.mkdir(self.pngdir)
        dtindex = get_dtindex('day', self.start_date,
                              self.enddate)
        for dat in dtindex:
            year = str(dat.year)
            month = "%02d" % (dat.month)
            day = "%02d" % (dat.day)
            fname = ('test_' + year + '_' + month + '_' + day + '.png')
            shutil.copy(os.path.join(curpath(), 'data', 'test.png'),
                        os.path.join(self.pngdir, fname))

    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.rootpath):
            shutil.rmtree(self.rootpath)
        if os.path.exists(self.pngdir):
            shutil.rmtree(self.pngdir)

    def test_init(self):
        assert len(self.poet.__dict__.keys()) == 13

    def test_add_source(self):
        name = 'CCI'
        filename = ("ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{YYYY}{MM}{TT}{hh}"
                    "{mm}{ss}-fv02.0.nc")
        filedate = {'YYYY': (38, 42), 'MM': (42, 44), 'DD': (44, 46),
                    'hh': (46, 48), 'mm': (48, 50), 'ss': (50, 52)}
        temp_res = 'daily'
        host = "ftp.ipf.tuwien.ac.at/"
        directory = "_down/daily_files/COMBINED/"
        protocol = 'SFTP'
        username = 'ecv_sm_v2'
        password = 'Gn03KGNyWmQp'
        port = 22
        dirstruct = ['YYYY']
        begin_date = datetime(1978, 11, 01)
        variables = ['sm']
        valid_range = (0, 0.6)
        colorbar = 'jet_r'

        self.poet.add_source(name, filename, filedate, temp_res, host,
                             protocol, username=username, password=password,
                             port=port, directory=directory,
                             dirstruct=dirstruct, begin_date=begin_date,
                             variables=variables, colorbar=colorbar,
                             valid_range=valid_range)

        assert len(self.poet.sources['CCI'].__dict__.keys()) == 29

        name = 'TEST'
        filename = "test_{YYYY}_{MM}_{TT}.png"
        filedate = {'YYYY': (5, 9), 'MM': (10, 12), 'DD': (13, 15)}
        temp_res = 'daily'
        host = self.pngdir
        protocol = 'local'
        begin_date = datetime(2013, 1, 7)
        nan_value = 255
        data_range = (0, 254)
        valid_range = (0, 1)
        unit = "NDVI"
        colorbar = 'Greens'

        self.poet.add_source(name, filename, filedate, temp_res, host,
                             protocol, begin_date=begin_date,
                             nan_value=nan_value, valid_range=valid_range,
                             unit=unit, data_range=data_range,
                             colorbar=colorbar)

        assert len(self.poet.sources['TEST'].__dict__.keys()) == 29

    def test_download(self):
        self.poet.download(begin=self.start_date, end=self.enddate)
        assert len(os.listdir(os.path.join(self.rootpath, 'RAWDATA'))) == 2

    def test_resample(self):
        self.poet.resample(begin=self.start_date, end=self.enddate)

    def test_fetch_data(self):
        self.poet.fetch_data(end=self.enddate)
        assert len(os.listdir(os.path.join(self.rootpath, 'DATA'))) == 1
        assert len(os.listdir(os.path.join(self.rootpath, 'RAWDATA'))) == 2

    def test_read_image(self):
        img, lon, lat, metadata = self.poet.read_image('CCI', self.testdate)
        assert img.shape == (3, 7)
        assert img[2, 4] == 0.21312499791383743
        assert metadata['units'] == 'm3 m-3'
        assert lat.shape == (3,)
        assert lon.shape == (7,)

        img, _, _, metadata = self.poet.read_image('TEST', self.testdate,
                                                   variable='TEST_dataset')
        assert img.shape == (3, 7)
        assert img[2, 4] == 0.69685039370078738
        assert img[0, 0] is np.ma.masked
        assert metadata is None

    def test_read_timeseries(self):
        location = (14.5, 46.5)
        ts = self.poet.read_timeseries('CCI', location, region=self.regions[0])
        assert ts['CCI_sm'][0] == 0.21312499791383743

        ts = self.poet.read_timeseries('TEST', location,
                                       region=self.regions[0],
                                       variable='TEST_dataset')
        assert ts['TEST_dataset'][0] == 0.69685039370078738

    def test_get_gridpoints(self):
        gridpoints = self.poet.get_gridpoints()
        assert gridpoints[self.regions[0]].index.size == 12

    def test_get_variables(self):
        variables = self.poet.get_variables()
        assert variables == ['CCI_sm', 'TEST_dataset']

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
