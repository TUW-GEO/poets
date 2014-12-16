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
# Creation date: 2014-07-18

"""
This module provides functions for converting lonlat-information
to pixels in an image file (eg. PNG, TIFF) and for calculating a
country bounding box.
"""

import numpy as np
import math
from osgeo import gdal
from PIL import Image
from poets.shape.shapes import Shape
from poets.image.geotiff import lonlat2px_gt, px2lonlat_gt


def get_layer_extent(filepath):
    """
    Returns extent of imagefile as minimum and maximum longitudes and 
    latitudes.

    Parameters:
    -----------
    filepath : str
        Path to image file.

    Returns:
    --------
    lon_min : float
        Minimum longitude.
    lat_min : float
        Minimum latitude.
    lon_max : float
        Maximum longitude.
    lat_max : float
        Maximum latitude.
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


def lonlat2px(img, lon, lat):
    """
    Converts a pair of lon and lat to its corresponding pixel value in an
    image file.

    Parameters
    ----------
    img : PIL image
        Input image file, e.g. PNG, TIFF.
    lon : float
        Longitude.
    lat : float
        Latitude.

    Returns
    -------
    Row : float
        Corresponding pixel value.
    Col : float
        Corresponding pixel value.
    """

    w, h = img.size

    mw = w / 360.0
    mh = h / 180.0

    row = h / 2 - lat * mh
    col = w / 2 + lon * mw

    return row, col


def lonlat2px_rearr(img, lon, lat):
    """
    Converts a pair of lon and lat to its corresponding pixel
    value in a rearranged image file (see rearrange_img).

    Parameters
    ----------
    img : PIL image
        Input image file, e.g. PNG, TIFF.
    lon : float
        Longitude
    lat : float
        Latitude

    Returns
    -------
    Row : float
        corresponding pixel value
    Col : float
        corresponding pixel value
    """

    w, h = img.size
    mw = w / 360.0
    mh = h / 180.0

    row = h / 2 - lat * mh

    if lon >= 0:
        col = 0 + lon * mw
    elif lon < 0:
        col = w + lon * mw

    return row, col


def px2lonlat(img, lon_px, lat_px):
    """
    Converts two arrays of row and column pixels into their corresponding lon 
    and lat arrays.

    Parameters
    ----------
    img : PIL image
        Input image file, e.g. PNG, TIFF.
    lon_px : np.array
        Array of column pixels.
    lat_px : np.array
        Array of row pixels.

    Returns
    -------
    lon_new : np.array
        List of corresponding longitude values.
    lat_new: np.array
        List of corresponding latitude values.
    """

    w, h = img.size

    mw = w / 360.0
    mh = h / 180.0

    lon_new = np.zeros(len(lon_px))
    lat_new = np.zeros(len(lat_px))

    for i in range(0, len(lon_px)):
        lon_new[i] = (lon_px[i] - w / 2) / mw

    for i in range(0, len(lat_px)):
        lat_new[i] = -(lat_px[i] - h / 2) / mh

    return lon_new, lat_new


def px2lonlat_rearr(img, lon_px, lat_px):
    """
    Converts two arrays of row and column pixels into their
    corresponding lon and lat arrays

    Parameters
    ----------
    img : PIL image
        Image which the pixel values refer to (rearranged image)
    lon_px : np.array
        Array of column pixels.
    lat_px : np.array
        Array of row pixels.

    Returns
    -------
    lon_new : np.array
        List of corresponding longitude values.
    lat_new: np.array
        List of corresponding latitude values.
    """

    w, h = img.size
    mw = w / 360.0
    mh = h / 180.0

    lon_new = np.zeros(len(lon_px))
    lat_new = np.zeros(len(lat_px))

    for i in range(0, len(lon_px)):  # lon [-180, 179.999]
        if lon_px[i] >= w / 2:  # west
            lon_new[i] = -(w - lon_px[i]) / mw
        elif lon_px[i] < w / 2:  # east
            lon_new[i] = lon_px[i] / mw

    for i in range(0, len(lat_px)):
        lat_new[i] = -(lat_px[i] - h / 2) / mh

    return lon_new, lat_new


def rearrange_img(img):
    """
    Rearranges image so that 0 degree Meridian is on the very left.
    Used when area around the +- 180 degree Meridian is of interest
    (eastern Russia, Alaska, New Zealand...).

    Parameters
    ----------
    img : PIL image
        Image to be rearranged.

    Returns
    -------
    img2 : Image file
        Rearranged image.
    """

    w, h = img.size
    blocklen = w / 2
    xblock = w / blocklen
    yblock = 1
    blockmap = [(xb * blocklen, yb * blocklen, (xb + 1) * blocklen,
                 (yb + 1) * blocklen) for xb in xrange(xblock)
                for yb in xrange(yblock)]
    rearr = blockmap[::-1]
    img2 = Image.new(img.mode, (w, h))
    for box, sbox in zip(blockmap, rearr):
        c = img.crop(sbox)
        img2.paste(c, box)

    return img2


def dateline_country(country):
    """
    Min and max longitude for countries that spread across the international 
    dateline.

    Returns
    -------
    lon_min : float
        Minimum longitude.
    lon_max : float
        Maximum longitude.
    """

    if country == 'NZ':
        lon_min = 165.0 + 52.0 / 60.0 + 12.0 / 3600.0
        lon_max = -(175.0 + 50.0 / 60.0)

    elif country == 'US':
        lon_min = 173.0 + 11.0 / 60.0
        lon_max = -(66.0 + 59.0 / 60.0 + 0.71006 / 3600.0)

    elif country == 'RS':
        lon_min = 19.0 + 38.0 / 60.0
        lon_max = -(169.0 + 3.0 / 60.0 + 54.0 / 3600.0)

    return lon_min, lon_max


def bbox_img(source_file, region, fileExtension, shapefile=None):
    """
    Clips bounding box out of image file and returns data as numpy.ndarray

    Parameters
    ----------
    source_file : str
        Path to source file.
    region : str
        Identifier of the region in the shapefile. If the default shapefile is
        used, this would be the FIPS country code.
    fileExtension : str
        Filetype (e.g. png, tif).
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.

    Returns
    -------
    data : dict of numpy.arrays
        Clipped image (grey values).
    lon_new : numpy.array
        Longitudes of the clipped image.
    lat_new : numpy.array
        Latitudes of the clipped image.
    timestamp : datetime.date
        Timestamp of the image.
    metadata : dict of strings
        Metadata from source netCDF file.
    """

    orig_img = Image.open(source_file)

    lon_min_src, lat_min_src, lon_max_src, lat_max_src = \
        get_layer_extent(source_file)

    if region == 'global':
        lon_min = -180
        lon_max = 180
        lat_min = -90
        lat_max = 90
    else:
        shp = Shape(region, shapefile)
        lon_min = shp.bbox[0]
        lon_max = shp.bbox[2]
        lat_min = shp.bbox[1]
        lat_max = shp.bbox[3]

    d = lon_max - lon_min

    # countries that cross the international dateline (maybe more!)
    if region in ['NZ', 'RS', 'US']:
        lon_min, lon_max = dateline_country(region)

    # get 2 pairs of points (upper left, lower right of bbox)
    if d > 350 and region not in ['AY', 'global']:
        if fileExtension in ['.tif', '.tiff', '.TIF', '.TIFF']:
            if (round(lon_max_src - lon_min_src) == 360.0 and
                round(lat_max_src - lat_min_src) == 180.0):
                orig_img = rearrange_img(orig_img)
                row_min, col_min = lonlat2px_rearr(orig_img, lon_min, lat_max)
                row_max, col_max = lonlat2px_rearr(orig_img, lon_max, lat_min)

                img = orig_img.crop((int(math.floor(col_min)),
                                     int(math.floor(row_min)),
                                     int(math.ceil(col_max)),
                                     int(math.ceil(row_max))))
            else:
                print 'Rearranging is only possible for global imagefiles.'
                return
        else:
            orig_img = rearrange_img(orig_img)
            row_min, col_min = lonlat2px_rearr(orig_img, lon_min, lat_max)
            row_max, col_max = lonlat2px_rearr(orig_img, lon_max, lat_min)

            img = orig_img.crop((int(math.floor(col_min)),
                                 int(math.floor(row_min)),
                                 int(math.ceil(col_max)),
                                 int(math.ceil(row_max))))

    elif fileExtension in ['.tif', '.tiff', '.TIF', '.TIFF']:
        row_min, col_min = lonlat2px_gt(orig_img, lon_min, lat_max,
                                        lon_min_src, lat_min_src, lon_max_src,
                                        lat_max_src)
        row_max, col_max = lonlat2px_gt(orig_img, lon_max, lat_min,
                                        lon_min_src, lat_min_src, lon_max_src,
                                        lat_max_src)

        # crop image
        img = orig_img.crop((int(math.floor(col_min)),
                             int(math.floor(row_min)),
                             int(math.ceil(col_max)),
                             int(math.ceil(row_max))))
    else:
        row_min, col_min = lonlat2px(orig_img, lon_min, lat_max)
        row_max, col_max = lonlat2px(orig_img, lon_max, lat_min)

        # crop image
        img = orig_img.crop((int(math.floor(col_min)),
                             int(math.floor(row_min)),
                             int(math.ceil(col_max)),
                             int(math.ceil(row_max))))

    # get data values from image
    data = {'dataset': np.array(img)}

    # lon_new, lat_new
    lon_px = np.arange(int(math.floor(col_min)), int(math.ceil(col_max)))
    lat_px = np.arange(int(math.floor(row_min)), int(math.ceil(row_max)))

    if region in ['NZ', 'RS', 'US']:
        lon_new, lat_new = px2lonlat_rearr(orig_img, lon_px, lat_px)
    elif fileExtension in ['.tif', '.tiff', '.TIF', '.TIFF']:
        lon_new, lat_new = px2lonlat_gt(orig_img, lon_px, lat_px, lon_min_src,
                                        lat_min_src, lon_max_src, lat_max_src)
    else:
        lon_new, lat_new = px2lonlat(orig_img, lon_px, lat_px)

    # timestamp
    timestamp = None

    # metadata
    metadata = None

    # move coordinates to pixel center
    if lon_new.size > 2:
        lon_new += (lon_new[1] - lon_new[0]) / 2
    if lat_new.size > 2:
        lat_new += (lat_new[1] - lat_new[0]) / 2

    return data, lon_new, lat_new, timestamp, metadata
