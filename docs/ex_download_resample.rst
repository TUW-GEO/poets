Download and resample data
==========================

After `setting up a Poet class and adding some sources`_, we can now start downloading and resampling the data by calling the :class:`poets.poet.Poet.fetch_data` method.

In[3]::
   
   p.fetch_data()
   
That's it! The :class:`poets.poet.Poet.fetch_data` method will now go through all defined sources and start downloading and resampling the data.
The resampled NetCDF file will be saved to the `DATA` folder within the rootpath as defined above.

The fetch_data method will download data starting from the begin_date as defined in the source up to the current date.
If you want to download and resample only a specific time period, you can do so by calling the method with the parameters `begin` and `end`.

In[4]::
   
   # Download and resample data for January 2000:
   p.fetch_data(begin=datetime(2000,1,1), end=datetime(2000,1,31))
   
   # Download and resample data from 2005 on:
   p.fetch_data(begin=datetime(2005,1,1))
   
   # Download and resample data until 2005:
   p.fetch_data(end=datetime(2004,12,13))

By default, downloaded rawdata will be kept in the `TMP` folder. However, if you do not need this data you can delete it by setting the delete_rawdata flag as followed:

In[5]::

   # Delete rawdata after resampling
   p.fetch_data(delete_rawdata=True)


Download and resample data from sources individually
----------------------------------------------------
The :class:`poets.poet.Poet.fetch_data` downloads and resamples data from all sources.
However, if you want to fetch data from only one source, you can do so by calling the :class:`poets.io.source_base.download_and_resample` method.
This method can be called within the :class:`poets.poet.Poet` class by accessing the source as followed:

In[6]::

   p.sources['MODIS_LST'].download_and_resample()
   
You can use the parameters begin, end and delete_rawdata as described in `Download and resample data`_.
   
Download only
-------------
If you only want to download the data without resampling it, you can do so by calling the :class:`poets.io.source_base.download` method.
You can use the parameters begin, end and delete_rawdata as described in `Download and resample data`_.

In[7]::

   p.sources['MODIS_LST'].download()
   
Resampling only
---------------

If you already downloaded data manually and only want to resample it, you can do so by calling the :class:`poets.io.source_base.resample` method.
You can use the parameters begin, end and delete_rawdata as described in `Download and resample data`_.

In[8]::

   p.sources['MODIS_LST'].resample()