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
# Creation date: 2014-06-13

"""
This module provides functions for loading from and writing to NetCDF4 files.
"""

import os.path
from netCDF4 import Dataset, date2num, num2date
from pytesmo.grid.netcdf import save_grid
import numpy as np
from poets.grid import grids
from poets.timedate.dateindex import get_dtindex


def save_image(image, timestamp, region, metadata, dest_file, start_date,
               sp_res, nan_value=-99, shapefile=None, temp_res='dekad'):
    """Saves numpy.ndarray images as multidimensional netCDF4 file.

    Creates a datetimeindex over the whole period defined in the settings file

    Parameters
    ----------
    image : dict of numpy.ndarrays
        Input image.
    timestamp : datetime.datetime
        Timestamp of image.
    region : str, optional
        Identifier of the region in the shapefile. If the default shapefile is
        used, this would be the FIPS country code.
    metadata : dict
        NetCDF metadata from source file.
    dest_file : str
        Path to the output file.
    start_date : datetime.datetime
        First date of available data.
    nan_value : int, optional
        Not a number value for dataset, defaults to -99.
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.
    temp_res : string or int, optional
        Temporal resolution of the output NetCDF4 file, defaults to dekad.
    """

    if region == 'global':
        grid = grids.RegularGrid(sp_res)
    else:
        grid = grids.ShapeGrid(region, sp_res, shapefile)

    dest_file = dest_file

    if not os.path.isfile(dest_file):
        save_grid(dest_file, grid)

    dt = get_dtindex(temp_res, start_date)

    with Dataset(dest_file, 'r+', format='NETCDF4') as ncfile:

        if 'time' not in ncfile.dimensions.keys():
            ncfile.createDimension("time", None)
            times = ncfile.createVariable('time', 'uint16', ('time',))
            times.units = 'days since ' + str(start_date)
            times.calendar = 'standard'
            times[:] = date2num(dt.tolist(), units=times.units,
                                calendar=times.calendar)

        else:
            times = ncfile.variables['time']

        dim = ('time', 'lat', 'lon')

        numdate = date2num(timestamp, units=times.units,
                           calendar=times.calendar)

        for key in image.keys():

            if key not in ncfile.variables.keys():
                var = ncfile.createVariable(key, image[key].dtype.char, dim,
                                            fill_value=nan_value)
            else:
                var = ncfile.variables[key]

            var[np.where(times[:] == numdate)[0][0]] = image[key]
            if metadata is not None:
                var.setncatts(metadata[key])


def write_tmp_file(image, timestamp, region, metadata, dest_file, start_date,
                   sp_res, nan_value=-99, shapefile=None):
    """Saves numpy.ndarray images as multidimensional netCDF4 file.

    Parameters
    ----------
    image : dict of numpy.ndarrays
        Input image.
    timestamp : datetime.datetime
        Timestamp of image.
    region : str, optional
        Identifier of the region in the shapefile. If the default shapefile is
        used, this would be the FIPS country code.
    metadata : dict
        NetCDF metadata from source file.
    dest_file : str
        Path to the output file.
    nan_value : int, optional
        Not a number value for dataset, defaults to -99.
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.
    """

    if region == 'global':
        grid = grids.RegularGrid(sp_res)
    else:
        grid = grids.ShapeGrid(region, sp_res, shapefile)

    if not os.path.isfile(dest_file):
        save_grid(dest_file, grid)

    with Dataset(dest_file, 'r+', format='NETCDF4') as ncfile:

        if 'time' not in ncfile.dimensions.keys():
            ncfile.createDimension("time", None)
            times = ncfile.createVariable('time', 'uint16', ('time',))
            times.units = 'days since ' + str(start_date)
            times.calendar = 'standard'

        else:
            times = ncfile.variables['time']

        numdate = date2num(timestamp, units=times.units,
                           calendar=times.calendar)

        dim = ('time', 'lat', 'lon')

        for key in image.keys():

            if key not in ncfile.variables.keys():
                var = ncfile.createVariable(key, image[key].dtype.char, dim,
                                            fill_value=nan_value)
            else:
                var = ncfile.variables[key]

            if times.shape[0] == 0:
                times[0] = numdate
                var_index = 0
            else:
                if numdate in times[:]:
                    t_index = np.where(times[:] == numdate)[0][0]
                    var_index = t_index
                else:
                    times[times[:].size] = numdate
                    var_index = times[:].size - 1

            var[var_index] = image[key]
            if metadata is not None:
                var.setncatts(metadata[key])


