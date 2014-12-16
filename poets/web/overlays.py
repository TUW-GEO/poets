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

# Author: Maximilian Wonaschuetz
# Creation date: 2014-07-29

"""
This modules provides functions used while creating image overlays.
"""

from poets.shape.shapes import Shape


def bounds(country, shapefile=None):
    """
    Returns the bounding box, center coordinates and zoom level
    for web overlay purposes.

    Parameters
    ----------
    Country : str
        FIPS country code (https://en.wikipedia.org/wiki/FIPS_country_code)

    Returns
    -------
    lon_min : int
        Minimum longitude.
    lon_max : int
        Maximum longitude.
    lat_min : int
        Minimum latitude.
    lat_max : int
        Maximum latitude.
    c_lat : int
        Center latidute of image.
    c_lon : int
        Center longitude of image.
    zoom : int
        Zoom level for openlayers.
    """
    shp = Shape(country, shapefile)

    lon_min = shp.bbox[0]
    lon_max = shp.bbox[2]
    lat_min = shp.bbox[1]
    lat_max = shp.bbox[3]
    e_lon = lon_max - lon_min
    e_lat = lat_max - lat_min
    c_lon = lon_min + e_lon / 2
    c_lat = lat_min + e_lat / 2

    zoom = 0
    i = 1024  # To be replaced with the width of the map container!
    while i / 2 > e_lon:
        zoom += 1
        i = i / 2

    return lon_min, lon_max, lat_min, lat_max, c_lat, c_lon, zoom

if __name__ == "__main__":
    pass
