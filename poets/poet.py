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

# Author: Thomas Mistelbauer
# Creation date: 2014-07-29

"""
This module includes the poets base class `Poet`.
"""

import os
import numpy as np
import pandas as pd
from datetime import datetime
from netCDF4 import Dataset
from poets.io.source_base import BasicSource
from poets.grid.grids import ShapeGrid

valid_temp_res = ['dekad', 'month']


class Poet(object):
    """POETS base class.

    Provides methods to download and resample data using parameters as defined
    in this class. Resampled outputfiles will be saved as NetCDF4 files.

    Parameters
    ----------
    rootpath : str
        path to the directory where data should be stored
    regions : list of str, optional
        Identifier of the region in the shapefile. If the default shapefile is
        used, this would be the FIPS country code. Defaults to global.
    spatial_resolution : float, optional
        spatial resolution in degree, defaults to 0.25
    temporal_resolution : str, optional
        temporal resolution of the data, possible values: month, dekad,
        defaults to dekad
    start_date : datetime.datetime, optional
        first date of the dataset, defaults to 2000-01-01
    nan_value : int
        NaN value to use, defaults to -99
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.
    delete_rawdata : bool, optional
        Original files will be deleted from tmp_path if set True. Defaults
        to False

    Attributes
    ----------
    rootpath : str
        path to the directory where data should be stored
    regions : list of str
        Identifier of the region in the shapefile.
    spatial_resolution : float
        Spatial resolution in degree.
    temporal_resolution : str
        Temporal resolution of the data.
    tmp_path : str
        Path where temporary files and original files are stored and
        downloaded.
    data_path : str
        Path where resampled NetCDF file is stored.
    nan_value : int
        NaN value to use, defaults to -99.
    start_date : datetime.datetime
        First date of the dataset.
    shapefile : str
        Path to shape file.
    sources : dict of poets.io.BasicSource objects
        Sources used by poets given as BasicSource class.
    delete_rawdata : bool
        Original files will be deleted from tmp_path if True.
    """

    def __init__(self, rootpath, regions=['global'],
                 spatial_resolution=0.25, temporal_resolution='dekad',
                 start_date=datetime(2000, 1, 1), nan_value=-99,
                 shapefile=None, delete_rawdata=False):

        self.rootpath = rootpath
        self.regions = regions
        self.spatial_resolution = spatial_resolution

        if temporal_resolution not in ['dekad', 'month']:
            raise ValueError("Temporal resulution must be one of " +
                             str(valid_temp_res))

        self.temporal_resolution = temporal_resolution
        self.tmp_path = os.path.join(rootpath, 'TMP')
        self.data_path = os.path.join(rootpath, 'DATA')
        self.nan_value = nan_value
        self.start_date = start_date
        self.shapefile = shapefile
        self.delete_rawdata = delete_rawdata
        self.sources = {}

        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)

        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

    def add_source(self, name, filename, filedate, temp_res, host, protocol,
                   username=None, password=None, port=22, directory=None,
                   dirstruct=None, begin_date=datetime(2000, 1, 1),
                   variables=['dataset'], nan_value=None):
        """Creates BasicSource class and adds it to `Poet.sources`.

        Parameters
        ----------
        name : str
            Name of the data source.
        filename : str
            Structure/convention of the file name.
        filedate : dict
            Position of date fields in filename, given as tuple.
        temp_res : str
            Temporal resolution of the source.
        host : str
            Link to data host.
        protocol : str
            Protocol for data transfer.
        username : str, optional
            Username for data access.
        password : str, optional
            Password for data access.
        port : int, optional
            Port to data host, defaults to 22.
        directory : str, optional
            Path to data on host.
        dirstruct : list of strings
            Structure of source directory, each list item represents a
            subdirectory.
        begin_date : datetime.date, optional
            Date from which on data is available, defaults to 2000-01-01.
        variables : list of strings, optional
            Variables used from data source, defaults to ['dataset'].
        nan_value : int, float, optional
            Nan value of the original data as given by the data provider.
        """

        source = BasicSource(name, filename, filedate, temp_res, self.rootpath,
                             host, protocol, username, password, port,
                             directory, dirstruct, begin_date, variables,
                             nan_value, self.nan_value, self.regions,
                             self.spatial_resolution, self.temporal_resolution,
                             self.start_date)

        self.sources[name] = source

    def fetch_data(self, begin=None, end=None, delete_rawdata=None):
        """Starts download and resampling of input data for sources as added
        to `Poets.sources`.

        Parameters
        ----------
        begin : datetime, optional
            Start date of data to download, defaults to start date as defined
            in poets class.
        end : datetime, optional
            End date of data to download, defaults to current datetime.
        delete_rawdata : bool, optional
            Original files will be deleted from tmp_path if set True. Defaults
            to delete_rawdata attribute as set in Poet class.
        """

        if not delete_rawdata:
            delete_rawdata = self.delete_rawdata

        for source in self.sources.keys():
            src = self.sources[source]
            print '[INFO] Download data for source ' + source
            src.download_and_resample(begin=begin, end=end,
                                      shapefile=self.shapefile)

        print '[SUCCESS] Download and resampling complete!'

    def get_gridpoints(self):
        """Returns gridpoints from NetCDF file.

        Parameters
        ----------
        region : str
            Identifier of the region in the NetCDF file.

        Returns
        -------
        gridpoints : dict of pandas.DataFrame
            Dict containing Dataframes with gridpoint index as index,
            longitutes and latitudes as columns for each region.
        """

        gridpoints = {}

        if self.regions == ['global']:
            filename = (self.regions[0] + '_' + str(self.spatial_resolution)
                        + '_' + str(self.temporal_resolution) + '.nc')
            ncfile = os.path.join(self.data_path, filename)

            with Dataset(ncfile, 'r+', format='NETCDF4') as nc:
                gpis = nc.variables['gpi'][:]
                lons = nc.variables['lon'][:]
                lats = nc.variables['lat'][:]
                gpis = gpis.flatten()
                lons, lats = np.meshgrid(lons, lats)
                lons = lons.flatten()
                lats = lats.flatten()

            points = pd.DataFrame(index=gpis)
            points['lon'] = lons
            points['lat'] = lats
            gridpoints['global'] = points
        else:
            for region in self.regions:
                grid = ShapeGrid(region, self.spatial_resolution)
                points = grid.get_gridpoints()
                gridpoints[region] = points

        return gridpoints

if __name__ == "__main__":
    pass
