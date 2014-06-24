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
from shapely.geometry import Polygon, Point
from poets.grid.shapes import Country


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
    def __init__(self, lon, lat, **kwargs):
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
