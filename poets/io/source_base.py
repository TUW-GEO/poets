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

"""
Base Class for data sources.
"""

import os
from poets.settings import Settings
from netCDF4 import Dataset, num2date
from poets.image.resampling import resample_to_shape
from poets.image.netcdf import save_image


class BasicSource(object):
    """
    Base Class for data sources.

    Parameters
    ----------
    source_path : string
        path to data source
    begin_date : datetime.date
        date, from which on data is available

    Attributes
    ----------
    """

    def __init__(self, name, source_path, filename, dirstruct, begin_date,
                 variables):
        """
        init method
        """

        self.name = name
        self.source_path = source_path
        self.begin_date = begin_date
        self.filename = filename
        self.dirstruct = dirstruct
        self.variables = variables

    def _check_current_date(self):

        dates = {}

        for region in Settings.regions:
            nc_name = os.path.join(Settings.data_path, region + '_'
                                  + str(Settings.sp_res) + '.nc')
            if os.path.exists(nc_name):
                dates[region] = {}
                for var in self.variables:
                    dates[region][var] = None
                    with Dataset(nc_name, 'r', format='NETCDF4') as ncfile:
                        for i in range(ncfile.variables['time'].size - 1, -1, -1):
                            if ncfile.variables[var][i].mask.min() == True:
                                continue
                            else:
                                times = ncfile.variables['time']
                                dat = num2date(ncfile.variables['time'][i],
                                               units=times.units,
                                               calendar=times.calendar)
                                dates[region][var] = dat
                                break
            else:
                dates = None
                break

        return dates

    def resample(self, delete_rawdata=False):

        for region in Settings.regions:

            tmp_path = os.path.join(Settings.tmp_path, self.name)

            dirList = os.listdir(tmp_path)

            for item in dirList:
                src_file = os.path.join(tmp_path, item)
                image, lon, lat, gpis, timestamp = resample_to_shape(src_file,
                                                                     region)
                save_image(image, lon, lat, timestamp, region)

                if delete_rawdata is True:
                    os.unlink(src_file)

if __name__ == "__main__":
    pass
