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
import os
import shutil
import unittest

import numpy as np
from poets.io.source_base import BasicSource
from poets.timedate.dateindex import get_dtindex


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    @classmethod
    def setUpClass(self):

        self.rootpath = os.path.join(curpath(), 'data', 'src_test')
        self.dest_nan_value = -99
        self.dest_regions = ['AU']
        self.dest_sp_res = 1
        self.dest_temp_res = 'daily'
        self.dest_start_date = datetime(2013, 1, 7)
        self.enddate = datetime(2013, 1, 13)
        self.testdate = datetime(2013, 1, 10)
        self.name = 'TEST'
        self.filename = "test_{YYYY}_{MM}_{TT}.png"
        self.filedate = {'YYYY': (5, 9), 'MM': (10, 12), 'DD': (13, 15)}
        self.temp_res = 'daily'
        self.protocol = 'local'
        self.begin_date = datetime(2013, 1, 7)

        if os.path.exists(self.rootpath):
            shutil.rmtree(self.rootpath)

        os.mkdir(self.rootpath)
        os.mkdir(os.path.join(self.rootpath, 'DATA'))
        os.mkdir(os.path.join(self.rootpath, 'TMP'))

        # setup test png files
        self.pngdir = os.path.join(curpath(), 'data', 'testpngs')
        self.host = self.pngdir

        if os.path.exists(self.pngdir):
            shutil.rmtree(self.pngdir)
        os.mkdir(self.pngdir)
        self.dtindex = get_dtindex('day', self.dest_start_date,
                                   self.enddate)
        for i, dat in enumerate(self.dtindex):
            if i == 3:
                continue
            year = str(dat.year)
            month = "%02d" % (dat.month)
            day = "%02d" % (dat.day)
            fname = ('test_' + year + '_' + month + '_' + day + '.png')
            shutil.copy(os.path.join(curpath(), 'data', 'test.png'),
                        os.path.join(self.pngdir, fname))

        self.source = BasicSource(self.name, self.filename, self.filedate,
                                  self.temp_res, self.rootpath,
                                  self.host, self.protocol,
                                  begin_date=self.begin_date,
                                  dest_nan_value=-self.dest_nan_value,
                                  dest_regions=self.dest_regions,
                                  dest_sp_res=self.dest_sp_res,
                                  dest_temp_res=self.dest_temp_res,
                                  dest_start_date=self.dest_start_date)

    @classmethod
    def tearDownClass(self):
        if os.path.exists(self.rootpath):
            shutil.rmtree(self.rootpath)
        if os.path.exists(self.pngdir):
            shutil.rmtree(self.pngdir)

    def test_download_and_resample(self):
        self.source.download_and_resample(end=self.enddate)
        for date in self.dtindex:
            img, _, _, _ = self.source.read_img(date)
            if date == self.testdate:
                assert img[2, 4] is np.ma.masked
            else:
                assert img[2, 4] == 177.

    def test_fill_gaps(self):
        shutil.copy(os.path.join(curpath(), 'data', 'test.png'),
                    os.path.join(self.pngdir, 'test_2013_01_10.png'))
        self.source.fill_gaps(begin=self.dest_start_date, end=self.enddate)
        img, _, _, _ = self.source.read_img(self.testdate)
        assert img[1, 1] == 145.

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
