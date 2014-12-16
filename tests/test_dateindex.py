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

# Author: Thomas Mistelbauer thomas.mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-08-13

import unittest
from datetime import datetime
from poets.timedate.dateindex import get_dtindex, check_period


class Test(unittest.TestCase):

    def setUp(self):
        self.begin = datetime(2004, 2, 1)
        self.end = datetime(2004, 3, 31)

    def tearDown(self):
        pass

    def test_get_dtindex(self):

        interval1 = 'dekad'
        interval2 = 'day'
        interval3 = 'week'
        interval4 = 'month'
        interval5 = 8

        dtindex1 = get_dtindex(interval1, self.begin, self.end)
        dtindex2 = get_dtindex(interval2, self.begin, self.end)
        dtindex3 = get_dtindex(interval3, self.begin, self.end)
        dtindex4 = get_dtindex(interval4, self.begin, self.end)
        dtindex5 = get_dtindex(interval5, self.begin, self.end)

        assert dtindex1.size == 6
        assert dtindex1[0] == datetime(2004, 2, 10)
        assert dtindex1[-1] == datetime(2004, 3, 31)

        assert dtindex2.size == 60
        assert dtindex2[0] == datetime(2004, 2, 1)
        assert dtindex2[-1] == datetime(2004, 3, 31)

        assert dtindex3.size == 9
        assert dtindex3[0] == datetime(2004, 2, 1)
        assert dtindex3[-1] == datetime(2004, 3, 28)

        assert dtindex4.size == 2
        assert dtindex4[0] == datetime(2004, 2, 29)
        assert dtindex4[-1] == datetime(2004, 3, 31)

        assert dtindex5.size == 8
        assert dtindex5[0] == datetime(2004, 2, 1)
        assert dtindex5[-1] == datetime(2004, 3, 28)

    def test_check_period(self):
        dat = datetime(2014, 11, 20)
        assert check_period('dekad', dat) == datetime(2014, 11, 20, 0, 0)
        assert check_period('week', dat) == datetime(2014, 11, 23, 0, 0)
        assert check_period('monthly', dat) == datetime(2014, 11, 30, 0, 0)


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
