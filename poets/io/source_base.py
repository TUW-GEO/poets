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
# Creation date: 2014-06-30

from datetime import datetime, timedelta
from netCDF4 import Dataset, num2date, date2num
from poets.grid.grids import ShapeGrid, RegularGrid
from poets.image.resampling import resample_to_shape, average_layers
from poets.io.download import download_http, download_ftp, download_sftp, \
    get_file_date, download_local
from poets.io.fileformats import select_file
from poets.io.unpack import unpack, check_compressed
import math as ma
import numpy as np
import os
import pandas as pd
import poets.grid.grids as gr
import poets.image.netcdf as nc
import poets.timedate.dateindex as dt
import shutil


class BasicSource(object):
    """Base Class for data sources.

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
    rootpath : str
        Root path where all data will be stored.
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
    dirstruct : list of strings, optional
        Structure of source directory, each list item represents a
        subdirectory.
    regions : list of str, optional
        List of regions where data from source is available. Uses all regions
        specified in dest_regions if not set.
    begin_date : datetime, optional
        Date from which on data is available.
    variables : string or list of strings, optional
        Variables used from data source, defaults to ['dataset'].
    nan_value : int, float, optional
        Nan value of the original data as given by the data provider.
    valid_range : tuple of int of float, optional
        Valid range of data, given as (minimum, maximum).
    data_range : tuple of int of float, optional
        Range of the values as data given in rawdata (minimum, maximum).
        Will be scaled to valid_range.
    ffilter : str, optional
        Pattern that apperas in filename. Can be used to select out not
        needed files if multiple files per date are provided.
    colorbar : str, optional
        Colorbar to use, use one from
        http://matplotlib.org/examples/color/colormaps_reference.html,
        defaults to jet.
    unit : str, optional
        Unit of dataset for displaying in legend. Does not have to be set
        if unit is specified in input file metadata. Defaults to None.
    dest_nan_value : int, float, optional
        NaN value in the final NetCDF file.
    dest_regions : list of str, optional
        Regions of interest where data should be resampled to.
    dest_sp_res : int, float, optional
        Spatial resolution of the destination NetCDF file, defaults to 0.25
        degree.
    dest_temp_res : string, optional
        Temporal resolution of the destination NetCDF file, possible values:
        ('day', 'week', 'dekad', 'month'), defaults to dekad.
    dest_start_date : datetime, optional
        Start date of the destination NetCDF file, defaults to 2000-01-01.
    src_file : dict of str, optional
        Path to file that contains source. Uses default NetCDF file if None.
        Key of dict must be regions as set in regions attribute.

    Attributes
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
    username : str
        Username for data access.
    password : str
        Password for data access.
    port : int
        Port to data host.
    directory : str
        Path to data on host.
    dirstruct : list of strings
        Structure of source directory, each list item represents a
        subdirectory.
    regions : list of str
        List of regions where data from source is available.
    begin_date : datetime
        Date from which on data is available.
    ffilter : str
        Pattern that apperas in filename.
    colorbar : str, optional
        Colorbar to used.
    unit : str
        Unit of dataset for displaying in legend.
    variables : list of strings
        Variables used from data source.
    nan_value : int, float
        Not a number value of the original data as given by the data provider.
    valid_range : tuple of int of float
        Valid range of data, given as (minimum, maximum).
    data_range : tuple of int of float
        Range of the values as data given in rawdata (minimum, maximum).
    dest_nan_value : int, float, optional
        NaN value in the final NetCDF file.
    tmp_path : str
        Path where temporary files are stored.
    rawdata_path : str
        Path where original files are stored.
    data_path : str
        Path where resampled NetCDF file is stored.
    dest_regions : list of str
        Regions of interest where data is resampled to.
    dest_sp_res : int, float
        Spatial resolution of the destination NetCDF file.
    dest_temp_res : string
        Temporal resolution of the destination NetCDF file.
    dest_start_date : datetime.datetime
        First date of the dataset in the destination NetCDF file.
    src_file : str, list of str
        Path to file that contains source.
    """

    def __init__(self, name, filename, filedate, temp_res, rootpath,
                 host, protocol, username=None, password=None, port=22,
                 directory=None, dirstruct=None, regions=None,
                 begin_date=None, ffilter=None, colorbar='jet',
                 variables=None, nan_value=None, valid_range=None, unit=None,
                 dest_nan_value=-99, dest_regions=None, dest_sp_res=0.25,
                 dest_temp_res='dekad', dest_start_date=datetime(2000, 1, 1),
                 data_range=None, src_file=None):

        self.name = name
        self.filename = filename
        self.filedate = filedate
        self.temp_res = temp_res
        self.host = host
        self.protocol = protocol
        self.username = username
        self.password = password
        self.port = port
        self.directory = directory
        self.dirstruct = dirstruct
        if begin_date is None:
            self.begin_date = dest_start_date
        else:
            self.begin_date = begin_date
        if type(variables) == str:
            self.variables = [variables]
        else:
            self.variables = variables
        self.ffilter = ffilter
        self.unit = unit
        self.nan_value = nan_value
        self.valid_range = valid_range
        self.data_range = data_range
        self.colorbar = colorbar
        if isinstance(regions, str):
            self.regions = [regions]
        else:
            self.regions = regions
        self.dest_nan_value = dest_nan_value
        if isinstance(dest_regions, str):
            self.dest_regions = [dest_regions]
        else:
            self.dest_regions = dest_regions
        self.dest_sp_res = dest_sp_res
        self.dest_temp_res = dest_temp_res
        self.dest_start_date = dest_start_date
        self.rawdata_path = os.path.join(rootpath, 'RAWDATA', name)
        self.tmp_path = os.path.join(rootpath, 'TMP')
        if not os.path.exists(self.tmp_path):
            os.mkdir(self.tmp_path)
        self.data_path = os.path.join(rootpath, 'DATA')
        if not os.path.exists(self.data_path):
            os.mkdir(self.data_path)

        if self.host[-1] != '/':
            self.host += '/'

        if self.directory is not None and self.directory[-1] != '/':
            self.directory += '/'

        if src_file is None:
            self.src_file = {}
            for reg in self.dest_regions:
                self.src_file[reg] = os.path.join(self.data_path, reg + '_' +
                                                  str(self.dest_sp_res) + '_'
                                                  + str(self.dest_temp_res)
                                                  + '.nc')
        else:
            self.src_file = src_file

    def _check_current_date(self, begin=True, end=True):
        """Helper method that checks the current date of individual variables
        in the netCDF data file.

        Parameters
        ----------
        begin : bool, optional
            If set True, begin will be returned as None.
        end : bool, optional
            If set True, end will be returned as None.
        Returns
        -------
        dates : dict of dicts
            Dictionary with dates of each parameter. None if no date available.
        """

        dates = {}

        for region in self.dest_regions:

            if self.regions is not None:
                if region not in self.regions:
                    continue

            nc_name = self.src_file[region]

            if os.path.exists(nc_name):
                dates[region] = {}

                variables = self.get_variables()

                with Dataset(nc_name, 'r', format='NETCDF4') as nc:
                    for var in variables:
                        dates[region][var] = []
                        if begin:
                            for i in range(0, nc.variables['time'].size - 1):
                                if(nc.variables[var][i].mask.min() or
                                   ma.isnan(np.nanmax(nc.variables[var][i]))):
                                    continue
                                else:
                                    times = nc.variables['time']
                                    dat = num2date(nc.variables['time'][i],
                                                   units=times.units,
                                                   calendar=times.calendar)
                                    dates[region][var].append(dat)
                                    break
                        else:
                            dates[region][var].append(None)

                        if end:
                            for i in range(nc.variables['time'].size - 1,
                                           - 1, -1):
                                if(nc.variables[var][i].mask.min() or
                                   ma.isnan(np.nanmax(nc.variables[var][i]))):
                                    continue
                                else:
                                    times = nc.variables['time']
                                    dat = num2date(nc.variables['time'][i],
                                                   units=times.units,
                                                   calendar=times.calendar)
                                    dates[region][var].append(dat)
                                    break
                        else:
                            dates[region][var].append(None)

                        if dates[region][var] in [[None], []]:
                            dates[region][var] = [None, None]
            else:
                dates = None
                break

        return dates

    def _get_download_date(self):
        """Gets the date from which to start the data download.

        Returns
        -------
        begin : datetime
            date from which to start the data download.
        """

        dates = self._check_current_date(begin=False)

        if dates is not None:
            begin = datetime.now()
            for region in self.dest_regions:

                if self.regions is not None:
                    if region not in self.regions:
                        continue

                variables = self.get_variables()
                if variables == []:
                    begin = self.dest_start_date
                else:
                    for var in variables:
                        if dates[region][var][1] is not None:
                            if dates[region][var][1] < begin:
                                begin = dates[region][var][1]
                                begin += timedelta(days=1)
                        else:
                            if self.dest_start_date < self.begin_date:
                                begin = self.begin_date
                            else:
                                begin = self.dest_start_date
        else:
            begin = self.begin_date

        return begin

    def _get_tmp_filepath(self, prefix, region):
        """Creates path to a temporary directory.

        Returns
        -------
        str
            Path to the temporary direcotry
        """
        filename = ('_' + prefix + '_' + region + '_' + str(self.dest_sp_res)
                    + '_' + str(self.dest_temp_res) + '.nc')
        return os.path.join(self.tmp_path, filename)

    def _resample_spatial(self, region, begin, end, delete_rawdata,
                          shapefile=None):
        """Helper method that calls spatial resampling routines.

        Parameters:
        region : str
            FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)
        begin : datetime
            Start date of resampling
        end : datetime
            End date of resampling
        delete_rawdata : bool
            True if original downloaded files should be deleted after
            resampling
        """

        dest_file = self._get_tmp_filepath('spatial', region)

        dirList = os.listdir(self.rawdata_path)
        dirList.sort()

        if region == 'global':
            grid = gr.RegularGrid(sp_res=self.dest_sp_res)
        else:
            grid = gr.ShapeGrid(region, self.dest_sp_res, shapefile)

        for item in dirList:

            src_file = os.path.join(self.rawdata_path, item)

            fdate = get_file_date(item, self.filedate)

            if begin is not None:
                if fdate < begin:
                    continue

            if end is not None:
                if fdate > end:
                    continue

            if check_compressed(src_file):
                dirname = os.path.splitext(item)[0]
                dirpath = os.path.join(self.rawdata_path, dirname)
                unpack(src_file)
                src_file = select_file(os.listdir(dirpath))
                src_file = os.path.join(dirpath, src_file)

            if begin is not None:
                if fdate < begin:
                    if check_compressed(item):
                        shutil.rmtree(os.path.join(self.rawdata_path,
                                                   os.path.splitext(item)[0]))
                    continue
            if end is not None:
                if fdate > end:
                    if check_compressed(item):
                        shutil.rmtree(os.path.join(self.rawdata_path,
                                                   os.path.splitext(item)[0]))
                    continue

            print '.',

            image, _, _, _, timestamp, metadata = \
                resample_to_shape(src_file, region, self.dest_sp_res, grid,
                                  self.name, self.nan_value,
                                  self.dest_nan_value, self.variables,
                                  shapefile)

            if timestamp is None:
                timestamp = get_file_date(item, self.filedate)

            if self.temp_res == self.dest_temp_res:
                filename = (region + '_' + str(self.dest_sp_res) + '_'
                            + str(self.dest_temp_res) + '.nc')
                dfile = os.path.join(self.data_path, filename)
                nc.save_image(image, timestamp, region, metadata, dfile,
                              self.dest_start_date, self.dest_sp_res,
                              self.dest_nan_value, shapefile,
                              self.dest_temp_res)
            else:
                nc.write_tmp_file(image, timestamp, region, metadata,
                                  dest_file, self.dest_start_date,
                                  self.dest_sp_res, self.dest_nan_value,
                                  shapefile)

            # deletes unpacked files if existing
            if check_compressed(item):
                shutil.rmtree(os.path.join(self.rawdata_path,
                                           os.path.splitext(item)[0]))

        print ''

    def _resample_temporal(self, region, shapefile=None):
        """Helper method that calls temporal resampling routines.

        Parameters:
        region : str
            Identifier of the region in the shapefile. If the default shapefile
            is used, this would be the FIPS country code.

        shapefile : str, optional
            Path to shape file, uses "world country admin boundary shapefile"
            by default.
        """

        src_file = self._get_tmp_filepath('spatial', region)

        if not os.path.exists(src_file):
            print '[Info] No data available for this period'
            return False

        data = {}
        variables, _, period = nc.get_properties(src_file)

        dtindex = dt.get_dtindex(self.dest_temp_res, period[0], period[1])

        for date in dtindex:
            # skip if data for period is not complete
            # if date > period[1]:
            #    continue
            if self.dest_temp_res == 'dekad':
                if date.day < 21:
                    begin = datetime(date.year, date.month, date.day - 10 + 1)
                else:
                    begin = datetime(date.year, date.month, 21)
                end = date
            else:
                begin = period[0]
                end = date

            data = {}
            metadata = {}

            for var in variables:
                img, _, _, meta = \
                    nc.read_variable(src_file, var, begin, end)

                metadata[var] = meta
                data[var] = average_layers(img, self.dest_nan_value)

            dest_file = self.src_file[region]

            nc.save_image(data, date, region, metadata, dest_file,
                          self.dest_start_date, self.dest_sp_res,
                          self.dest_nan_value, shapefile, self.dest_temp_res)

        # delete intermediate netCDF file
        print ''
        os.unlink(src_file)

    def _scale_values(self, data):

        if self.valid_range is not None:
            if self.data_range is not None:
                data = ((data - self.data_range[0]) /
                        (self.data_range[1] - self.data_range[0]) *
                        (self.valid_range[1] - self.valid_range[0]) +
                        self.valid_range[0])

        return data

    def download(self, download_path=None, begin=None, end=None):
        """"Download data

        Parameters
        ----------
        begin : datetime, optional
            start date of download, default to None
        end : datetime, optional
            start date of download, default to None
        """

        if begin is None:
            if self.dest_start_date < self.begin_date:
                begin = self.begin_date
            else:
                begin = self.dest_start_date

        if self.protocol in ['HTTP', 'http']:
            check = download_http(self.rawdata_path, self.host,
                                  self.directory, self.filename, self.filedate,
                                  self.dirstruct, begin=begin, end=end,
                                  ffilter=self.ffilter)
        elif self.protocol in ['FTP', 'ftp']:
            check = download_ftp(self.rawdata_path, self.host, self.directory,
                                 self.filedate, self.port, self.username,
                                 self.password, self.dirstruct, begin=begin,
                                 end=end, ffilter=self.ffilter)
        elif self.protocol in ['SFTP', 'sftp']:
            check = download_sftp(self.rawdata_path, self.host,
                                  self.directory, self.port, self.username,
                                  self.password, self.filedate, self.dirstruct,
                                  begin=begin, end=end, ffilter=self.ffilter)
        elif self.protocol in ['local', 'LOCAL']:
            check = download_local(self.rawdata_path, directory=self.host,
                                   filedate=self.filedate,
                                   dirstruct=self.dirstruct, begin=begin,
                                   end=end, ffilter=self.ffilter)

        return check

    def resample(self, begin=None, end=None, delete_rawdata=False,
                 shapefile=None, stepwise=True):
        """Resamples source data to given spatial and temporal resolution.

        Writes resampled images into a netCDF data file. Deletes original
        files if flag delete_rawdata is set True.

        Parameters
        ----------
        begin : datetime
            Start date of resampling.
        end : datetime
            End date of resampling.
        delete_rawdata : bool
            Original files will be deleted from rawdata_path if set 'True'.
        shapefile : str, optional
            Path to shape file, uses "world country admin boundary shapefile"
            by default.
        """

        if len(os.listdir(self.tmp_path)) != 0:
            for fname in os.listdir(self.tmp_path):
                if '.nc' in fname:
                    os.remove(os.path.join(self.tmp_path, fname))

        # clean rawdata folder from sudirectories
        for item in os.listdir(self.rawdata_path):
            if os.path.isdir(os.path.join(self.rawdata_path, item)):
                os.rmdir(os.path.join(self.rawdata_path, item))

        begin, end = self._check_begin_end(begin, end)

        if begin > end:
            print '[INFO] everything up to date'
            return '[INFO] everything up to date'

        if stepwise:

            drange = dt.get_dtindex(self.dest_temp_res, begin, end)

            for i, date in enumerate(drange):
                if i == 0:
                    start = begin
                else:
                    if self.dest_temp_res in ['dekad', 'dekadal', 'week',
                                              'weekly', 'month', 'monthly']:
                        start = drange[i - 1] + timedelta(days=1)
                    else:
                        start = date

                stop = date

                print '[INFO] Resampling ' + str(start) + ' to ' + str(stop)

                for region in self.dest_regions:

                    if self.regions is not None:
                        if region not in self.regions:
                            continue

                    print '[INFO] resampling to region ' + region
                    print '[INFO] performing spatial resampling ',

                    self._resample_spatial(region, start, stop, delete_rawdata,
                                           shapefile)

                    if self.temp_res == self.dest_temp_res:
                        print '[INFO] skipping temporal resampling'
                    else:
                        print '[INFO] performing temporal resampling ',
                        self._resample_temporal(region, shapefile)

        else:

            print '[INFO] ' + str(begin) + '-' + str(end)

            for region in self.dest_regions:

                if self.regions is not None:
                    if region not in self.regions:
                        continue

                print '[INFO] resampling to region ' + region
                print '[INFO] performing spatial resampling ',

                self._resample_spatial(region, begin, end, delete_rawdata,
                                       shapefile)

                if self.temp_res == self.dest_temp_res:
                    print '[INFO] skipping temporal resampling'
                else:
                    print '[INFO] performing temporal resampling ',
                    self._resample_temporal(region, shapefile)

        if delete_rawdata:
            print '[INFO] Cleaning up rawdata'
            dirList = os.listdir(self.rawdata_path)
            dirList.sort()

            for item in dirList:
                src_file = os.path.join(self.rawdata_path, item)
                os.unlink(src_file)

    def download_and_resample(self, download_path=None, begin=None, end=None,
                              delete_rawdata=False, shapefile=None):
        """Downloads and resamples data.

        Parameters
        ----------
        download_path : str
            Path where to save the downloaded files.
        begin : datetime.date, optional
            set either to first date of remote repository or date of
            last file in local repository
        end : datetime.date, optional
            set to today if none given
        delete_rawdata : bool, optional
            Original files will be deleted from rawdata_path if set True
        shapefile : str, optional
            Path to shape file, uses "world country admin boundary shapefile"
            by default.
        """

        begin, end = self._check_begin_end(begin, end)

        if begin > end:
            print '[INFO] everything up to date'
            return '[INFO] everything up to date'

        drange = dt.get_dtindex(self.dest_temp_res, begin, end)

        for i, date in enumerate(drange):
            if i == 0:
                start = begin
            else:
                if self.dest_temp_res in ['dekad', 'dekadal', 'week',
                                          'weekly', 'month', 'monthly']:
                    start = drange[i - 1] + timedelta(days=1)
                else:
                    start = date

            stop = date

            filecheck = self.download(download_path, start, stop)
            if filecheck is True:
                self.resample(start, stop, delete_rawdata, shapefile, False)
            else:
                print '[WARNING] no data available for this date'

    def read_ts(self, location, region=None, variable=None, shapefile=None,
                scaled=True):
        """Gets timeseries from netCDF file for a gridpoint.

        Parameters
        ----------
        location : int or tuple of floats
            Either Grid point index as integer value or Longitude/Latitude
            given as tuple.
        region : str, optional
            Region of interest, set to first defined region if not set.
        variable : str, optional
            Variable to display, selects all available variables if None.
        shapefile : str, optional
            Path to custom shapefile.
        scaled : bool, optional
            If true, data will be scaled to a predefined range; if false, data
            will be shown as given in rawdata file; defaults to True

        Returns
        -------
        df : pd.DataFrame
            Timeseries for selected variables.
        """

        if region is None:
            region = self.dest_regions[0]

        if type(location) is tuple:
            if region == 'global':
                grid = RegularGrid(self.dest_sp_res)
            else:
                grid = ShapeGrid(region, self.dest_sp_res, shapefile)

            gp, _ = grid.find_nearest_gpi(location[0], location[1])
        else:
            gp = location

        if variable is None:
            variable = self.get_variables()
        else:
            variable = self.check_variable(variable)
            variable = [variable]

        source_file = self.src_file[region]

        var_dates = self._check_current_date()

        with Dataset(source_file, 'r', format='NETCDF4') as nc:

            time = nc.variables['time']
            dates = num2date(time[:], units=time.units, calendar=time.calendar)
            position = np.where(nc.variables['gpi'][:] == gp)
            lat_pos = position[0][0]
            lon_pos = position[1][0]
            df = pd.DataFrame(index=pd.DatetimeIndex(dates))

            for ncvar in variable:
                begin = np.where(dates == var_dates[region][ncvar][0])[0][0]
                end = np.where(dates == var_dates[region][ncvar][1])[0][0]
                df[ncvar] = np.NAN
                for i in range(begin, end + 1):
                    df[ncvar][i] = nc.variables[ncvar][i, lat_pos, lon_pos]

                if 'scaling_factor' in nc.variables[ncvar].ncattrs():
                    vvar = nc.variables[ncvar]
                    if vvar.getncattr('scaling_factor') < 0:
                        df[ncvar] = (df[ncvar] *
                                     float(vvar.getncattr('scaling_factor')))
                    else:
                        df[ncvar] = (df[ncvar] /
                                     float(vvar.getncattr('scaling_factor')))
                if scaled:
                    if self.valid_range is not None:
                        if self.data_range is not None:
                            df[ncvar] = self._scale_values(df[ncvar])

        return df

    def read_img(self, date, region=None, variable=None, scaled=True):
        """Gets images from netCDF file for certain date

        Parameters
        ----------
        date : datetime
            Date of the image.
        region : str, optional
            Region of interest, set to first defined region if not set.
        variable : str, optional
            Variable to display, selects first available variables if None.
        scaled : bool, optional
            If true, data will be scaled to a predefined range; if false, data
            will be shown as given in rawdata file; defaults to True.

        Returns
        -------
        img : numpy.ndarray
            Image of selected date.
        lon : numpy.array
            Array with longitudes.
        lat : numpy.array
            Array with latitudes.
        metadata : dict
            Dictionary containing metadata of the variable.
        """

        if region is None:
            region = self.dest_regions[0]

        if variable is None:
            variable = self.get_variables()[0]
        else:
            # Renames variable name to SOURCE_variable
            variable = self.check_variable(variable)

        source_file = self.src_file[region]

        # get dekad of date:
        date = dt.check_period(self.dest_temp_res, date)

        with Dataset(source_file, 'r', format='NETCDF4') as nc:
            time = nc.variables['time']

            datenum = date2num(date, units=time.units, calendar=time.calendar)

            position = np.where(time[:] == datenum)[0][0]

            var = nc.variables[variable]
            img = var[position]
            lon = nc.variables['lon'][:]
            lat = nc.variables['lat'][:]

            metadata = {}

            for attr in var.ncattrs():
                if attr[0] != '_' and attr != 'scale_factor':
                    metadata[attr] = var.getncattr(attr)

            if not metadata:
                metadata = None

            if 'scaling_factor' in var.ncattrs():
                if metadata['scaling_factor'] < 0:
                    img = img * float(metadata['scaling_factor'])
                else:
                    img = img / float(metadata['scaling_factor'])

        if scaled:
            if self.valid_range is not None:
                if self.data_range is not None:
                    img = self._scale_values(img)

        return img, lon, lat, metadata

    def get_variables(self):
        """
        Gets all variables given in the NetCDF file.

        Returns
        -------
        variables : list of str
            Variables from given in the NetCDF file.
        """

        # nc_name = self.src_file[self.dest_regions[0]]

        # nc_vars, _, _ = nc.get_properties(nc_name)

        nc_vars = []
        for reg in self.dest_regions:
            vari, _, _ = nc.get_properties(self.src_file[reg])
            if vari is None:
                continue
            for v in vari:
                if v not in nc_vars:
                    nc_vars.append(v)

        variables = []

        if self.variables is not None:
            for var in self.variables:
                if var in nc_vars:
                    variables.append(var)
                else:
                    if self.name + '_' + var in nc_vars:
                        variables.append(self.name + '_' + var)
        else:
            for var in nc_vars:
                if self.name + '_dataset' in var:
                    variables.append(var)
                elif self.name in var:
                    variables.append(var)

        return variables

    def check_variable(self, variable):
        """
        Checks if a variable exists in a source and returns it's correct name.

        Parameters
        ----------
        variable : str
            Variable to check.

        Returns
        -------
        varname : str
            Name of the variable in the source.
        """

        varname = ''

        if self.variables is not None:
            for var in self.variables:
                if variable in var:
                    varname = variable
                    break
                elif self.name + '_' + variable in var:
                    varname = self.name + '_' + variable
                    break
                else:
                    if variable == self.name + '_' + var:
                        varname = self.name + '_' + var
                        break

        else:
            for var in self.get_variables():
                if variable == var:
                    varname = variable
                    break
                else:
                    if self.name + '_' + variable in var:
                        varname = self.name + '_' + variable
                        break

        return varname

    def _check_begin_end(self, begin, end):
        """
        Checks begin and end date and returns valid dates.

        Parameters
        ----------
        begin : datetime
            Begin date to check.
        end : datetime
            End date to check.

        Returns
        -------
        begin : datetime
            Begin date.
        end : datetime
            End date.
        """

        if begin is None:
            if self.dest_start_date < self.begin_date:
                begin = self.begin_date
            else:
                begin = self.dest_start_date

            if begin < self._get_download_date():
                begin = self._get_download_date()

            # start one period earlier to close possible gaps
            begin = begin - timedelta(days=1)
            begin, _ = dt.check_period_boundaries(self.dest_temp_res, begin)
            if begin < self.begin_date:
                begin = self.begin_date
            if begin < self.dest_start_date:
                begin = self.dest_start_date

        if end is None:
            end = datetime.now()

        return begin, end

    def fill_gaps(self, begin=None, end=None):
        """
        Detects gaps in data and tries to fill them by downloading and
        resampling the data within these periods.
        
        Parameters
        ----------
        begin : datetime
            Begin date of intervall to check, defaults to None.
        end : datetime
            End date of intervall to check, defaults to None.
        """

        gaps = []

        for region in self.dest_regions:

            if self.regions is not None:
                if region not in self.regions:
                    continue

            _, _, period = nc.get_properties(self.src_file[region])
            if begin is None:
                if self.begin_date < self.dest_start_date:
                    begin = self.dest_start_date
                else:
                    begin = self.begin_date
            if end is None:
                end = period[1]
            drange = dt.get_dtindex(self.dest_temp_res, begin, end)
            for date in drange:
                nonans = []
                for var in self.get_variables():
                    img, _, _, _ = self.read_img(date, region, var)
                    if np.nanmean(img) is not np.ma.masked:
                        nonans.append(1)
                if len(nonans) == 0:
                    if date not in gaps:
                        gaps.append(date)

        if len(gaps) == 0:
            print '[INFO] No gaps found.'
        else:
            print '[INFO] Found ' + str(len(gaps)) + ' gap(s), attempt to fill..'
            for date in gaps:
                if self.dest_temp_res in ['day', 'daily']:
                    begin = date
                    end = date
                else:
                    begin, end = dt.check_period_boundaries(self.dest_temp_res,
                                                            date)

                self.download_and_resample(begin=begin, end=end)
