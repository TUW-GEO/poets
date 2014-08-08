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
Description of module.
"""

import os
import datetime
import poets.io.sat as source


class Poet(object):
    """POETS base class

    Parameters
    ----------
    data_path : str
        path to the directory where data should be stored
    region : list of str, optional
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code),
        defaults to global
    spatial_resolution : float, optional
        spatial resolution in degree, defaults to 0.25
    temporal_resolution : str, optional
        temporal resolution of the data, possible values: day, week,
        month, dekad, defaults to dekad
    start_date : datetime.datetime, optional
        first date of the dataset, defaults to 2000-01-01
    nan_value : int
        NaN value to use, defaults to -99
    """

    def __init__(self, data_path, region='global',
                 spatial_resolution=0.25,
                 temporal_resolution='dekad',
                 start_date=datetime.datetime(2000, 1, 1),
                 nan_value=-99, shapefile=None):

        self.spatial_resolution = spatial_resolution
        self.temporal_resolution = temporal_resolution
        self.tmp_path = os.path.join(data_path, 'TMP')
        self.data_path = os.path.join(data_path, 'DATA')
        self.regions = region
        self.nan_value = nan_value
        self.start_date = start_date
        self.shapefile = shapefile

    def fetch_data(self):
        pass

if __name__ == "__main__":
    pass
