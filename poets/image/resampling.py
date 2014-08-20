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
# Creation date: 2014-06-13

import os
import numpy as np
import pandas as pd
import pyresample as pr
import poets.grid.grids as gr
import poets.image.netcdf as nc
from poets.shape.shapes import Shape
from poets.grid.grids import ShapeGrid, RegularGrid
from pytesmo.grid import resample
from shapely.geometry import Point
from poets.image.imagefile import bbox_img

imgfiletypes = ['.png', '.PNG', '.tif', '.tiff', '.TIF', '.TIFF', '.jpg',
                '.JPG', '.jpeg', '.JPEG', '.gif', '.GIF']


def resample_to_shape(source_file, region, sp_res, prefix=None,
                      nan_value=None, dest_nan_value=None, shapefile=None):
    """
    Resamples images and clips country boundaries

    Parameters
    ----------
    source_file : str
        Path to source file.
    region : str
        Identifier of the region in the shapefile. If the default shapefile is
        used, this would be the FIPS country code.
    sp_res : int or float
        Spatial resolution of the shape-grid.
    prefix : str, optional
        Prefix for the variable in the NetCDF file, should be name of source
    nan_value : int, float, optional
        Not a number value of the original data as given by the data provider
    dest_nan_value : int or float, optional
        NaN value used in the final NetCDF file
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.

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

    _, fileExtension = os.path.splitext(source_file)

    if region == 'global':
        lon_min = -180
        lon_max = 180
        lat_min = -90
        lat_max = 90
        grid = gr.RegularGrid(sp_res=sp_res)
    else:
        shp = Shape(region, shapefile)
        lon_min = shp.bbox[0]
        lon_max = shp.bbox[2]
        lat_min = shp.bbox[1]
        lat_max = shp.bbox[3]
        grid = gr.ShapeGrid(region, sp_res, shapefile)

    if fileExtension in ['.nc', '.nc3', '.nc4']:
        data, src_lon, src_lat, timestamp, metadata = \
            nc.clip_bbox(source_file, lon_min, lat_min, lon_max, lat_max)

    elif fileExtension in imgfiletypes:
        data, src_lon, src_lat, timestamp, metadata = bbox_img(source_file,
                                                               region)

    if nan_value is not None:
        for key in data.keys():
            data[key] = np.ma.array(data[key], mask=(data[key] == 255))

    src_lon, src_lat = np.meshgrid(src_lon, src_lat)

    lons = grid.arrlon[0:grid.shape[1]]
    dest_lon, dest_lat = np.meshgrid(lons, np.unique(grid.arrlat)[::-1])

    gpis = grid.get_bbox_grid_points(grid.arrlat.min(), grid.arrlat.max(),
                                     grid.arrlon.min(), grid.arrlon.max())

    search_rad = 180000 * sp_res

    data = resample.resample_to_grid(data, src_lon, src_lat, dest_lon,
                                     dest_lat, search_rad=search_rad)

    mask = np.zeros(shape=grid.shape, dtype=np.bool)

    if region != 'global':
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

        if region == 'global':
            mask = data[key].mask

        if metadata is not None:
            metadata[var] = metadata[key]
            if var != key:
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


def resample_to_gridpoints(source_file, region, sp_res, shapefile=None):
    """Resamples image to predefined gridpoints.

    Parameters
    ----------
    source_file : str
        Path to source file.
    region : str
        Latitudes of source image.
    sp_res : int or float
        Spatial resolution of the shape-grid.
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.

    Returns
    -------
    dframe : pandas.DataFrame
        Resampled data with gridpoints as index.
    """

    shp = Shape(region, shapefile)
    lon_min = shp.bbox[0]
    lon_max = shp.bbox[2]
    lat_min = shp.bbox[1]
    lat_max = shp.bbox[3]
    grid = ShapeGrid(region, sp_res, shapefile)
    gridpoints = grid.get_gridpoints()

    data, lon, lat, _, _ = nc.clip_bbox(source_file, lon_min, lat_min, lon_max,
                                        lat_max)

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
        Input image to average.

    Returns
    -------
    avg_img : numpy.ma.MaskedArray
        Averaged image.
    """

    img = np.ma.masked_array(image.mean(0), fill_value=dest_nan_value)
    mask = img.mask
    data = np.copy(img.data)
    data[img.mask == True] = dest_nan_value
    avg_img = np.ma.masked_array(data, mask=mask,
                                 fill_value=dest_nan_value)

    return avg_img
