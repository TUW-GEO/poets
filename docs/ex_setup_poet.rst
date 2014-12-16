Setting up a Poet base class
============================

To be able to use poets, a :class:`poets.poet.Poet` class must be initialized.
You can find a description of the class parameters and attribures here: :class:`poets.poet.Poet`.

In[1]::

   import os
   from datetime import datetime
   from poets.poet import Poet
   
   # poets attributes:
   rootpath = os.path.join('D:\\', 'Test')
   regions = ['AU'] # clipping to Austria
   spatial_resolution = 0.1
   temporal_resolution = 'dekad'
   start_date = datetime(2000, 1, 1)
   nan_value = -99
   
   # initializing Poet class:
   p = Poet(rootpath, regions, spatial_resolution, temporal_resolution, 
            start_date, nan_value)


Usage of custom shapefiles
==========================

Resampling and clipping data to a regions specified in a custom shapefile is available since v0.3.1.
A link to the custom shapefile must be set with the 
:class:`poets.poet.Poet` `shapefile` parameter.
The shapefile itself must contain one attribute whicht contains a unique ID or Code,
which is used to select the desired region/area with the :class:`poets.poet.Poet`
`regions` parameter. The shapefile must be in given in WGS 84.

The following example extends the code from `In[1]` with the shapefile parameter. In this case,
the shapefile is locally stored at `D:\\Shapefiles\\shapefile1.shp`, and we want to clip the data
to `region1` and `region2`.
Please note that the file-suffix ".shp" MUST NOT be set in the shapefile parameter!

In[2]::

   # use custom shapefile:
   shapefile = os.path.join('D:\\', 'Shapefiles', 'shapefile1')
   regions = ['region1', 'region2']
   
   # initializing Poet class:
   p = Poet(rootpath, regions, spatial_resolution, temporal_resolution, 
            start_date, nan_value, shapefile=shapefile)


Adding a source
===============

Data sources can be added via the :class:`poets.poet.Poet.add_source` method.
In order to be able to extract the date out of the filename of imagefiles, it is necessary to provide
the location of the date attributes within the filename with the parameter `filedate`. We know that
this is very unfortunate, but we'll promise to work on a more convenient method.

In[3]::
   
   # source attributes:
   name = 'MODIS_LST'
   filename = "MOD11C1_D_LSTDA_{YYYY}_{MM}-{DD}.png"
   filedate = {'YYYY': (16, 20), 'MM': (21, 23), 'DD': (24, 26)}
   temp_res = 'daily'
   host = "neoftp.sci.gsfc.nasa.gov"
   protocol = 'FTP'
   directory = "/gs/MOD11C1_D_LSTDA/"
   begin_date = datetime(2000, 1, 1)
   nan_value = 255
   
   # initializing the data source:
   p.add_source(name, filename, filedate, temp_res, host, protocol,
                directory=directory, begin_date=begin_date,
                nan_value=nan_value)

