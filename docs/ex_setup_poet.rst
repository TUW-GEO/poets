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
   p = Poet(rootpath, regions, spatial_resolution, temporal_resolution, start_date, nan_value)
   
Adding a source
===============

Data sources can be added via the :class:`poets.poet.Poet.add_source` method.
In order to be able to extract the date out of the filename of imagefiles, it is necessary to provide
the location of the date attributes within the filename with the parameter `filedate`. We know that
this is very unfortunate, but we'll promise to work on a more convenient method.

In[2]::
   
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