def clip_bbox(source_file, lon_min, lat_min, lon_max, lat_max):
    """Clips bounding box out of netCDF file and returns data as numpy.ndarray

    Parameters
    ----------
    source_file : str
        Path to source file.
    lon_min : float
        Min longitude of bounding box.
    lat_min : float
        Min latitude of bounding box.
    lon_max : float
        Max longitude of bounding box.
    lat_max : float
        Max latitude of bounding box.

    Returns
    -------
    data : dict of numpy.arrays
        Clipped image.
    lon_new : numpy.array
        Longitudes of the clipped image.
    lat_new : numpy.array
        Latgitudes of the clipped image.
    timestamp : datetime.date
        Timestamp of image.
    metadata : dict of strings
        Metadata from source netCDF file.
    """

    with Dataset(source_file, 'r', format='NETCDF4') as nc:

        if 'time' in nc.variables.keys():
            times = nc.variables['time']
            timestamp = num2date(times[:], units=times.units)[0]
        else:
            timestamp = None

        lon = np.copy(nc.variables['lon'])
        lat = np.copy(nc.variables['lat'])

        variables = nc.variables.keys()
        if 'gpi' in variables:
            variables.remove('gpi')
        if 'lat' in variables:
            variables.remove('lat')
        if 'lon' in variables:
            variables.remove('lon')
        if 'time' in variables:
            variables.remove('time')

        lons = np.where((lon >= lon_min) & (lon <= lon_max))[0]
        lats = np.where((lat >= lat_min) & (lat <= lat_max))[0]

        lon_new = lon[lons.min():lons.max() + 1]
        lat_new = lat[lats.min():lats.max() + 1]

        data = {}
        metadata = {}

        for var in variables:
            dat = nc.variables[var][:][0]
            data[var] = dat[lats.min():lats.max() + 1,
                            lons.min():lons.max() + 1]
            metadata[var] = {}
            for attr in nc.variables[var].ncattrs():
                if attr[0] != '_' and attr != 'scale_factor':
                    metadata[var][attr] = nc.variables[var].getncattr(attr)

    return data, lon_new, lat_new, timestamp, metadata


def read_image(source_file, variable, date, date_to=None):
    """Gets images from a netCDF file.

    Reads the image for a specific date. If date_to is given, it will return
    multiple images in a multidimensional numpy.ndarray

    Parameters
    ----------
    source_file : str
        Path to source file.
    variable : str
        Requested variable of image.
    date : datetime.datetime
        Date of the image, start date of data cube if date_to is set.
    date_to : datetime.date, optional
        End date of data cube to slice from NetCDF file.

    Returns
    -------
    image : numpy.ndarray
        Image for a specific date.
    lon : numpy.array
        Longitudes of the image.
    lat : numpy.array
        Latgitudes of the image.
    metadata : dict of strings
        Metadata from source netCDF file.
    """

    with Dataset(source_file, 'r', format='NETCDF4') as nc:
        times = nc.variables['time']
        lon = nc.variables['lon'][:]
        lat = nc.variables['lat'][:]
        var = nc.variables[variable]

        metadata = {}
        for attr in var.ncattrs():
            if attr[0] != '_' and attr != 'scale_factor':
                metadata[attr] = var.getncattr(attr)

        numdate = date2num(date, units=times.units, calendar=times.calendar)
        if date_to is None:
            image = var[np.where(times[:] == numdate)[0][0]]
        else:
            numdate_to = date2num(date_to, units=times.units,
                                  calendar=times.calendar)
            subset = np.where((times[:] >= numdate) & (times[:] <= numdate_to))
            image = var[subset]

    return image, lon, lat, metadata

if __name__ == "__main__":
    pass


def get_properties(src_file):
    """Gets variables, dimensions and time period from a netCDF file.

    Parameters
    ----------
    src_file : str
        Path to NetCDF file.

    Returns
    -------
    variables : list of str
        List of variables.
    dimensions : list of str
        Dimensions of the NetCDF file.
    period : list of datetime.datetime
        Date of first and last image in source file.
    """

    with Dataset(src_file, 'r+', format='NETCDF4') as nc:
        variables = nc.variables.keys()
        dimensions = nc.dimensions.keys()
        time = nc.variables['time']
        period = [num2date(time[:].min(), units=time.units,
                           calendar=time.calendar),
                  num2date(time[:].max(), units=time.units,
                           calendar=time.calendar)]

        for dim in dimensions:
            variables.remove(dim)

    if 'gpi' in variables:
        variables.remove('gpi')

    return variables, dimensions, period
