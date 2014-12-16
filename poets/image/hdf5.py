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
# Creation date: 2014-10-02

"""
This module provides functions for loading from HDF5 files.
"""

import h5py
import numpy as np


def read_image(source_file, variables=None):
    """Reads data out of hdf5 file and returns it as numpy.ndarray

    Parameters
    ----------
    source_file : str
        Path to source file.
    variables : list of str, optional
        Variables to read from file, reads all variables if not set.

    Returns
    -------
    data : dict of numpy.arrays
        Source file.
    lon : numpy.array
        Longitudes of the source file.
    lat : numpy.array
        Latitudes of the source file.
    timestamp : datetime.date
        Timestamp of image.
    metadata : dict of strings
        Metadata from source netCDF file.
    """

    with h5py.File(source_file, 'r') as h5:

        # extract time!!!
        timestamp = None

        data = {}
        metadata = {}
        meta_global = {}

        for attr in h5.attrs:
            if (isinstance(h5.attrs[attr], list) or
                isinstance(h5.attrs[attr], dict) or
                isinstance(h5.attrs[attr], tuple)):
                meta_global[str(attr).lower()] = h5.attrs[attr][0]
            else:
                meta_global[str(attr).lower()] = h5.attrs[attr]

        for grp in h5:
            for var in h5[grp].keys():
                if ((variables is not None and var in variables)
                    or variables is None):
                    metadata[str(var)] = {}
                    data[var] = h5[grp][var].value
                    for attr in meta_global:
                        metadata[var][attr] = meta_global[attr]
                    for attr in h5[grp][var].attrs:
                        if (isinstance(h5[grp][var].attrs[attr], list) or
                            isinstance(h5[grp][var].attrs[attr], dict) or
                            isinstance(h5[grp][var].attrs[attr], tuple)):
                            attr_value = h5[grp][var].attrs[attr][0]
                        else:
                            attr_value = h5[grp][var].attrs[attr]
                        metadata[var][str(attr)] = attr_value
                        if str(attr).lower() == 'scaling_factor':
                            metadata[var]['scale_factor'] = \
                                attr_value

        sp_res = 180. / data[data.keys()[0]].shape[0]

        lonmin = -180. + (sp_res / 2.)
        latmin = -90. + (sp_res / 2.)

        lon = np.arange(lonmin, 180, sp_res)
        lat = np.arange(latmin, 90, sp_res)

        lat = lat[::-1]

    return data, lon, lat, timestamp, metadata
