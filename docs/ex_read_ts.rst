Reading and plotting time series
================================

This example shows how to read and plot time series data from the resampled NetCDF file.
It presumes that we already set up a Poet class and added the source `MODIS_LST` as 
given in `Setting up a Poet base class`_. For plotting, we will use `Matplotlib <http://matplotlib.org>`_.

Reading the image can be done with the :class:`poets.io.source_base.BasicSource.read_ts` method.
You can read time series only for gridpoints given in the defined region(s). To get a list of available
gridpoints, you can call :class:`poets.poet.Poet.get_gridpoints`. 


In[10]::

   import matplotlib.pyplot as plt
   
   # Get a list of valid gridpoints
   gridpoints = p.get_gridpoints()
   
   # Reading the time series for point 1632
   ts = p.sources['MODIS_LST'].read_ts(1632)
   
   # Plot time series
   ts.plot()
   plt.show()


.. image:: images/read_ts_austria.png