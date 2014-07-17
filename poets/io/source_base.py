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
# Creation date: 2014-06-30

import os
import pandas as pd
import numpy as np
import datetime
from poets.settings import Settings
from poets.timedate.dateindex import check_dekad, dekad_index, dekad2day
from netCDF4 import Dataset, num2date, date2num
from poets.image.resampling import resample_to_shape, average_layers
from poets.image.netcdf import save_image, write_tmp_file, get_properties, read_image


class BasicSource(object):
    """
    Base Class for data sources.

    Attributes
    ----------
    name : str
        Name of the data source
    source_path : str
        Link to data source
    filename : str
        Structure/convention of the file name
    dirstruct : list of strings
        Structure of source directory
        Each list item represents a subdirectory
    begin_date : datetime.date
        Date, from which on data is available
    variables : list of strings
        Variables used from data source
    """

    def __init__(self, name, source_path, filename, filedate, temp_res,
                 dirstruct, begin_date, variables):
        """
        init method
        """

        self.name = name
        self.source_path = source_path
        self.begin_date = begin_date
        self.filename = filename
        self.filedate = filedate
        self.temp_res = temp_res
        self.dirstruct = dirstruct
        self.variables = variables

    def _check_current_date(self, begin=True, end=True):
        """
        Helper method that checks the current date of individual variables in
        the netCDF data file.

        Returns
        -------
        dates : dict of dicts
            None if no date available
        """

        dates = {}

        for region in Settings.regions:
            nc_name = os.path.join(Settings.data_path, region + '_'
                                  + str(Settings.sp_res) + '.nc')
            if os.path.exists(nc_name):
                dates[region] = {}
                for var in self.variables:
                    ncvar = self.name + '_' + var
                    dates[region][var] = []
                    with Dataset(nc_name, 'r', format='NETCDF4') as ncfile:
                        if begin is True:
                        # check first date of data
                            for i in range(0,
                                            ncfile.variables['time'].size - 1):
                                if ncfile.variables[ncvar][i].mask.min() == True:
                                    continue
                                else:
                                    times = ncfile.variables['time']
                                    dat = num2date(ncfile.variables['time'][i],
                                                   units=times.units,
                                                   calendar=times.calendar)
                                    dates[region][var].append(dat)
                                    break
                        else:
                            dates[region][var].append(None)

                        if end is True:
                            # check last date of data
                            for i in range(ncfile.variables['time'].size - 1,
                                           - 1, -1):
                                if ncfile.variables[ncvar][i].mask.min() == True:
                                    continue
                                else:
                                    times = ncfile.variables['time']
                                    dat = num2date(ncfile.variables['time'][i],
                                                   units=times.units,
                                                   calendar=times.calendar)
                                    dates[region][var].append(dat)
                                    break
                        else:
                            dates[region][var].append(None)

            else:
                dates = None
                break

        return dates

    def get_file_date(self, fname):

        fname = str(fname)

        if 'YYYY' in self.filedate.keys():
            year = int(fname[self.filedate['YYYY'][0]:
                             self.filedate['YYYY'][1]])

        if 'MM' in self.filedate.keys():
            month = int(fname[self.filedate['MM'][0]:self.filedate['MM'][1]])

        if 'DD' in self.filedate.keys():
            day = int(fname[self.filedate['DD'][0]:self.filedate['DD'][1]])
        else:
            day = 1

        if 'P' in self.filedate.keys():
            dekad = int(fname[self.filedate['P'][0]:self.filedate['P'][1]])
            day = dekad2day(year, month, dekad)

        if 'hh' in self.filedate.keys():
            hour = int(fname[self.filedate['hh'][0]:self.filedate['hh'][1]])
        else:
            hour = 0

        if 'mm' in self.filedate.keys():
            minute = int(fname[self.filedate['mm'][0]:self.filedate['mm'][1]])
        else:
            minute = 0

        if 'ss' in self.filedate.keys():
            second = int(fname[self.filedate['ss'][0]:self.filedate['ss'][1]])
        else:
            second = 0

        return datetime.datetime(year, month, day, hour, minute, second)

    def _get_tmp_filepath(self, prefix, region):
        tmp_path = os.path.join(Settings.tmp_path, self.name)
        filename = ('_' + prefix + '_' + region + '_' + str(Settings.sp_res)
                    + '.nc')
        return os.path.join(tmp_path, filename)

    def _resample_spatial(self, region, begin, end, delete_rawdata):

        raw_files = []
        tmp_path = os.path.join(Settings.tmp_path, self.name)

        # filename if tmp file is used
        dest_file = self._get_tmp_filepath('spatial', region)

        dirList = os.listdir(tmp_path)
        dirList.sort()

        for item in dirList:

            src_file = os.path.join(tmp_path, item)
            raw_files.append(src_file)

            fdate = self.get_file_date(item)

            if begin is not None:
                if fdate < begin:
                    continue
            if end is not None:
                if fdate > end:
                    continue

            print '    ' + item

            image, _, _, _, timestamp, metadata = \
                resample_to_shape(src_file, region, self.name)

            if self.temp_res is 'dekad':
                save_image(image, timestamp, region, metadata)
            else:
                write_tmp_file(image, timestamp, region, metadata, dest_file)

            if delete_rawdata is True:
                print '[INFO] delete source files'
                os.unlink(src_file)

    def _resample_temporal(self, region):

        src_file = self._get_tmp_filepath('spatial', region)

        data = {}
        variables, _, period = get_properties(src_file)

        if Settings.temp_res is 'dekad':
            dtindex = dekad_index(period[0], end=period[1])

        for date in dtindex:
            if date.day < 21:
                begin = datetime.datetime(date.year, date.month,
                                          date.day - 10 + 1)
            else:
                begin = datetime.datetime(date.year, date.month, 21)
            end = date

            data = {}
            metadata = {}

            for var in variables:
                img, lon, lat, meta = \
                    read_image(src_file, region, var, begin, end)

                metadata[var] = meta
                data[var] = average_layers(img)

            save_image(data, date, region, metadata)

        # delete intermediate netCDF file
        print '[INFO] delete source files'
        os.unlink(src_file)

    def download(self):
        """"
        Virtual method, it has to be overriden by childs

        Raises
        ------
        NotImplementedError
            Raised if not overriden by childs
        """
        raise NotImplementedError()

    def resample(self, begin=None, end=None, delete_rawdata=False):
        """
        Resamples source data to predefined spatial and temporal resolution and
        writes them into the netCDF data file. Deletes original files if flag
        delete_rawdata is set True.

        Parameters
        ----------
        delete_rawdata : bool
            Original files will be deleted from tmp_path if set 'True'
        """

        for region in Settings.regions:

            print '[INFO] resampling to region ' + region
            print '  performing spatial resampling'

            self._resample_spatial(region, begin, end, delete_rawdata)

            if self.temp_res is 'dekad':
                print '  skipping temporal resampling'
            else:
                print '  performing temporal resampling'
                self._resample_temporal(region)

    def download_and_resample(self, download_path=None, begin=None, end=None,
                              delete_rawdata=False):
        """
        Downloads and resamples data

        Parameters
        ----------
        download_path : str
            Path where to save the downloaded files.
        begin : datetime.date
            Optional, set either to first date of remote repository or date of
            last file in local repository
        end : datetime.date
            Optional, set to today if none given
        delete_rawdata : bool
            Original files will be deleted from tmp_path if set 'True'

        Raises
        ------
        NotImplementedError
            Raised if method is not called from child class
        """

        self.download(download_path, begin, end)
        self.resample(begin=begin, end=end, delete_rawdata=delete_rawdata)

    def read_ts(self, gp, region=None, variable=None):
        """
        Gets timeseries from netCDF file for certain gridpoint

        Parameters
        ----------
        gp : int
            Grid point index
        region : str
            Region of interest, set to first defined region if not set
        variable : str
            Variable to display, selects all available variables if None

        Returns
        -------
        df : pd.DataFrame
            Timeseries for selected variables
        """

        if region is None:
            region = Settings.regions[0]

        if variable is None:
            variable = self.variables
        else:
            variable = [variable]

        source_file = os.path.join(Settings.data_path,
                                   region + '_' + str(Settings.sp_res)
                                   + '.nc')

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
                values = nc.variables[ncvar][begin:end + 1, lat_pos, lon_pos]
                df[ncvar][begin:end + 1] = values

                # Replaces NAN value with np.NAN
                df[ncvar][df[ncvar] == Settings.nan_value] = np.NAN
                df[ncvar]

        return df

    def read_img(self, date, region=None, variable=None):
        """
        Gets images from netCDF file for certain date

        Parameters
        ----------
        date : datetime.datetime
            Date of the image
        region : str
            Region of interest, set to first defined region if not set
        variable : str
            Variable to display, selects first available variables if None

        Returns
        -------
        img : numpy.ndarray
            Image of selected date
        """

        if region is None:
            region = Settings.regions[0]

        if variable is None:
            variable = self.variables[0]

        source_file = os.path.join(Settings.data_path,
                                   region + '_' + str(Settings.sp_res)
                                   + '.nc')

        # get dekad of date:
        date = check_dekad(date)

        with Dataset(source_file, 'r', format='NETCDF4') as nc:
            time = nc.variables['time']

            datenum = date2num(date, units=time.units, calendar=time.calendar)

            position = np.where(time[:] == datenum)[0][0]

            img = nc.variables[variable][position]

        return img

if __name__ == "__main__":
    pass
