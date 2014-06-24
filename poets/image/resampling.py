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

'''
Created on May 27, 2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import numpy as np
import pandas as pd
import pyresample as pr
import poets.grid.grids as gr
from poets.grid.shapes import Country
from netCDF4 import Dataset
from poets.constants import Settings as settings
from pytesmo.grid import resample
from shapely.geometry import Polygon, Point


def _create_grid():
    """
    Generates regular grid based on spatial resolution set in constants.py

    Returns
    -------
    grid : grids.BasicGrid
        regular grid
    """

    if settings.sp_res == 0.1:
        grid = gr.TenthDegGrid(setup_kdTree=False)
    elif settings.sp_res == 0.25:
        grid = gr.TenthDegGrid(setup_kdTree=False)
    elif settings.sp_res == 1:
        grid = gr.OneDegGrid(setup_kdTree=False)

    return grid


def resample_to_shape(source_file, country):
    """
    Resamples images and clips country boundaries

    Parameters
    ----------
    source_file : string
        path to source file
    country : string
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)

    Returns
    -------
    data : dict of numpy.arrays
        resampled image
    lons : numpy.array
        longitudes of the points in the resampled image
    lats : numpy.array
        latgitudes of the points in the resampled image
    """

    shp = Country(country)

    data, lon, lat = clip_netcdf_bbox(source_file, shp.bbox[0], shp.bbox[1],
                                     shp.bbox[2], shp.bbox[3], country=country)

    grid = _create_grid()
    pts = gr.getCountryPoints(grid, country)

    londim = np.arange(pts.lon.min(), pts.lon.max(), settings.sp_res)
    latdim = np.arange(pts.lat.max(), pts.lat.min(), -settings.sp_res)

    gpis = grid.get_bbox_grid_points(latdim.min(), latdim.max(), londim.min(),
                                     londim.max())

    lon, lat = np.meshgrid(lon, lat)
    lons, lats = np.meshgrid(londim, latdim)

    data = resample.resample_to_grid(data, lon, lat, lons, lats)

    mask = np.zeros(shape=lons.shape, dtype=np.bool)

    poly = Polygon(shp.polygon)

    for i in range(0, lons.shape[0]):
        for j in range(0, lons.shape[1]):
            p = Point(lons[i][j], lats[i][j])
            if p.within(poly) == False:
                mask[i][j] = True
            if data[data.keys()[0]].mask[i][j] == True:
                mask[i][j] = True

    for key in data.keys():
        data[key] = np.ma.masked_array(data[key], mask=mask)

    return data, lons, lats, gpis


def resample_to_gridpoints(source_file, country):
    """
    resamples image to the predefined grid

    Parameters
    ----------
    source_file : string
        path to source file
    country : numpy.ndarray
        latitudes of source image

    Returns
    -------
    dframe : pandas.DataFrame
        resampled data with gridpoints as index
    """

    grid = _create_grid()

    gridpoints = gr.getCountryPoints(grid, country)
    shp = Country(country)

    data, lon, lat = clip_netcdf_bbox(source_file, shp.bbox[0], shp.bbox[1],
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


def clip_netcdf_bbox(source_file, lon_min, lat_min, lon_max, lat_max,
                     country=None):
    """
    Clips bounding box out of an image

    Parameters
    ----------
    source_file : string
        path to source file
    lon_min : float
        min longitude of bounding box
    lat_min : float
        min latitude of bounding box
    lon_max : float
        max longitude of bounding box
    lat_max : float
        max latitude of bounding box

    Returns
    -------
    data : dict of numpy.arrays
        clipped image
    lon_new : numpy.array
        longitudes of the clipped image
    lat_new : numpy.array
        latgitudes of the clipped image
    """

    nc = Dataset(source_file)

    lon = np.copy(nc.variables['lon'])
    lat = np.copy(nc.variables['lat'])

    variables = nc.variables.keys()[3:]

    lons = np.where((lon >= lon_min) & (lon <= lon_max))[0]
    lats = np.where((lat >= lat_min) & (lat <= lat_max))[0]

    lon_new = lon[lons.min():lons.max()]
    lat_new = lat[lats.min():lats.max()]

    data = {}

    for var in variables:
        dat = nc.variables[var][:][0]
        data[var] = dat[lats.min():lats.max(), lons.min():lons.max()]

    nc.close()

    return data, lon_new, lat_new

