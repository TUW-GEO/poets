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
import shutil
from datetime import datetime
from poets.io.source_base import BasicSource


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):

        self.rootpath = os.path.join(curpath(), 'data', 'src_test')
        self.dest_nan_value = -99
        self.regions = ['AU']
        self.spatial_resolution = 1
        self.temporal_resolution = 'week'
        self.dest_start_date = datetime(2013, 1, 1)
        self.enddate = datetime(2013, 1, 10)

        if os.path.exists(self.rootpath):
            shutil.rmtree(self.rootpath)

        os.mkdir(self.rootpath)

        self.name = 'CCI'
        self.filename = ("ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{YYYY}{MM}{TT}"
                         "{hh}{mm}{ss}-fv02.0.nc")
        self.filedate = {'YYYY': (38, 42), 'MM': (42, 44), 'DD': (44, 46),
                         'hh': (46, 48), 'mm': (48, 50), 'ss': (50, 52)}
        self.temp_res = 'daily'
        self.host = "ftp.ipf.tuwien.ac.at/"
        self.directory = "_down/daily_files/COMBINED/"
        self.protocol = 'SFTP'
        self.username = 'ecv_sm_v2'
        self.password = 'Gn03KGNyWmQp'
        self.port = 22
        self.begin_date = datetime(1978, 11, 01)
        self.variables = ['sm']
        self.valid_range = (0, 0.6)
        self.colorbar = 'jet_r'

        #======================================================================
        # self.source = BasicSource(self.name,
        #                           self.filename,
        #                           self.filedate,
        #                           self.temp_res,
        #                           self.rootpath,
        #                           self.host,
        #                           self.protocol,
        #                           username=self.username,
        #                           password=self.password,
        #                           port=self.port,
        #                           ffilter=self.ffilter,
        #                           directory=self.directory,
        #                           dirstruct=self.dirstruct,
        #                           begin_date=self.begin_date,
        #                           variables=self.variables,
        #                           nan_value=self.nan_value,
        #                           valid_range=self.valid_range,
        #                           unit=self.unit,
        #                           data_range=self.data_range,
        #                           scolorbar=self.colorbar,
        #                           dest_nan_value=self.nan_value,
        #                           dest_regions=self.regions,
        #                           dest_sp_res=self.spatial_resolution,
        #                           dest_temp_res=self.temporal_resolution,
        #                           dest_start_date=self.start_date)
        #======================================================================

    def tearDown(self):
        if os.path.exists(self.rootpath):
            shutil.rmtree(self.rootpath)

    def test_init(self):
        source = BasicSource(self.name, self.filename, self.filedate,
                             self.temp_res, self.rootpath, self.host,
                             self.protocol, username=self.username,
                             password=self.password, port=self.port,
                             directory=self.directory,
                             begin_date=self.begin_date,
                             variables=self.variables,
                             colorbar=self.colorbar,
                             dest_nan_value=self.dest_nan_value,
                             dest_regions=self.regions,
                             dest_sp_res=self.spatial_resolution,
                             dest_temp_res=self.temporal_resolution,
                             dest_start_date=self.dest_start_date)

        assert len(source.__dict__.keys()) == 27


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
