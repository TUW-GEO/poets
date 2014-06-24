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
from pytesmo.grid.netcdf import save_lonlat
from poets.constants import Settings as settings
from netCDF4 import Dataset


def save_image(image, lon, lat, country, gpis=None):

    path = settings.out_path

    filename = country + '_' + str(settings.sp_res) + '.nc'

    nc_name = os.path.join(path, filename)

    if not os.path.isfile(nc_name):
        save_lonlat(nc_name, lon, lat, gpis)

    with Dataset(nc_name, 'a', format='NETCDF4') as ncfile:

        rd = ncfile.createGroup("raw_data")
        rd.createDimension("raw_data", lon.size)

        for key in image.keys():
            var = rd.createVariable(key, np.dtype('int32').char,
                                                   ('raw_data',))
            var[:] = image[key].flatten()
            setattr(var, 'long_name', 'Rainfall Estimates')
            setattr(var, 'units', 'millimeters')
            # setattr(var, 'standard_name', 'rfe')
            # setattr(var, 'valid_range', [0, 240])
            # setattr(var, '_FillValue', '-99S')

if __name__ == "__main__":
    pass
