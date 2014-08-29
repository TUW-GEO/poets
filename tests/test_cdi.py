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
# Creation date: 2014-08-29

import unittest
import numpy.testing as nptest
import os
import pandas as pd
from datetime import datetime
from poets.time_series.cdi import calc_DI, calc_CDI


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.testfilename = os.path.join(curpath(), 'data', 'ts_sm.csv')
        self.ts = pd.read_csv(self.testfilename, index_col=0)
        ts2 = []
        for ind in range(0, len(self.ts.index)):
            ts2.append(datetime.strptime(self.ts.index[ind], '%Y-%m-%d'))
        self.ts.index = ts2
        self.attribute = 'sm'

    def tearDown(self):
        pass

    def test_calc_DI(self):
        di6_mean = 0.41332512418600514
        di12_mean = 0.47425204454677033

        ts_di = calc_DI(self.ts.copy(), 'soil_moisture',
                        interest_period=[6, 12],
                        scale_zero=False)

        ts_di0 = calc_DI(self.ts.copy(), 'soil_moisture',
                         interest_period=[6, 12],
                         scale_zero=True)

        assert ts_di['sm_DI_6'].mean() == di6_mean
        assert ts_di['sm_DI_12'].mean() == di12_mean
        nptest.assert_almost_equal(ts_di0['sm_DI_6'].mean(), 0)
        nptest.assert_almost_equal(ts_di0['sm_DI_12'].mean(), 0)

    def test_calc_CDI(self):
        cdi_mean = 0.32209785681714431
        cdi2_mean = 0.28988807113543041

        ts = self.ts.copy()
        ts['sm3'] = ts['sm'] * 3

        cdi = calc_CDI(ts.copy())

        cdi2 = calc_CDI(ts.copy(), [60, 40])

        assert cdi['CDI'].mean() == cdi_mean
        assert cdi2['CDI'].mean() == cdi2_mean

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
