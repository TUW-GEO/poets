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
        temporal resolution of the data, possible values: day, week,
        month, dekad, defaults to dekad
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
    regions : list of str, optional
        Identifier of the region in the shapefile. If the default shapefile is
        used, this would be the FIPS country code. Defaults to global.
    spatial_resolution : float, optional
        spatial resolution in degree, defaults to 0.25
    temporal_resolution : str, optional
        temporal resolution of the data, possible values: day, week,
        month, dekad, defaults to dekad
    tmp_path : str
        Path where temporary files and original files are stored and
        downloaded.
    data_path : str
        Path where resampled NetCDF file is stored.
    nan_value : int
        NaN value to use, defaults to -99.
    start_date : datetime.datetime, optional
        First date of the dataset, defaults to 2000-01-01.
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.
    sources : dict of poets.io.BasicSource objects
        Sources used by poets given as BasicSource class.
    delete_rawdata : bool, optional
        Original files will be deleted from tmp_path if set True.
    """

    def __init__(self, rootpath, regions=['global'],
                 spatial_resolution=0.25, temporal_resolution='dekad',
                 start_date=datetime(2000, 1, 1), nan_value=-99,
                 shapefile=None, delete_rawdata=False):

        self.rootpath = rootpath
        self.regions = regions
        self.spatial_resolution = spatial_resolution
        self.temporal_resolution = temporal_resolution
        self.tmp_path = os.path.join(rootpath, 'TMP')
        self.data_path = os.path.join(rootpath, 'DATA')
        self.nan_value = nan_value
        self.start_date = start_date
        self.shapefile = shapefile
        self.delete_rawdata = delete_rawdata
        self.sources = {}

    def add_source(self, name, filename, filedate, temp_res, host, protocol,
                   username=None, password=None, port=22, directory=None,
                   dirstruct=None, begin_date=datetime(2000, 1, 1),
                   variables=None, nan_value=None):

        source = BasicSource(name, filename, filedate, temp_res, self.rootpath,
                             host, protocol, username, password, port,
                             directory, dirstruct, begin_date, variables,
                             nan_value, self.nan_value, self.regions,
                             self.spatial_resolution, self.temporal_resolution,
                             self.start_date)

        self.sources[name] = source

    def fetch_data(self, begin=None, end=None, delete_rawdata=None):
        """Starts download and resampling of input data.

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

    def get_gridpoints(self, region):
        """Returns gridpoints from NetCDF file.

        Parameters
        ----------
        region : str
            Identifier of the region in the NetCDF file.

        Returns
        -------
        gridpoints : pandas.DataFrame
            Dataframe with gridpoint index as index, longitutes and latitudes
            as columns.
        """
        filename = region + '_' + str(self.spatial_resolution) + '.nc'
        ncfile = os.path.join(self.data_path, filename)

        with Dataset(ncfile, 'r+', format='NETCDF4') as nc:
            gpis = nc.variables['gpi'][:]
            lons = nc.variables['lon'][:]
            lats = nc.variables['lat'][:]
            gpis = gpis.flatten()
            lons, lats = np.meshgrid(lons, lats)
            lons = lons.flatten()
            lats = lats.flatten()

        gridpoints = pd.DataFrame(index=gpis)
        gridpoints['lon'] = lons
        gridpoints['lat'] = lats

        return gridpoints

if __name__ == "__main__":
    pass
