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

# Author: Isabella Pfeil, isy.pfeil@gmx.at
# Creation date: 2014-07-18

"""
This module provides functions for converting lonlat-information
to pixels in an image file (eg. PNG, TIFF) and for calculating a
country bounding box.
"""

import numpy as np
from PIL import Image
from poets.grid.shapes import Shape
import math
import matplotlib.pyplot as plt
from matplotlib.path import Path
import matplotlib.patches as patches


def lonlat2px(img, lon, lat):
    """
    Converts a pair of lon and lat to its corresponding pixel
    value in an image file.

    Parameters:
    ----------
    img : Image File, e.g. PNG, TIFF
        Input image file
    lon : float
        Longitude
    lat : float
        Latitude

    Returns:
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
    col = w / 2 + lon * mw

    return row, col


def lonlat2px_rearr(img, lon, lat):
    """
    Converts a pair of lon and lat to its corresponding pixel
    value in a rearranged image file (see rearrange_img).

    Parameters:
    ----------
    img : Image File, e.g. PNG, TIFF
        Input image file
    lon : float
        Longitude
    lat : float
        Latitude

    Returns:
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
    Converts two arrays of row and column pixels into their
    corresponding lon and lat arrays

    Parameters:
    -----------
    img : Image file
        Image which the pixel values refer to
    lon_px : np.array
        array of column pixels
    lat_px : np.array
        array of row pixels

    Returns:
    --------
    lon_new : np.array
        List of corresponding longitude values
    lat_new: np.array
        List of corresponding latitude values
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

    Parameters:
    -----------
    img : Image file
        Image which the pixel values refer to (rearranged image)
    lon_px : np.array
        array of column pixels
    lat_px : np.array
        array of row pixels

    Returns:
    --------
    lon_new : np.array
        List of corresponding longitude values
    lat_new: np.array
        List of corresponding latitude values
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

    Parameters:
    -----------
    img : Image File, e.g. PNG, TIFF
        Image to be rearranged

    Returns:
    --------
    img : Image file
        Rearranged image
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


def plot_polygon(country):
    """Plots the shapefile of a country border

    Parameters:
    ----------
    country : FIPS-code
    """

    shp = Shape(country)
    polygon = shp.polygon
    polygon.append(polygon[0])

    codes = [Path.MOVETO]
    i = 1

    while i < (len(polygon) - 1):
        codes.append(Path.LINETO)
        i += 1

    codes.append(Path.CLOSEPOLY)

    path = Path(polygon, codes)

    fig = plt.figure()
    ax = fig.add_subplot(111)
    patch = patches.PathPatch(path, facecolor='orange')
    ax.add_patch(patch)
    ax.relim()
    ax.autoscale_view(True, True, True)
    plt.show()


def dateline_country(country):
    """
    Min and max longitude for countries that spread across the
    international dateline

    Returns:
    -------
    lon_min, lon_max : float
        min and max longitude
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


def bbox_img(source_file, country):
    """
    Clips bounding box out of image file and returns data as numpy.ndarray

    Parameters
    ----------
    source_file : str
        path to source file
    Country : str
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)

    Returns
    -------
    data : dict of numpy.arrays
        clipped image (grey values)
    lon_new : numpy.array
        longitudes of the clipped image
    lat_new : numpy.array
        latitudes of the clipped image
    timestamp : datetime.date
        timestamp of image
    metadata : dict of strings
        metadata from source netCDF file
    """

    orig_img = Image.open(source_file)

    shp = Shape(country)
    lon_min = shp.bbox[0]
    lon_max = shp.bbox[2]
    lat_min = shp.bbox[1]
    lat_max = shp.bbox[3]

    d = lon_max - lon_min

    # countries that cross the international dateline (maybe more!)
    if country in ['NZ', 'RS', 'US']:
        lon_min, lon_max = dateline_country(country)

    # get 2 pairs of points (upper left, lower right of bbox)
    if d > 350 and country != 'AY':
        orig_img = rearrange_img(orig_img)
        row_min, col_min = lonlat2px_rearr(orig_img, lon_min, lat_max)
        row_max, col_max = lonlat2px_rearr(orig_img, lon_max, lat_min)

        img = orig_img.crop((int(math.floor(col_min)), int(math.floor(row_min)),
                        int(math.ceil(col_max)), int(math.ceil(row_max))))
    else:
        row_min, col_min = lonlat2px(orig_img, lon_min, lat_max)
        row_max, col_max = lonlat2px(orig_img, lon_max, lat_min)

        # crop image
        img = orig_img.crop((int(math.floor(col_min)), int(math.floor(row_min)),
                        int(math.ceil(col_max)), int(math.ceil(row_max))))

    # get data values from image
    data = {'dataset': np.array(img)}

    # lon_new, lat_new
    lon_px = np.arange(int(math.floor(col_min)), int(math.ceil(col_max)))
    lat_px = np.arange(int(math.floor(row_min)), int(math.ceil(row_max)))

    if country in ['NZ', 'RS', 'US']:
        lon_new, lat_new = px2lonlat_rearr(orig_img, lon_px, lat_px)
    else:
        lon_new, lat_new = px2lonlat(orig_img, lon_px, lat_px)

    # timestamp
    timestamp = np.NAN

    # metadata
    metadata = {'dataset': np.NAN}

    return data, lon_new, lat_new, timestamp, metadata

if __name__ == "__main__":
    pass