========
Examples
========

Some notes before we start
==========================
This version of poets supports resampling to a daily, weekly, monthly or dekadal interval, with values at the period end.
Dekadal resolution provides 3 values per month at day 10, day 20 and the last day of the month.

If you want your data to be resampled and clipped to one or multiple countries, 
you need to provide a list containing the `FIPS country codes <https://en.wikipedia.org/wiki/FIPS_country_code>`_ for each country.
['AA', 'AC'] for example would represet Aruba and Antigua and Barbuda.
If you want to youse your own shapefile, please read `Usage of custom shapefiles`_. If you want the data to be resampled globally, just skip the regions parameter.

In our example, we want to resample `MODIS Land Surface Temperature <http://neo.sci.gsfc.nasa.gov/view.php?datasetId=MOD11C1_D_LSTDA>`_ data over the area of Austria to a resolution of 0.1° on a dekadal basis.

But now let's start...

.. include::
   ex_setup_poet.rst
   
.. include::
   ex_download_resample.rst
   
.. include::
   ex_read_img.rst
   
.. include::
   ex_read_ts.rst
   
.. include::
   ex_start_app.rst

