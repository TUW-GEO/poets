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
# Creation date: 2014-07-07

import unittest
from poets.grid.grids import ShapeGrid, RegularGrid


class Test(unittest.TestCase):

    def setUp(self):
        self.region = 'AU'
        self.sp_res = 0.25
        self.sp_res1 = 0.5

    def tearDown(self):
        pass

    def test_ShapeGrid(self):
        # general case
        cgrid = ShapeGrid(self.region, sp_res=self.sp_res)
        bbox = (cgrid.arrlat.min(), cgrid.arrlat.max(),
                cgrid.arrlon.min(), cgrid.arrlon.max())

        assert cgrid.get_grid_points()[0].size == 290
        assert bbox == (46.625, 48.875, 9.875, 16.875)
        assert cgrid.get_gridpoints().shape == (158, 2)

        # test special case NZ
        cgrid = ShapeGrid('NZ', sp_res=self.sp_res1)
        bbox = (cgrid.arrlat[0], cgrid.arrlat[-1],
                cgrid.arrlon[0], cgrid.arrlon[-1])

        assert cgrid.shape == (24, 34)
        assert cgrid.get_gridpoints().shape == (116, 2)
        assert bbox == (-46.75, -35.25, 167.37, -176.5)

    def test_RegularGrid(self):
        points_number = 259200
        bbox = (-89.75, 89.75, -179.75, 179.75)
        grid_shape = (360, 720)

        grid = RegularGrid(sp_res=self.sp_res1)

        grid_bbox = (grid.arrlat.min(), grid.arrlat.max(),
                     grid.arrlon.min(), grid.arrlon.max())

        assert grid.get_grid_points()[0].size == points_number
        assert grid_bbox == bbox
        assert grid.shape == grid_shape

if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
