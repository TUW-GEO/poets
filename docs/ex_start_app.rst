Start Web Interface
===================

Once Poets is set up, data is downloaded and resampled it is time to check out
the built in web interface. All you have to do is run the :class:`poets.poet.Poet.start_app` command.

In[10]::

   p.start_app()


Complete Example
================

In[11]::

   import os
   from datetime import datetime
   from poets.poet import Poet
   
   # poets attributes:
   rootpath = os.path.join('D:\\', 'Test') # Wherever the data should be stored
   regions = ['AU'] # clipping to Austria
   spatial_resolution = 0.1
   temporal_resolution = 'dekad'
   start_date = datetime(2000, 1, 1)
   nan_value = -99
   
   # initializing Poet class:
   p = Poet(rootpath, regions, spatial_resolution, temporal_resolution, start_date, nan_value)
   
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
   
   
   # get the data (in this example from beginning of 2014)   
   p.fetch_data(begin=datetime(2014,1,1)
   
   
   # start the web interface
   p.start_app()