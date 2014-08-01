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
# Creation date: 2014-06-13

import os
import numpy as np
import pandas as pd
import pyresample as pr
import poets.grid.grids as gr
import poets.image.netcdf as nc
from poets.grid.shapes import Shape
from poets.settings import Settings
from pytesmo.grid import resample
from shapely.geometry import Point
from poets.image.imagefile import bbox_img


def _create_grid():
    """
    Generates regular grid based on spatial resolution set in constants.py

    Returns
    -------
    grid : grids.BasicGrid
        regular grid
    """

    if Settings.sp_res == 0.01:
        grid = gr.HundredthDegGrid(setup_kdTree=False)
    elif Settings.sp_res == 0.1:
        grid = gr.TenthDegGrid(setup_kdTree=False)
    elif Settings.sp_res == 0.25:
        grid = gr.TenthDegGrid(setup_kdTree=False)
    elif Settings.sp_res == 1:
        grid = gr.OneDegGrid(setup_kdTree=False)

    return grid


def resample_to_shape(source_file, country, prefix=None):
    """
    Resamples images and clips country boundaries

    Parameters
    ----------
    source_file : str
        path to source file
    country : str
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)

    Returns
    -------
    data : dict of numpy.arrays
        resampled image
    lons : numpy.array
        longitudes of the points in the resampled image
    lats : numpy.array
        latitudes of the points in the resampled image
    gpis : numpy.array
        grid point indices
    timestamp : datetime.date
        date of the image
    """

    if prefix is not None:
        prefix += '_'
    else:
        prefix = ''

    shp = Shape(country)

    _, fileExtension = os.path.splitext(source_file)

    if fileExtension in ['.nc', '.nc3', '.nc4']:
        data, src_lon, src_lat, timestamp, metadata = \
            nc.clip_bbox(source_file, shp.bbox[0], shp.bbox[1], shp.bbox[2],
                         shp.bbox[3], country=country)
<<<<<<< HEAD
    elif fileExtension in ['.png', '.PNG']:
        print  # clip bbox from png
    elif fileExtension in ['.tif', '.tiff']:
        print  # clip bbox from geotiff
=======
    elif fileExtension in ['.png', '.PNG', '.tif', '.tiff']:
        data, src_lon, src_lat, timestamp, metadata = bbox_img(source_file,
                                                            country)
>>>>>>> 426f45d284ea016924081bc68c9d396b597a8590

    src_lon, src_lat = np.meshgrid(src_lon, src_lat)
    grid = gr.CountryGrid(country)

    dest_lon, dest_lat = np.meshgrid(np.unique(grid.arrlon),
                                      np.unique(grid.arrlat)[::-1])

    gpis = grid.get_bbox_grid_points(grid.arrlat.min(), grid.arrlat.max(),
                                     grid.arrlon.min(), grid.arrlon.max())

    data = resample.resample_to_grid(data, src_lon, src_lat, dest_lon,
                                     dest_lat)

    mask = np.zeros(shape=grid.shape, dtype=np.bool)

    poly = shp.polygon

    for i in range(0, grid.shape[0]):
        for j in range(0, grid.shape[1]):
            p = Point(dest_lon[i][j], dest_lat[i][j])
            if p.within(poly) == False:
                    mask[i][j] = True
            if data[data.keys()[0]].mask[i][j] == True:
                mask[i][j] = True

    for key in data.keys():
        var = prefix + key
        metadata[prefix + key] = metadata[key]
        del metadata[key]
        data[var] = np.ma.masked_array(data[key], mask=mask,
                                       fill_value=Settings.nan_value)
        dat = np.copy(data[var].data)
        dat[data[var].mask == True] = Settings.nan_value
        data[var] = np.ma.masked_array(dat, mask=mask,
                                       fill_value=Settings.nan_value)
        # del data[key]

    return data, dest_lon, dest_lat, gpis, timestamp, metadata


def resample_to_gridpoints(source_file, country):
    """
    resamples image to the predefined grid

    Parameters
    ----------
    source_file : str
        path to source file
    country : str
        latitudes of source image

    Returns
    -------
    dframe : pandas.DataFrame
        resampled data with gridpoints as index
    """

    grid = _create_grid()

    gridpoints = gr.get_country_gridpoints(grid, country)
    shp = Shape(country)

    data, lon, lat = nc.clip_bbox(source_file, shp.bbox[0], shp.bbox[1],
                                  shp.bbox[2], shp.bbox[3])

    lon, lat = np.meshgrid(lon, lat)

    src_grid = pr.geometry.GridDefinition(lon, lat)
    des_swath = pr.geometry.SwathDefinition(gridpoints['lon'].values,
                                            gridpoints['lat'].values)

    dframe = pd.DataFrame(index=gridpoints.index)
    dframe['lon'] = gridpoints.lon
    dframe['lat'] = gridpoints.lat

    # resampling to country gridpoints
    for var in data.keys():
        dframe[var] = pr.kd_tree.resample_nearest(src_grid, data[var],
                                                  des_swath, 20000)

    return dframe


def resample_temporal(src_file, temp_res=Settings.temp_res):
    """
    Resamples image-cubes to a specific temporal resolution.

    Parameters
    ----------
    src_file : str
        path to source file
    temp_res : str, optional
        temporal resolution of output images

    Returns
    -------

    """
    print 'test'


def average_layers(image):
    """
    Averages image layers, given as ndimensional masked arrays to one image

    Parameters
    ----------
    image : numpy.ma.MaskedArray
        input image to average

    Returns
    -------
    avg_img : numpy.ma.MaskedArray
        averaged image
    """

    img = np.ma.masked_array(image.mean(0), fill_value=Settings.nan_value)
    mask = img.mask
    data = np.copy(img.data)
    data[img.mask == True] = Settings.nan_value
    avg_img = np.ma.masked_array(data, mask=mask,
                                 fill_value=Settings.nan_value)

    return avg_img
