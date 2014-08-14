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
                                              "netcdf4 >= 1.0.1",
                                              "pytesmo >= 0.2.0",
                                              "Shapely >= 1.3.2",
                                              "pyshp >=1.2.1",
                                              "paramiko >= 1.14.0",
                                              "requests >= 1.14.0",
                                              "pillow >= 2.5.1"
                                              ],
                         'test_suite': 'poets/test/'
    }

setup(
    name='poets',
    version='0.1.0',
    author='poets Team',
    author_email='Thomas.Mistelbauer@geo.tuwien.ac.at',
    packages=['poets', 'poets.grid', 'poets.image', 'poets.io', 'poets.shape',
              'poets.timedate'],
    license='LICENSE.txt',
    description='python Open Earth Observation Tools',
    long_description=open('README.txt').read(),
    **setuptools_kwargs)



