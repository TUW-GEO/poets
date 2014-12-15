Web Interface
=============

Once Poets is set up, data is downloaded and resampled it is time to check out
the built in web interface. All you have to do is run the :class:`poets.poet.Poet.start_app` command.

In[12]::

   p.start_app()

By default, the app will run on host `127.0.0.1` and port `5000`. However, other values
can be set with the keywords `host` and `port`.

In[13]::

   p.start_app(host='111.222.3.44', port=1234)
  
   

Using colorbars and units
-------------------------

The default colorbar used for displaying images is matplotlibs `jet`. You choose any colorbar
from `this list <http://matplotlib.org/examples/color/colormaps_reference.html>`_ by setting
the :class:`poets.poet.Poet.add_source` colorbar parameter. Further, if the physical unit
of the dataset is not given in its metadata, you can set the unit manually with the `unit` parameter.
In our example the unit would be `degree celsius`.

In[14]::
  
   # setting the colobar for a source:
   p.add_source(..., colorbar='Blues', unit='degree celsius')
   

Scaling data
------------
By default, poets supports scaling of data if a corresponding parameter is given in the metadata of the source data.
Sometimes, this information is missing although the data is scaled. In our example the each MODIS_LST file contains values
between 0 and 255, where 255 represents the NaN value. In this case, we need to set the parameters
`nan_value` and `data_range` when adding a source with :class:`poets.poet.Poet.add_source`. Further, we need to scale the 
dataset to its actual value range between min -25°C and max 45°C.

in[15]::

   p.add_source(..., nan_value=255, data_range=(0, 254), valid_range=(-25, 45))
   



Complete Example
================

In[16]::

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
   p = Poet(rootpath, regions, spatial_resolution, temporal_resolution,
            start_date, nan_value)
   
   # setting source attributes:             
   name = 'MODIS_LST'
   filename = "MOD11C1_D_LSTDA_{YYYY}_{MM}-{DD}.png"
   filedate = {'YYYY': (16, 20), 'MM': (21, 23), 'DD': (24, 26)}
   temp_res = 'daily'
   host = "neoftp.sci.gsfc.nasa.gov"
   protocol = 'FTP'
   directory = "/gs/MOD11C1_D_LSTDA/"
   begin_date = datetime(2000, 2, 24)
   nan_value = 255
   data_range = (0, 254)
   valid_range = (-25, 45)
   unit = "degree Celsius"
   
   # adding the source
   p.add_source(name, filename, filedate, temp_res, host, protocol,
                directory=directory, begin_date=begin_date,
                nan_value=nan_value, valid_range=valid_range,
                data_range=data_range, unit=unit)
   
   
   # get the data (in this example from beginning of 2014)   
   p.fetch_data(begin=datetime(2014,1,1)
   
   
   # start the web interface
   p.start_app()