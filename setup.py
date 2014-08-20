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
# Creation date: 2014-05-19

import os

try:
    from setuptools import setup
    have_setuptools = True
except ImportError:
    have_setuptools = False
    from distutils.core import setup


if not have_setuptools:
    setuptools_kwargs = {}
else:
    setuptools_kwargs = {'install_requires': ["numpy >= 1.7",
                                              "pandas >= 0.12",
                                              "scipy >= 0.12",
                                              "statsmodels >= 0.4.3",
                                              "netcdf4 >= 1.1.0",
                                              "pytesmo >= 0.2.0",
                                              "Shapely >= 1.3.2",
                                              "pyshp >=1.2.1",
                                              "paramiko >= 1.14.0",
                                              "requests >= 1.14.0",
                                              "pillow >= 2.5.1"
                                              ],
                         'test_suite': 'tests/'}

setup(
    name='poets',
    version='0.1.0',
    url='http://rs.geo.tuwien.ac.at/tools/poets',
    description='python Open Earth Observation Tools',
    long_description=open('README.rst').read(),

    author='poets Team',
    author_email='Thomas.Mistelbauer@geo.tuwien.ac.at',

    license='LICENSE.txt',

    packages=['poets', 'poets.grid', 'poets.image', 'poets.io', 'poets.shape',
              'poets.timedate'],
    package_data={'poets': [os.path.join('shape', 'ancillary', '*.dbf'),
                            os.path.join('shape', 'ancillary', '*.README'),
                            os.path.join('shape', 'ancillary', '*.shp'),
                            os.path.join('shape', 'ancillary', '*.shx')]
                  },
    **setuptools_kwargs)



