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

# Author: Thomas Mistelbauer thomas.mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-11-04

"""
Module contains base class for user addons.
"""

import abc


class AddonBase(object):
    """
    Base class for poets add-ons that implements basic functions and also
    abstract methods that have to be implemented by child classes.

    Parameters
    ----------

    Attributes
    ----------
    """

    __metaclass__ = abc.ABCMeta

    def __init__(self):
        pass

    @abc.abstractmethod
    def _read_spec_img(self):
        pass

    @abc.abstractmethod
    def _read_spec_ts(self):
        pass

    def read_image(self):
        """Gets images from netCDF file for certain date

        Parameters
        ----------
        date : datetime
            Date of the image.
        source : str
            Data source from which image should be read.
        region : str, optional
            Region of interest, set to first defined region if None.
        variable : str, optional
            Variable to display, set to first variable of source if None.

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
        return self._read_spec_img()

    def read_timeseries(self, source, location, region=None, variable=None):
        """
        Gets timeseries from netCDF file for a gridpoint.

        Parameters
        ----------
        source : str
            Data source from which time series should be read.
        location : int or tuple of floats
            Either Grid point index as integer value or Longitude/Latitude
            given as tuple.
        region : str, optional
            Region of interest, set to first defined region if None.
        variable : str, optional
            Variable to display, set to first variable of source if None.

        Returns
        -------
        ts : pd.DataFrame
            Timeseries for the selected data.
        """

        return self._read_spec_ts()

if __name__ == "__main__":
    pass
