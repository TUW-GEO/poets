---
layout: splash
permalink: /
header:
  overlay_color: "#000000"
  overlay_image: earth-banner.JPG
  cta_label: "<i class='fa fa-play-circle'></i> Getting Started"
  cta_url: "/docs/quick-start-guide/"
  caption: Image courtesy of the Earth Science and Remote Sensing Unit, NASA Johnson Space Center
excerpt: 'Python Open Earth Observation Tools'
---

Poets° is a collection of Python packages for the downloading, reading,
conversion and comparison of geospatial data. The included packages cover the
following broad features:

- Automated downloading of supported products.
- Conversion of image/swath based products into time series based formats.
- Reading of the resulting geospatial time series dataset.
- Comparison or Validation of multiple geospatial time series datasets.

The Python packages that form Poets° can be used as standalone libraries or in
combination. The packages are:

- [`pygeobase`](https://github.com/tuw-geo/pygeobase) contains the abstract
  base classes that define the interfaces for reading and writing supported
  datasets. These base classes ensure a consistent interface to all datasets.
- [`pygeogrids`](https://github.com/tuw-geo/pygeogrids) is a package for working with discrete global grids
  (DGGs) on different geodetic datums, it also supports nearest neighbor
  search and lookup table creation.
- [`pynetcf`](https://github.com/tuw-geo/pynetcf) implements the interface defined in `pygeobase`
  for netCDF files with a focus on the time series representations defined
  in the Climate and Forecast Metadata Conventions (CF Conventions).
- [`repurpose`](https://github.com/tuw-geo/repurpose) is a package that performs the conversion from the
  time-slice image or swath based format most remote sensing or modeled
  products come in into a time series optimized format. It uses
  `pynetcf` for writing the output time series.
- [`smap_io`](https://github.com/tuw-geo/smap_io) is a package that supports downloading, reading and
  conversion to time series of SMAP data.
- [`ascat`](https://github.com/tuw-geo/ascat) is a package that supports reading of ASCAT Level 2 and
  H-SAF soil moisture products based on the ASCAT sensor.
- the `gldas` package supports downloading, reading and conversion
  of GLDAS Noah data.
- [`ecmwf_models`](https://github.com/tuw-geo/ecmwf_models) is a Python package for downloading, reading and
  conversion of ERA Interim data.
- [`pytesmo`](https://github.com/tuw-geo/pytesmo) is the Python Toolbox for the Evaluation of Soil Moisture
  Observations and contains the validation framework, implementations of common
  metrics and readers for the data from the International Soil Moisture Network
  (ISMN). 
