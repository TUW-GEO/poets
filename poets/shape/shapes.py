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
# Creation date: 2014-06-04

import os
import shapefile
from shapely.geometry import MultiPolygon


class FipsError(Exception):
    pass


class Shape(object):
    """Provides geography information of a region/country given as shapefile.

    Parameters
    ----------
    code : str
        Identifier of the records in the shapefile; uses the first argument
        returned by shapefile.Reader as identifier, for the default shapefile,
        this would be the FIPS country code.
    shapefile : str, optional
        Path to shape file, uses "world country admin boundary shapefile" by
        default.

    Attributes
    ----------
    code : str
        Identifier of the selected record in the shapefile; uses the first
        argument returned by shapefile.Reader as identifier, for the default
        shapefile, this would be the FIPS country code.
    name : str
        Name of the selected record in the shapefile; uses the second argument
        returned by shapefile.Reader as identifier, for the default shapefile,
        this would be the FIPS country code.
    shpfile : str
        Path to the source shapefile.
    bbox : tuple
        Bounding box of the country.
    polygon : list of tuples
        Country boundary polygon.
    """

    def __init__(self, code, shapefile=None):
        self.code = code
        if shapefile is None:
            self.shpfile = os.path.join(os.path.dirname(__file__),
                                        'ancillary',
                                        'world_country_admin_boundary_'
                                        'shapefile_with_fips_codes')
        else:
            self.shpfile = shapefile
        rec, bbox, polygon = self._get_shape()
        self.name = rec[1]
        self.bbox = tuple(bbox)
        self.polygon = polygon

    def _get_shape(self):
        """Fetches shape and record information from shapefile.

        Returns
        -------
        record : list
            Record of the country.
        bbox : shapefile._Array
            Bounding box of the country.
        multipoly : shapely.geometry.MultiPolygon
            Country boundary polygon.

        Raises
        ------
        FipsError
            If FIPS code does not exist.
        """

        sf = shapefile.Reader(self.shpfile)
        pos = False
        for i, rec in enumerate(sf.records()):
            if self.code == str(rec[0]):
                pos = i
                break

        if not pos:
            raise FipsError("FIPS Code '" + self.code + "' does not exist")

        sh = sf.shapeRecord(pos)

        if len(sh.shape.parts) == 1:
            multipoly = [[sh.shape.points, []]]

        else:
            points = []
            for i in range(0, len(sh.shape.parts) - 1):
                points.append(sh.shape.points[sh.shape.parts[i]:
                                              sh.shape.parts[i + 1]])
            points.append(sh.shape.points[sh.shape.parts[-1]:])
            multipoly = []
            for i in range(0, len(points)):
                    multipoly.append([points[i], []])

        multipoly = MultiPolygon(multipoly)

        return sh.record, sh.shape.bbox, multipoly

if __name__ == '__main__':
    pass
