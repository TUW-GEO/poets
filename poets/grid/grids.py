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
Defines the grids using pytesmo.grid.grids

Created on Jun 3, 2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import pytesmo.grid.grids as grids
import numpy as np
import pandas as pd
import math
from shapely.geometry import Polygon, Point
from poets.grid.shapes import Country
from poets.settings import Settings


class HundredthDegGrid(grids.BasicGrid):
    """
    Regular 0.1 degree grid with grid middle points at
    (-179.95,-89.95), (-179.85,-89.95) etc.
    """
    def __init__(self, **kwargs):

        londim = np.arange(-179.995, 180, 0.01)
        latdim = np.arange(-89.995, 90, 0.01)
        lon, lat = np.meshgrid(londim, latdim)
        super(HundredthDegGrid, self).__init__(lon.flatten(), lat.flatten(),
                                         shape=lon.shape, **kwargs)


class TenthDegGrid(grids.BasicGrid):
    """
    Regular 0.1 degree grid with grid middle points at
    (-179.95,-89.95), (-179.85,-89.95) etc.
    """
    def __init__(self, **kwargs):

        londim = np.arange(-179.95, 180, 0.1)
        latdim = np.arange(-89.95, 90, 0.1)
        lon, lat = np.meshgrid(londim, latdim)
        super(TenthDegGrid, self).__init__(lon.flatten(), lat.flatten(),
                                         shape=lon.shape, **kwargs)


class QuarterDegGrid(grids.BasicGrid):
    """
    Regular 0.25 degree grid with grid middle points at
    (-179.875,-89.875), (-179.875,-89.875) etc.
    """
    def __init__(self, **kwargs):

        londim = np.arange(-179.875, 180, 0.25)
        latdim = np.arange(-89.875, 90, 0.25)
        lon, lat = np.meshgrid(londim, latdim)
        super(QuarterDegGrid, self).__init__(lon.flatten(), lat.flatten(),
                                             shape=lon.shape, **kwargs)


class OneDegGrid(grids.BasicGrid):
    """
    Regular 0.1 degree grid with grid middle points at
    (-179.5,-89.5), (-179.5,-89.5) etc.
    """
    def __init__(self, **kwargs):

        londim = np.arange(-179.5, 180, 1)
        latdim = np.arange(-89.5, 90, 1)
        lon, lat = np.meshgrid(londim, latdim)
        super(OneDegGrid, self).__init__(lon.flatten(), lat.flatten(),
                                         shape=lon.shape, **kwargs)


class CountryGrid(grids.BasicGrid):
    """
    Regular grid for spedific country
    """
    def __init__(self, country, **kwargs):

        shp = Country(country)

        lonmin, lonmax = _minmaxcoord(shp.bbox[0], shp.bbox[2])
        latmin, latmax = _minmaxcoord(shp.bbox[1], shp.bbox[3])

        lons = np.arange(lonmin, lonmax + Settings.sp_res, Settings.sp_res)
        lats = np.arange(latmin, latmax + Settings.sp_res, Settings.sp_res)

        poly = Polygon(shp.polygon)

        del_lons = []
        del_lats = []

        # left boundary check
        for i, x in enumerate(lons[:(lons.size / 2)]):
            checksum = 0
            for y in lats:
                p = Point(x, y)
                if p.within(poly) == False:
                    checksum += 1
            if checksum == lats.size:
                del_lons.append(i)
            else:
                break

        # right boundary check
        for i, x in enumerate(lons[::-1][:(lons.size / 2)]):
            checksum = 0
            for y in lats:
                p = Point(x, y)
                if p.within(poly) == False:
                    checksum += 1
            if checksum == lats.size:
                del_lons.append(lons.size - 1 - i)
            else:
                break

        # bottom boundary check
        for i, y in enumerate(lats[:(lats.size / 2)]):
            checksum = 0
            for x in lons:
                p = Point(x, y)
                if p.within(poly) == False:
                    checksum += 1
            if checksum == lons.size:
                del_lats.append(i)
            else:
                break

        # top boundary check
        for i, y in enumerate(lats[::-1][:(lats.size / 2)]):
            checksum = 0
            for x in lons:
                p = Point(x, y)
                if p.within(poly) == False:
                    checksum += 1
            if checksum == lons.size:
                del_lats.append(lats.size - 1 - i)
            else:
                break

        lon_new = lons.tolist()
        lat_new = lats.tolist()

        for i in del_lons:
            if lons[i] in lon_new:
                lon_new.remove(lons[i])

        for i in del_lats:
            if lats[i] in lat_new:
                lat_new.remove(lats[i])

        lon, lat = np.meshgrid(lon_new, lat_new)

        super(CountryGrid, self).__init__(lon.flatten(), lat.flatten(),
                                          shape=lon.shape, **kwargs)


def getCountryPoints(grid, country):

    shp = Country(country)
    box = grid.get_bbox_grid_points(shp.bbox[1], shp.bbox[3], shp.bbox[0],
                                    shp.bbox[2])
    poly = Polygon(shp.polygon)

    lons = []
    lats = []
    pts = []

    for gpi in box:
        lon, lat = grid.gpi2lonlat(gpi)
        if poly.contains(Point(lon, lat)):
            pts.append(gpi)
            lons.append(lon)
            lats.append(lat)

    points = pd.DataFrame({'lon': lons, 'lat': lats}, pts)

    return points


def _minmaxcoord(min_threshold, max_threshold):

    res = float(Settings.sp_res)

    minval = int(math.ceil(min_threshold / res)) * res
    maxval = int(math.floor(max_threshold / res)) * res

    if minval - (res / 2) < min_threshold:
        minval += res / 2
    else:
        minval -= res / 2

    if maxval + (res / 2) > max_threshold:
        maxval -= res / 2
    else:
        maxval += res / 2

    return minval, maxval
