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

# Author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-07-07

"""
Description of module.
"""

import unittest
from poets.grid.grids import CountryGrid


class Test(unittest.TestCase):

    def setUp(self):
        self.region = 'AU'
        self.sp_res = 0.25

    def tearDown(self):
        pass

    def test_CountryGrid(self):
        points_number = 290
        bbox = (46.625, 48.875, 9.875, 16.875)
        cpoints_shape = (158, 2)

        cgrid = CountryGrid(self.region, resolution=self.sp_res)
        grid_bbox = (cgrid.arrlat.min(), cgrid.arrlat.max(),
                     cgrid.arrlon.min(), cgrid.arrlon.max())

        grid_points_number = cgrid.get_grid_points()[0].size

        country_points_shape = cgrid.get_country_gridpoints().shape

        assert points_number == grid_points_number
        assert bbox == grid_bbox
        assert cpoints_shape == country_points_shape


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
