==============================================================
Introduction to poets, the Python Open Earth Observation Tools
==============================================================
poets is a package with aims to provide a standard library that can be used for
collecting and resampling geospatial image datasets.


Features
========

* easy download of geospatial image datasets provided via `Supported Data 
  Sources`
* spatial and temporal resampling of datasets
* saves resampled images as NetCDF4 file
* web interface for displaying images and time series in a browser


Supported Datasets
==================

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
* GeoTiff
* png, jpg, and gif image files

The latter image files must have global coverage with longitudes from -180 to 
180 and latitudes from -90 to 90, with the left upper pixel at -180, 90 and the
right lower pixel at 180,-90.

Ancillary data
==============

The world country boundary shape file was downloaded from 
http://geocommons.com/overlays/33578

