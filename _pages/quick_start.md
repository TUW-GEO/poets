---
layout: splash
permalink: /quick_start_guide
header:
  overlay_color: "#000000"
excerpt: 'Introduction to Poets°'
---

# Downloading and conversion of data

Remote sensing and modelled datasets are often distributed in image or swath
based formats. These formats are not ready to be used for efficient time series
analysis. They have to be converted into a time series representation. The
dataset packages that belong to Poets° offer functionality to download and
convert the data into a time series format. Downloading can of course also be
performed manually but using the included command line scripts stores the data
in the correct folder structure which makes it easier to use the commands for
time series conversion.

The chosen format for the time series is one of the representations defined in
the
[CF Conventions](http://cfconventions.org/cf-conventions/v1.6.0/cf-conventions.html#representations-features).
The exact format is described in the documentation of each package. Please find
the detailed information about the conversion at the following locations.

- [SMAP](http://smap-io.readthedocs.io/en/latest/#conversion-to-time-series-format)
- [GLDAS](http://gldas.readthedocs.io/en/latest/img2ts.html)
- [ECMWF Models](http://ecmwf-models.readthedocs.io/en/latest/#conversion-to-time-series-format)

ASCAT data is already available in
a
[timeseries format](http://ascat.readthedocs.io/en/latest/#time-series-products)
so no conversion is necessary.

# Reading of time series data

After conversion the time series are all accessible under the same API. 


```python
# Example of reading GLDAS time series data

from gldas.interface import GLDASTs
ds = GLDASTs(ts_path)
# read_ts takes either lon, lat coordinates or a grid point indices.
# and returns a pandas.DataFrame
ts = ds.read_ts(45, 15)
```

Detailed instructions for reading the data can be found in the documentation of
each dataset package linked above.

# Using the data in the pytesmo validation framework

The pytesmo validation framework implements the following processing modeled:

![Processing model]({{ site.url }}/poets/images/processing_model.svg)

More detailed information about how the framework works can be found in
the
[pytesmo documentation](http://pytesmo.readthedocs.io/en/latest/examples.html#the-pytesmo-validation-framework).
This example currently shows a validation of ISMN data and the ASCAT products.
Other examples are in preparation.

The framework can be used together with the datasets supported by Poets° but it
is also possible to write compatible interfaces to datasets you might already
have. The basic requirement is that the dataset can be accessed by a function
that takes the two arguments `longitude` and `latitude` and returns
a
[`pandas.DataFrame`](http://pandas.pydata.org/pandas-docs/stable/generated/pandas.DataFrame.html).



