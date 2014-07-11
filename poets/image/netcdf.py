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
Functions for loading from and writing to netCDF4 files
"""

import os.path
import numpy as np
from pytesmo.grid.netcdf import save_grid
from poets.settings import Settings
from poets.grid import grids
from poets.timedate.dateindex import dekad_index
from netCDF4 import Dataset, date2num, num2date


def save_image(image, lon, lat, timestamp, country):
    """
    Saves numpy.ndarray images as multidimensional netCDF4 file.
    
    Parameters
    ----------
    image : dict of numpy.ndarrays
        input image
    lon : numpy.ndarray
        longitudes of image
    lat : numpy.ndarray
        latitudes of image
    timestamp : datetime.datetime
        timestamp of image
    country : str
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)
    """

    c_grid = grids.CountryGrid(country)

    path = Settings.data_path

    filename = country + '_' + str(Settings.sp_res) + '.nc'

    nc_name = os.path.join(path, filename)

    if not os.path.isfile(nc_name):
        save_grid(nc_name, c_grid)

    dt = dekad_index(Settings.start_date)

    with Dataset(nc_name, 'r+', format='NETCDF4') as ncfile:

        dim = ncfile.dimensions.keys()

        if 'time' not in ncfile.dimensions.keys():
            ncfile.createDimension("time", None)
            dim = dim[::-1]
            dim.append('time')
            dim = dim[::-1]

            times = ncfile.createVariable('time', 'uint16', ('time',))
            times.units = 'days since ' + str(Settings.start_date)
            times.calendar = 'standard'
            times[:] = date2num(dt.tolist(), units=times.units,
                                calendar=times.calendar)

        else:
            times = ncfile.variables['time']

        numdate = date2num(timestamp, units=times.units,
                           calendar=times.calendar)

        for key in image.keys():

            if key not in ncfile.variables.keys():
                var = ncfile.createVariable(key, np.dtype('int32').char, dim,
                                            fill_value=-99)
            else:
                var = ncfile.variables[key]

            var[np.where(times[:] == numdate)[0][0]] = image[key]
            setattr(var, 'long_name', key)
            setattr(var, 'units', 'millimeters')


def clip_bbox(source_file, lon_min, lat_min, lon_max, lat_max, country=None):
    """
    Clips bounding box out of netCDF file and returns data as numpy.ndarray

    Parameters
    ----------
    source_file : str
        path to source file
    lon_min : float
        min longitude of bounding box
    lat_min : float
        min latitude of bounding box
    lon_max : float
        max longitude of bounding box
    lat_max : float
        max latitude of bounding box

    Returns
    -------
    data : dict of numpy.arrays
        clipped image
    lon_new : numpy.array
        longitudes of the clipped image
    lat_new : numpy.array
        latgitudes of the clipped image
    timestamp : datetime.date
        timestamp of image
    """

    nc = Dataset(source_file)

    if 'time' in nc.variables.keys():
        times = nc.variables['time']
        timestamp = num2date(times[:], units=times.units)[0]
    else:
        timestamp = None

    lon = np.copy(nc.variables['lon'])
    lat = np.copy(nc.variables['lat'])

    variables = nc.variables.keys()[3:]

    lons = np.where((lon >= lon_min) & (lon <= lon_max))[0]
    lats = np.where((lat >= lat_min) & (lat <= lat_max))[0]

    lon_new = lon[lons.min():lons.max()]
    lat_new = lat[lats.min():lats.max()]

    data = {}

    for var in variables:
        dat = nc.variables[var][:][0]
        data[var] = dat[lats.min():lats.max(), lons.min():lons.max()]

    nc.close()

    return data, lon_new, lat_new, timestamp

if __name__ == "__main__":
    pass
