==============================================================
Introduction to poets, the Python Open Earth Observation Tools
==============================================================

poets is a package with aims to provide a standard library that can be used for
collecting and resampling geospatial image datasets.


Features
========

* easy download of geospatial image datasets provided via `Supported Data Sources`_.
* spatial resampling to a regular grid globally or to a specific country
* temporal resampling to monthly or dekadal intervals (more options will be available in future versions)
* saves resampled images as NetCDF4 file


Supported Data
==============

Supported Data Sources
----------------------

In order to work properly, all datasets must be provided via one of the 
following protocols:

* HTTP
* FTP
* SFTP

All files within a repository must be named following a certain structure, 
this structure MUST NOT vary.

Supported File Types
--------------------

poets supports following file types:

* NetCDF version >= 4.0
* png, jpg, tif and gif image files

The latter image files must have global coverage with longitudes from -180 to 
180 and latitudes from -90 to 90, with the left upper pixel at -180, 90 and the
right lower pixel at 180,-90.

Input files MUST NOT be compressed, support of compressed files will be enabled in future versions.


Installation
============

Prerequisites
-------------

In order to use all poets features python version 2.7.5 with the following packages has to be installed

* pytesmo >= 0.2.0 http://rs.geo.tuwien.ac.at/validation_tool/pytesmo/
* numpy >= 1.7.0 http://www.numpy.org/
* pandas >= 0.12.0 http://pandas.pydata.org/
* scipy >= 0.12.0 http://www.scipy.org/
* statsmodels >= 0.4.3 http://statsmodels.sourceforge.net/
* netCDF4 >= 1.0.1 https://pypi.python.org/pypi/netCDF4
* Shapely >= 1.3.2 http://toblerity.org/shapely/
* pyshp >=1.2.1 https://code.google.com/p/pyshp/
* paramiko >= 1.14.0 http://paramiko-www.readthedocs.org/
* requests >= 1.14.0 http://docs.python-requests.org/
* pillow >= 2.5.1 http://pillow.readthedocs.org/

How to install python packages
------------------------------

If you have no idea of how to install python packages then I'll try to give a short overview and provide links to resources that can explain
the process.

The recommended way of installing python packages is using `pip <https://pip.pypa.io/en/latest/installing.html>`_ which downloads the package
you want from the `python package repository Pypi <https://pypi.python.org/>`_ and installs it if possible. For more complex packages that depend 
upon a C or Fortran library like netCDF4 or pybufr-ecmwf installation instructions are provided on the package website.

Linux
-----

If you already have a working python installation with the necessary packages download and unpack the poets source package which is available from

* Pypi https://pypi.python.org/pypi/poets

just change the active directory to the unpacked poets-0.1.0 folder and use the following command in the command line::
   
   python setup.py install

or if you'd rather use pip then use the command::
   
   pip install poets
   
Contribute
==========

If you would like to help this project by improving the documentation, 
providing examples of how you use it or by extending the functionality of poets we would be very happy.

Please browse the source code which is available at http://github.com/TUW-GEO/poets

Feel free to contact `Thomas Mistelbauer <http://rs.geo.tuwien.ac.at/our-team/thomas-mistelbauer/>`_ in case of any questions or requests.

Ancillary data
==============

The world country boundary shape file was downloaded from 
http://geocommons.com/overlays/33578

