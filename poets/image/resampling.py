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
import poets.image.netcdf as nc
import poets.image.hdf5 as h5
import matplotlib.path
from poets.image.imagefile import bbox_img
from poets.shape.shapes import Shape
from pytesmo.grid import resample
import scipy


imgfiletypes = ['.png', '.PNG', '.tif', '.tiff', '.TIF', '.TIFF', '.jpg',
                '.JPG', '.jpeg', '.JPEG', '.gif', '.GIF']


def resample_to_shape(source_file, region, sp_res, grid, prefix=None,
                      nan_value=None, dest_nan_value=None, variables=None,
                      shapefile=None):
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
    grid : poets.grid.RegularGrid or poets.grid.ShapeGrid
        Grid to resample data to.
    prefix : str, optional
        Prefix for the variable in the NetCDF file, should be name of source
    nan_value : int, float, optional
        Not a number value of the original data as given by the data provider
    dest_nan_value : int or float, optional
        NaN value used in the final NetCDF file.
    variables : list of str, optional
        Variables to resample from original file.
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.

    Returns
    -------
    res_data : dict of numpy.arrays
        resampled image
    dest_lon : numpy.array
        longitudes of the points in the resampled image
    dest_lat : numpy.array
        latitudes of the points in the resampled image
    gpis : numpy.array
        grid point indices
    timestamp : datetime.date
        date of the image
    metadata : dict
        Metadata derived from input file.
    """

    if prefix is not None:
        prefix += '_'

    fileExtension = os.path.splitext(source_file)[1].lower()

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

    if fileExtension in ['.nc', '.nc3', '.nc4']:
        data_src, lon, lat, timestamp, metadata = nc.read_image(source_file,
                                                                variables)
        data, src_lon, src_lat = nc.clip_bbox(data_src, lon, lat, lon_min,
                                              lat_min, lon_max, lat_max)
    elif fileExtension in ['.h5']:
        data_src, lon, lat, timestamp, metadata = h5.read_image(source_file,
                                                                variables)
        data, src_lon, src_lat = nc.clip_bbox(data_src, lon, lat, lon_min,
                                              lat_min, lon_max, lat_max)
    elif fileExtension in imgfiletypes:
        data, src_lon, src_lat, timestamp, metadata = bbox_img(source_file,
                                                               region,
                                                               fileExtension,
                                                               shapefile)

    if nan_value is not None:
        for key in data.keys():
            data[key] = np.ma.array(data[key], mask=(data[key] == nan_value))

    src_lon, src_lat = np.meshgrid(src_lon, src_lat)

    lons = grid.arrlon[0:grid.shape[1]]
    dest_lon, dest_lat = np.meshgrid(lons, np.unique(grid.arrlat)[::-1])

    gpis = grid.get_bbox_grid_points(grid.arrlat.min(), grid.arrlat.max(),
                                     grid.arrlon.min(), grid.arrlon.max())

    search_rad = 180000 * sp_res

    data = resample.resample_to_grid(data, src_lon, src_lat, dest_lon,
                                     dest_lat, search_rad=search_rad)

    res_data = {}
    path = []

    if region != 'global':
        _, _, multipoly = shp._get_shape()
        for ring in multipoly:
            poly_verts = list(ring.exterior.coords)
            path.append(matplotlib.path.Path(poly_verts))

        coords = [grid.arrlon, grid.arrlat[::-1]]
        coords2 = np.zeros((len(coords[0]), 2))

        for idx in range(0, len(coords[0])):
            coords2[idx] = [coords[0][idx], coords[1][idx]]

        mask_old = path[0].contains_points(coords2)

    for key in data.keys():
        if variables is not None:
            if key not in variables:
                del metadata[key]
                continue

        if region != 'global':
            for ring in path:
                mask_new = (ring.contains_points(coords2))
                mask_rev = scipy.logical_or(mask_old, mask_new)
                mask_old = mask_rev

            mask_rev = mask_rev.reshape(dest_lon.shape)
            mask = np.invert(mask_rev)

            mask[data[key].mask == True] = True
        else:
            mask = data[key].mask

        if prefix is None:
            var = key
        else:
            var = prefix + key

        if metadata is not None:
            metadata[var] = metadata[key]
            if var != key:
                del metadata[key]
        res_data[var] = np.ma.masked_array(data[key], mask=np.copy(mask),
                                           fill_value=dest_nan_value)

        dat = np.copy(res_data[var].data)
        dat[mask == True] = dest_nan_value

        res_data[var] = np.ma.masked_array(dat, mask=np.copy(mask),
                                           fill_value=dest_nan_value)

    return res_data, dest_lon, dest_lat, gpis, timestamp, metadata


def average_layers(image, dest_nan_value):
    """
    Averages image layers, given as n-dimensional masked arrays to one image.

    Parameters
    ----------
    image : numpy.ma.MaskedArray
        Input image to average.
    dest_nan_value : int
        NaN value to be used.

    Returns
    -------
    avg_img : numpy.ma.MaskedArray
        Averaged image.
    """

    img = np.ma.masked_array(np.nanmean(image, axis=0),
                             fill_value=dest_nan_value)
    mask = img.mask
    data = np.copy(img.data)
    data[img.mask == True] = dest_nan_value
    avg_img = np.ma.masked_array(data, mask=mask,
                                 fill_value=dest_nan_value)

    return avg_img
