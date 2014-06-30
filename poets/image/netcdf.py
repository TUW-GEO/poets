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
# Creation date: 2014-06-13

"""
Description of module.
"""

import os.path
import numpy as np
from pytesmo.grid.netcdf import save_grid
from poets.constants import Settings as settings
from poets.grid import grids
from netCDF4 import Dataset


def save_image(image, lon, lat, country):

    c_grid = grids.CountryGrid(country)

    path = settings.out_path

    filename = country + '_' + str(settings.sp_res) + '.nc'

    nc_name = os.path.join(path, filename)

    #===========================================================================
    # if not os.path.isfile(nc_name):
    #     save_grid(nc_name, c_grid)
    #===========================================================================

    save_grid(nc_name, c_grid)

    with Dataset(nc_name, 'a', format='NETCDF4') as ncfile:

        dim = ncfile.dimensions.keys()

        for key in image.keys():

            var = ncfile.createVariable(key, np.dtype('int32').char, dim,
                                        fill_value=-99)
            var[:] = np.copy(image[key])
            setattr(var, 'long_name', key)
            setattr(var, 'units', 'millimeters')

if __name__ == "__main__":
    pass
