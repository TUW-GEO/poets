# Copyright (c) 2014, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

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

# Author: pydev
# Creation date: 2014-07-08

import unittest
import os
import numpy as np
import numpy.testing as nptest
from datetime import datetime
from poets.image.netcdf import save_image, write_tmp_file
from netCDF4 import Dataset


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        self.sp_res = 90
        self.region = 'global'
        self.testfilename = os.path.join(curpath(), 'data', 'test.nc')
        self.metadata = None
        self.timestamp = datetime.today()
        self.start_date = datetime.today()
        self.temp_res = 'day'
        self.shape = (2, 4)
        self.mask = [[1, 0, 1, 0], [0, 1, 0, 1]]

        self.image = {}
        self.data = np.ma.array(np.ones(self.shape), mask=self.mask,
                          fill_value=-99)
        self.image['data'] = self.data

        if not os.path.exists(os.path.join(curpath(), 'data')):
            os.mkdir(os.path.join(curpath(), 'data'))

    def tearDown(self):
        os.remove(self.testfilename)
        pass

    def test_save_image(self):

        save_image(self.image, self.timestamp, self.region, self.metadata,
                   self.testfilename, self.start_date, self.sp_res,
                   temp_res=self.temp_res)

        with Dataset(self.testfilename) as nc_data:
            nptest.assert_array_equal(self.data,
                                      nc_data.variables['data'][0, :])

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
