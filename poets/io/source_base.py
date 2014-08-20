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

import datetime
import os

from netCDF4 import Dataset, num2date, date2num

import numpy as np
import pandas as pd
import poets.image.netcdf as nt
from poets.image.resampling import resample_to_shape, average_layers
from poets.io.download import download_http, download_ftp, download_sftp, \
    get_file_date
import poets.timedate.dateindex as dt
from poets.timedate.dekad import check_dekad


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
    dirstruct : list of strings
        Structure of source directory, each list item represents a
        subdirectory.
    begin_date : datetime.date, optional
        Date from which on data is available, defaults to 2000-01-01.
    variables : list of strings, optional
        Variables used from data source, defaults to ['dataset'].
    nan_value : int, float, optional
        Nan value of the original data as given by the data provider.
    dest_nan_value : int, float, optional
        NaN value in the final NetCDF file.
    dest_regions : list of str, optional
        Regions of interest where data should be resampled to.
    dest_sp_res : int, float, optional
        Spatial resolution of the destination NetCDF file, defaults to 0.25
        degree.
    dest_temp_res : string, optional
        Temporal resolution of the destination NetCDF file, possible values:
        ('month', 'dekad'), defaults to dekad.
    dest_start_date : datetime.datetime, optional
        Start date of the destination NetCDF file, defaults to 2000-01-01.

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
    begin_date : datetime.date
        Date from which on data is available.
    variables : list of strings
        Variables used from data source.
    nan_value : int, float
        N a number value of the original data as given by the data provider.
    dest_nan_value : int, float, optional
        NaN value in the final NetCDF file.
    tmp_path : str
        Path where temporary files and original files are stored and
        downloaded.
    data_path : str
        Path where resampled NetCDF file is stored.
    dest_regions : list of str
        Regions of interest where data is resampled to.
    dest_sp_res : int, float
        Spatial resolution of the destination NetCDF file.
    dest_temp_res : string
        Temporal resolution of the destination NetCDF file.
    """

    def __init__(self, name, filename, filedate, temp_res, rootpath,
                 host, protocol, username=None, password=None, port=22,
                 directory=None, dirstruct=None,
                 begin_date=datetime.datetime(2000, 1, 1),
                 variables=['dataset'],
                 nan_value=None, dest_nan_value=-99, dest_regions=None,
                 dest_sp_res=0.25, dest_temp_res='dekad',
                 dest_start_date=datetime.datetime(2000, 1, 1)):

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
        self.begin_date = begin_date
        self.variables = variables
        self.nan_value = nan_value
        self.dest_nan_value = dest_nan_value
        self.dest_regions = dest_regions
        self.dest_sp_res = dest_sp_res
        self.dest_temp_res = dest_temp_res
        self.dest_start_date = dest_start_date
        self.tmp_path = os.path.join(rootpath, 'TMP', name)
        self.data_path = os.path.join(rootpath, 'DATA')

        if self.host[-1] != '/':
            self.host += '/'

        if self.directory is not None and self.directory[-1] != '/':
            self.directory += '/'

    def _check_current_date(self, begin=True, end=True):
        """Helper method that checks the current date of individual variables
        in the netCDF data file.

        Parameters
        ----------
        begin : bool, optional
            If set True, begin will be returned as None
        end : bool, optional
            If set True, end will be returned as None
        Returns
        -------
        dates : dict of dicts
            None if no date available
        """

        dates = {}

        for region in self.dest_regions:
            nc_name = os.path.join(self.data_path, region + '_'
                                   + str(self.dest_sp_res) + '_'
                                   + str(self.dest_temp_res) + '.nc')
            if os.path.exists(nc_name):
                dates[region] = {}
                for var in self.variables:
                    ncvar = self.name + '_' + var
                    dates[region][var] = []
                    with Dataset(nc_name, 'r', format='NETCDF4') as nc:
                        if begin:
                            # check first date of data
                            if ncvar in nc.variables.keys():
                                for i in range(0, nc.variables['time'].size - 1):
                                    if nc.variables[ncvar][i].mask.min():
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
                        else:
                            dates[region][var].append(None)

                        if end is True:
                            # check last date of data
                            if ncvar in nc.variables.keys():
                                for i in range(nc.variables['time'].size - 1,
                                               - 1, -1):
                                    if nc.variables[ncvar][i].mask.min():
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
                        else:
                            dates[region][var].append(None)

            else:
                dates = None
                break

        return dates

    def _get_download_date(self):
        """Gets the date from which to start the data download.

        Returns
        -------
        begin : datetime.datetime
            date from which to start the data download.
        """
        dates = self._check_current_date(begin=False)
        if dates is not None:
            begin = datetime.datetime.now()
            for region in self.dest_regions:
                for var in self.variables:
                    if dates[region][var][1] is not None:
                        if dates[region][var][1] < begin:
                            begin = dates[region][var][1]
                            begin += datetime.timedelta(days=1)
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
        begin : datetime.datetime
            Start date of resampling
        end : datetime.datetime
            End date of resampling
        delete_rawdata : bool
            True if original downloaded files should be deleted after
            resampling
        """

        raw_files = []

        # filename if tmp file is used
        dest_file = self._get_tmp_filepath('spatial', region)

        dirList = os.listdir(self.tmp_path)
        dirList.sort()

        for item in dirList:

            src_file = os.path.join(self.tmp_path, item)
            raw_files.append(src_file)

            fdate = get_file_date(item, self.filedate)

            if begin is not None:
                if fdate < begin:
                    continue
            if end is not None:
                if fdate > end:
                    continue
            else:
                print '.',

            image, _, _, _, timestamp, metadata = \
                resample_to_shape(src_file, region, self.dest_sp_res,
                                  self.name, self.nan_value,
                                  self.dest_nan_value, shapefile)

            if timestamp is None:
                timestamp = get_file_date(item, self.filedate)

            if self.temp_res == self.dest_temp_res:
                filename = (region + '_' + str(self.dest_sp_res) + '_'
                            + str(self.dest_temp_res) + '.nc')
                dfile = os.path.join(self.data_path, filename)
                nt.save_image(image, timestamp, region, metadata, dfile,
                              self.dest_start_date, self.dest_sp_res,
                              self.dest_nan_value, shapefile)
            else:
                nt.write_tmp_file(image, timestamp, region, metadata,
                                  dest_file, self.dest_start_date,
                                  self.dest_sp_res, self.dest_nan_value,
                                  shapefile)

            if delete_rawdata:
                os.unlink(src_file)
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
        variables, _, period = nt.get_properties(src_file)

        dtindex = dt.get_dtindex(self.dest_temp_res, period[0], period[1])

        for date in dtindex:
            if date > period[1]:
                continue
            print date
            if self.dest_temp_res == 'dekad':
                if date.day < 21:
                    begin = datetime.datetime(date.year, date.month,
                                              date.day - 10 + 1)
                else:
                    begin = datetime.datetime(date.year, date.month, 21)
                end = date
            else:
                begin = period[0]
                end = date

            data = {}
            metadata = {}

            for var in variables:
                img, _, _, meta = \
                    nt.read_image(src_file, var, begin, end)

                metadata[var] = meta
                data[var] = average_layers(img, self.dest_nan_value)

            filename = (region + '_' + str(self.dest_sp_res) + '_'
                        + str(self.dest_temp_res) + '.nc')
            dest_file = os.path.join(self.data_path, filename)

            nt.save_image(data, date, region, metadata, dest_file,
                          self.dest_start_date, self.dest_sp_res,
                          self.dest_nan_value, shapefile, self.dest_temp_res)

        # delete intermediate netCDF file
        print ''
        os.unlink(src_file)

    def download(self, download_path=None, begin=None, end=None):
        """"Download data

        Parameters
        ----------
        begin : datetime.datetime, optional
            start date of download, default to None
        end : datetime.datetime, optional
            start date of download, default to None
        """

        if begin is None:
            if self.dest_start_date < self.begin_date:
                begin = self.begin_date
            else:
                begin = self.dest_start_date

        if self.protocol in ['HTTP', 'http']:
            check = download_http(self.tmp_path, self.host,
                                  self.directory, self.filename, self.filedate,
                                  self.dirstruct, begin, end=end)
        elif self.protocol in ['FTP', 'ftp']:
            check = download_ftp(self.tmp_path, self.host, self.directory,
                                 self.port, self.username, self.password,
                                 self.filedate, self.dirstruct, begin, end=end)

        elif self.protocol in ['SFTP', 'sftp']:
            check = download_sftp(self.tmp_path, self.host,
                                  self.directory, self.port, self.username,
                                  self.password, self.filedate, self.dirstruct,
                                  begin, end=end)

        return check

    def resample(self, begin=None, end=None, delete_rawdata=False,
                 shapefile=None):
        """Resamples source data to given spatial and temporal resolution.

        Writes resampled images into a netCDF data file. Deletes original
        files if flag delete_rawdata is set True.

        Parameters
        ----------
        begin : datetime.datetime
            Start date of resampling.
        end : datetime.datetime
            End date of resampling.
        delete_rawdata : bool
            Original files will be deleted from tmp_path if set 'True'.
        shapefile : str, optional
            Path to shape file, uses "world country admin boundary shapefile"
            by default.
        """

        for region in self.dest_regions:

            print '[INFO] resampling to region ' + region
            print '[INFO] performing spatial resampling ',

            self._resample_spatial(region, begin, end, delete_rawdata,
                                   shapefile)

            if self.temp_res == self.dest_temp_res:
                print '[INFO] skipping temporal resampling'
            else:
                print '[INFO] performing temporal resampling ',
                self._resample_temporal(region, shapefile)

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
            Original files will be deleted from tmp_path if set True
        shapefile : str, optional
            Path to shape file, uses "world country admin boundary shapefile"
            by default.
        """

        if begin is None:
            if self.dest_start_date < self.begin_date:
                begin = self.begin_date
            else:
                begin = self.dest_start_date

            if begin < self._get_download_date():
                begin = self._get_download_date()

        if end is None:
            end = datetime.datetime.now()

        drange = dt.get_dtindex(self.dest_temp_res, begin, end)

        for i, date in enumerate(drange):
            if date > end:
                continue
            if i == 0:
                start = begin
            else:
                if self.dest_temp_res == 'dekad':
                    start = drange[i - 1] + datetime.timedelta(days=1)
                else:
                    start = date

            stop = date

            filecheck = self.download(download_path, start, stop)
            if filecheck is True:
                self.resample(start, stop, delete_rawdata, shapefile)
            else:
                print '[WARNING] no data available for this date'

    def read_ts(self, gp, region=None, variable=None):
        """Gets timeseries from netCDF file for a gridpoint.

        Parameters
        ----------
        gp : int
            Grid point index.
        region : str, optional
            Region of interest, set to first defined region if not set.
        variable : str, optional
            Variable to display, selects all available variables if None.

        Returns
        -------
        df : pd.DataFrame
            Timeseries for selected variables.
        """

        if region is None:
            region = self.dest_regions[0]

        if variable is None:
            variable = self.variables
        else:
            variable = [variable]

        source_file = os.path.join(self.data_path,
                                   region + '_' + str(self.dest_sp_res) + '_'
                                   + str(self.dest_temp_res) + '.nc')

        var_dates = self._check_current_date()

        with Dataset(source_file, 'r', format='NETCDF4') as nc:

            time = nc.variables['time']
            dates = num2date(time[:], units=time.units, calendar=time.calendar)
            position = np.where(nc.variables['gpi'][:] == gp)
            lat_pos = position[0][0]
            lon_pos = position[1][0]
            df = pd.DataFrame(index=pd.DatetimeIndex(dates))

            for var in variable:
                begin = np.where(dates == var_dates[region][var][0])[0][0]
                end = np.where(dates == var_dates[region][var][1])[0][0]

                # Renames variable name to SOURCE_variable
                ncvar = self.name + '_' + var
                df[ncvar] = np.NAN
                for i in range(begin, end + 1):
                    df[ncvar][i] = nc.variables[ncvar][i, lat_pos, lon_pos]

        return df

    def read_img(self, date, region=None, variable=None):
        """Gets images from netCDF file for certain date

        Parameters
        ----------
        date : datetime.datetime
            Date of the image.
        region : str, optional
            Region of interest, set to first defined region if not set.
        variable : str, optional
            Variable to display, selects first available variables if None.

        Returns
        -------
        img : numpy.ndarray
            Image of selected date.
        lon : numpy.array
            Array with longitudes.
        lat : numpy.array
            Array with latitudes.
        """

        if region is None:
            region = self.dest_regions[0]

        if variable is None:
            variable = self.name + '_' + self.variables[0]

        source_file = os.path.join(self.data_path,
                                   region + '_' + str(self.dest_sp_res)
                                   + '_' + str(self.dest_temp_res) + '.nc')

        # get dekad of date:
        date = check_dekad(date)

        with Dataset(source_file, 'r', format='NETCDF4') as nc:
            time = nc.variables['time']

            datenum = date2num(date, units=time.units, calendar=time.calendar)

            position = np.where(time[:] == datenum)[0][0]

            img = nc.variables[variable][position]
            lon = nc.variables['lon'][:]
            lat = nc.variables['lat'][:]

        return img, lon, lat

if __name__ == "__main__":
    pass
