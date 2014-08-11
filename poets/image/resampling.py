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
from poets.shape.shapes import Shape
from poets.grid.grids import CountryGrid
from pytesmo.grid import resample
from shapely.geometry import Point
from poets.image.imagefile import bbox_img


def _create_grid(sp_res):
    """
    Generates regular grid based on spatial resolution set in constants.py

    Returns
    -------
    grid : grids.BasicGrid
        regular grid
    """

    if sp_res == 0.01:
        grid = gr.HundredthDegGrid(setup_kdTree=False)
    elif sp_res == 0.1:
        grid = gr.TenthDegGrid(setup_kdTree=False)
    elif sp_res == 0.25:
        grid = gr.TenthDegGrid(setup_kdTree=False)
    elif sp_res == 1:
        grid = gr.OneDegGrid(setup_kdTree=False)

    return grid


def resample_to_shape(source_file, country, sp_res, prefix=None,
                      nan_value=None, dest_nan_value=None):
    """
    Resamples images and clips country boundaries

    Parameters
    ----------
    source_file : str
        path to source file
    country : str
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)
    prefix : str, optional
        Prefix for the variable in the NetCDF file, should be name of source
    nan_value : int, float, optional
        Not a number value of the original data as given by the data provider

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

    shp = Shape(country)

    _, fileExtension = os.path.splitext(source_file)

    if fileExtension in ['.nc', '.nc3', '.nc4']:
        data, src_lon, src_lat, timestamp, metadata = \
            nc.clip_bbox(source_file, shp.bbox[0], shp.bbox[1], shp.bbox[2],
                         shp.bbox[3], country=country)

    elif fileExtension in ['.png', '.PNG', '.tif', '.tiff']:
        data, src_lon, src_lat, timestamp, metadata = bbox_img(source_file,
                                                               country)

    if nan_value is not None:
        for key in data.keys():
            data[key] = np.ma.array(data[key], mask=(data[key] == 255))

    src_lon, src_lat = np.meshgrid(src_lon, src_lat)
    grid = gr.CountryGrid(country)

    lons = grid.arrlon[0:grid.shape[1]]
    dest_lon, dest_lat = np.meshgrid(lons, np.unique(grid.arrlat)[::-1])

    gpis = grid.get_bbox_grid_points(grid.arrlat.min(), grid.arrlat.max(),
                                     grid.arrlon.min(), grid.arrlon.max())

    data = resample.resample_to_grid(data, src_lon, src_lat, dest_lon,
                                     dest_lat)

    mask = np.zeros(shape=grid.shape, dtype=np.bool)

    poly = shp.polygon

    for i in range(0, grid.shape[0]):
        for j in range(0, grid.shape[1]):
            p = Point(dest_lon[i][j], dest_lat[i][j])
            if not p.within(poly):
                mask[i][j] = True
            if data[data.keys()[0]].mask[i][j]:
                mask[i][j] = True

    for key in data.keys():
        if prefix is None:
            var = key
        else:
            var = prefix + key
        if metadata is not None:
            metadata[var] = metadata[key]
            del metadata[key]
        data[var] = np.ma.masked_array(data[key], mask=mask,
                                       fill_value=dest_nan_value)
        dat = np.copy(data[var].data)
        dat[mask == True] = dest_nan_value
        data[var] = np.ma.masked_array(dat, mask=mask,
                                       fill_value=dest_nan_value)
        if prefix is not None:
            del data[key]

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

    grid = CountryGrid(country)

    gridpoints = grid.get_country_gridpoints()
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


def average_layers(image, dest_nan_value):
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

    img = np.ma.masked_array(image.mean(0), fill_value=dest_nan_value)
    mask = img.mask
    data = np.copy(img.data)
    data[img.mask == True] = dest_nan_value
    avg_img = np.ma.masked_array(data, mask=mask,
                                 fill_value=dest_nan_value)

    return avg_img
