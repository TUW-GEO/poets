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

# Author: Isabella Pfeil, isy.pfeil@gmx.at
# Creation date: 2014-09-11

"""
GeoTIFF operations.
"""

from osgeo import gdal
from poets.shape.shapes import Shape
import numpy as np


def get_layer_extent(filepath):
    """
    as in: 'http://stackoverflow.com/questions/2922532/obtain-latitude-and-
            longitude-from-a-geotiff-file'

    Parameters:
    -----------
    filepath : str
        path to geotiff
        
    Returns:
    --------
    lon_min, lat_min : float
        lower left coordinate
    lon_max, lat_max : float
        upper right coordinate
    """
    ds = gdal.Open(filepath)
    gt = ds.GetGeoTransform()
    width = ds.RasterXSize
    height = ds.RasterYSize
    lon_min = gt[0]
    lat_min = gt[3] + width * gt[4] + height * gt[5]
    lon_max = gt[0] + width * gt[1] + height * gt[2]
    lat_max = gt[3]

    return lon_min, lat_min, lon_max, lat_max


def region_in_geotiff(lon_min, lat_min, lon_max, lat_max, region):
    """ Checks if geotiff covers country.
    
    Parameters:
    -----------
    lon_min, lat_min : float
        lower left coordinate of geotiff
    lon_max, lat_max : float
        upper right coordinate of geotiff
    region : str
        country FIPS code
    
    Returns:
    --------
    True, if region in geotiff
    """
    
    shp = Shape(region)
    region_ext = shp.bbox
    if (region_ext[0] >= lon_min and region_ext[1] >= lat_min and
        region_ext[2] <= lon_max and region_ext[3] <= lat_max):
        return True


def lonlat2px_gt(img, lon, lat, lon_min, lat_min, lon_max, lat_max):
    """
    Converts a pair of lon and lat to its corresponding pixel
    value in an image file.

    Parameters
    ----------
    img : Image File, e.g. PNG, TIFF
        Input image file
    lon : float
        Longitude
    lat : float
        Latitude
    lon_min, lat_min : float
        lower left coordinate of geotiff
    lon_max, lat_max : float
        upper right coordinate of geotiff

    Returns
    -------
    Row : float
        corresponding pixel value
    Col : float
        corresponding pixel value
    """

    w, h = img.size
    
    londiff = lon_max-lon_min
    latdiff = lat_max-lat_min
    
    mw = w / londiff
    mh = h / latdiff
    
    row = (-lat+lat_max) * mh
    col = (lon-lon_min) * mw

    return row, col


def px2lonlat_gt(img, lon_px, lat_px, lon_min, lat_min, lon_max, lat_max):
    """
    Converts two arrays of row and column pixels into their
    corresponding lon and lat arrays

    Parameters
    ----------
    img : Image file
        Image which the pixel values refer to
    lon_px : np.array
        array of column pixels
    lat_px : np.array
        array of row pixels

    Returns
    -------
    lon_new : np.array
        List of corresponding longitude values
    lat_new: np.array
        List of corresponding latitude values
    lon_min, lat_min : float
        lower left coordinate of geotiff
    lon_max, lat_max : float
        upper right coordinate of geotiff
    """
    
    w, h = img.size
    
    londiff = lon_max-lon_min
    latdiff = lat_max-lat_min
    
    mw = w / londiff
    mh = h / latdiff

    lon_new = np.zeros(len(lon_px))
    lat_new = np.zeros(len(lat_px))

    for i in range(0, len(lon_px)):
        lon_new[i] = lon_min + lon_px[i] / mw

    for i in range(0, len(lat_px)):
        lat_new[i] = lat_max - lat_px[i] / mh

    return lon_new, lat_new

if __name__ == "__main__":
    pass
