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
Created on May 19, 2014

@author: Thomas Mistelbauer, Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import poets

try:
    from setuptools import setup
    have_setuptools = True
except ImportError:
    have_setuptools = False
    from distutils.core import setup


if not have_setuptools:
    setuptools_kwargs = {}
else:
    setuptools_kwargs = {'install_requires':[ "numpy >= 1.7",
                                            "pandas >= 0.12",
                                            "scipy >= 0.12",
                                            "statsmodels >= 0.4.3",
                                            "netcdf4 >= 1.0.1",
                                            "GDAL >= 1.11.0"  # ?????
                                           ]
                       }

setup(
    name='poets',
    version=poets.__version__
    author='poets Team',
    author_email='Thomas.Mistelbauer@geo.tuwien.ac.at',
    packages=['poets'],
    scripts=[''],
    url='',
    license='LICENSE.txt',
    description='python Open Earth Observation Tools',
    long_description=open('README.txt').read(),
    **setuptools_kwargs)
