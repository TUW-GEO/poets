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
from poets.settings import Settings
from poets.timedate.dateindex import check_dekad
from netCDF4 import Dataset, num2date, date2num
from poets.image.resampling import resample_to_shape
from poets.image.netcdf import save_image, write_tmp_file


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

    def __init__(self, name, source_path, filename, temp_res, dirstruct,
                 begin_date, variables):
        """
        init method
        """

        self.name = name
        self.source_path = source_path
        self.begin_date = begin_date
        self.filename = filename
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

    def resample(self, delete_rawdata=False):
        """
        Resamples source data to predefined spatial and temporal resolution and
        writes them into the netCDF data file. Deletes original files if flag
        delete_rawdata is set True.

        Parameters
        ----------
        delete_rawdata : bool
            Original files will be deleted from tmp_path if set 'True'
        """

        # tmp_path = os.path.join(Settings.tmp_path, self.name)

        #======================================================================
        # if self.temp_res != 'dekadal':
        #     temp_path = os.path.join(Settings.tmp_path, self.name, 'temp')
        #     resample_temporal(temp_path,)
        #     tmp_path = temp_path
        #======================================================================

        raw_files = []
        tmp_path = os.path.join(Settings.tmp_path, self.name)

        for region in Settings.regions:

            print '[INFO] resampling to region ' + region

            dirList = os.listdir(tmp_path)
            dirList.sort()

            year = {'old': None, 'new': None}

            for item in dirList:
                src_file = os.path.join(tmp_path, item)
                image, lon, lat, gpis, timestamp = resample_to_shape(src_file,
                                                                     region,
                                                                     self.name)
                year['new'] = timestamp.year
                if year['old']  is None:
                    print '  ' + str(year['new']) + ' [',
                else:
                    if year['old'] != year['new']:
                        print ']'
                        print '  ' + str(year['new']) + ' [',
                year['old'] = year['new']

                print '.',

                path = Settings.data_path
                filename = region + '_' + str(Settings.sp_res) + '.nc'
                nc_name = os.path.join(path, filename)

                filepath = os.path.join(Settings.tmp_path, filename)

                write_tmp_file(image, lon, lat, timestamp, region, filepath)
                # save_image(image, lon, lat, timestamp, region, nc_name)
                raw_files.append(src_file)

            print ']'

        if delete_rawdata is True:
            print '[INFO] delete rawdata'
            for f in raw_files:
                os.unlink(f)

    def download(self):
        """"
        Virtual method, it has to be overriden by childs

        Raises
        ------
        NotImplementedError
            Raised if not overriden by childs
        """
        raise NotImplementedError()

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
        self.resample(delete_rawdata)

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
