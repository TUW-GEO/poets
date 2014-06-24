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
Created on Jun 4, 2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import os
import shapefile


class FipsError(Exception):
    pass


class Country(object):
    """
    Class that provides geography information of a country

    Parameters
    ----------
    fips : string
        FIPS country code

    Attributes
    ----------
    fips : string
        FIPS country code
    shpfile : string
        Path to the source shapefile
    bbox : list
        Bounding box of the country
    polygon : list
        Country boundary polygon
    """

    def __init__(self, fips):
        self.fips = fips
        self.shpfile = os.path.join(os.path.dirname(__file__),
                                    'ancillary', 'boundaries',
                                    'world_country_admin_boundary_shapefile_'
                                    'with_fips_codes')
        rec, bbox, polygon = self._get_shape()
        self.name = rec[1]
        self.bbox = list(bbox)
        self.polygon = polygon

    def _get_shape(self):
        """
        Fetches shape and record information from shapefile

        Returns
        -------
        record : list
            Record of the country
        bbox : shapefile._Array
            Bounding box of the country
        polygon : list
            Country boundary polygon

        Raises
        ------
        FipsError
            if FIPS code does not exist
        """

        sf = shapefile.Reader(self.shpfile)
        pos = False
        for i, rec in enumerate(sf.records()):
            if rec[0] == self.fips:
                pos = i
                break

        if pos == False:
            raise FipsError("FIPS Code '" + self.fips + "' does not exist")

        sh = sf.shapeRecord(pos)

        return sh.record, sh.shape.bbox, sh.shape.points

if __name__ == '__main__':

    ctr = Country('ET')
