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

# Author: Isabella Pfeil, isy.pfeil@gmx.at
# Creation date: 2014-08-18

import unittest
import os
import pandas as pd
from datetime import datetime
from poets.time_series.filtering import group_months, group_seasons, ctrd_mov_avg
from poets.time_series.deseasonalizing import seasonal_indices, zscore


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        # read WACMOS soil moisture time series for lon=15, lat=10
        self.testfilename = os.path.join(curpath(), 'data', 'ts_sm.csv')
        self.ts = pd.read_csv(self.testfilename, index_col=0)
        ts2 = []
        for ind in range(0, len(self.ts.index)):
            ts2.append(datetime.strptime(self.ts.index[ind], '%Y-%m-%d'))
        self.ts.index = ts2
        self.attribute = 'sm'

    def tearDown(self):
        pass

    def test_group_months(self):
        len_ts_mon = 132
        lenDates = 45

        ts_mon = len(group_months(self.ts, self.attribute)[0])
        ts_dat = len(group_months(self.ts, self.attribute)[1])

        assert len_ts_mon == ts_mon
        assert lenDates == ts_dat

    def test_group_seasons(self):
        len_ts_seas = 45
        lenDates = 45

        ts_months, dates = group_months(self.ts, self.attribute)

        ts_seas = len(group_seasons(ts_months, dates)[0])
        ts_dat = len(group_seasons(ts_months, dates)[1])

        assert len_ts_seas == ts_seas
        assert lenDates == ts_dat

    def test_ctrd_mov_avg(self):
        len_ts_ctrd = 40
        ts_months, dates = group_months(self.ts, self.attribute)
        ts_seas, _ = group_seasons(ts_months, dates)
        ts_ctrd = len(ctrd_mov_avg(ts_seas))

        assert len_ts_ctrd == ts_ctrd

    def test_seasonal_indices(self):
        len_ts_des = 45

        ts_des = len(seasonal_indices(self.ts, self.attribute))

        assert len_ts_des == ts_des

    def test_zscore(self):
        len_ts_des = 45

        ts_des = len(zscore(self.ts, self.attribute))

        assert len_ts_des == ts_des


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()