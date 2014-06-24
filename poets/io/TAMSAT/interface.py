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

'''
Created on 23.05.2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import os
import glob
import numpy as np
import netCDF4 as nc

import RS.dataspecific.dataset_base as dataset_base
import general.root_path as root

filename = 'rfe{YYYY}_{MM}-dk{P}.nc'


class RFE10Img(dataset_base.DatasetImgBase):
    """
    Class for the dekadal TAMSAT rainfall estimates produkt
    """
    def __init__(self):
        path = os.path.join(root.r, 'Datapool_raw', 'TAMSAT', 'datasets',
                            'TAMSAT_rfe_dekadal')
        super(RFE10Img, self).__init__(path, grid=None)

    def _read_spec_img(self, timestamp):
        """
        Read specific image for given datetime date.

        Parameters
        ----------
        timestamp : datetime.date
            exact observation timestamp of the image that should be read

        Returns
        -------
        data : dict
            dictionary of numpy arrays that hold the image data for each
            variable of the dataset
        metadata : dict
            dictionary of numpy arrays that hold the metadata
        timestamp : datetime.datetime
            exact timestamp of the image
        lon : numpy.array or None
            array of longitudes, if None self.grid will be assumed
        lat : numpy.array or None
            array of latitudes, if None self.grid will be assumed
        time_var : string or None
            variable name of observation times in the data dict, if None all
            observations have the same timestamp
        """

        if timestamp.day >= 1 and timestamp.day < 11:
            dekad = 1
        elif timestamp.day >= 11 and timestamp.day < 21:
            dekad = 2
        else:
            dekad = 3

        filen = (filename.replace('{YYYY}', '%Y').replace('{MM}', '%m')
                 .replace('{P}', str(dekad)))

        month = str("%02d" % (timestamp.month,))

        files = glob.glob(os.path.join(self.path, str(timestamp.year), month,
                                       timestamp.strftime(filen)))
        if len(files) != 1:
            raise ValueError("There must be exactly one file for given "
                             "timestamp %s" % timestamp.isoformat())

        dataset = nc.Dataset(files[0], 'r', format='NETCDF4')

        rfe = dataset.variables['rfe'][:]

        lons = dataset.variables['lon']
        lats = dataset.variables['lat']

        lons, lats = np.meshgrid(lons, lats)

        data = {'rfe': rfe}

        return data, {}, timestamp, lons, lats, None
