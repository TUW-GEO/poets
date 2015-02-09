# Copyright (c) 2014, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# * Redistributions of source code must retain the above copyright notice, this
#   list of conditions and the following disclaimer.
#
# * Redistributions in binary form must reproduce the above copyright notice,
#   this list of conditions and the following disclaimer in the documentation
#   and/or other materials provided with the distribution.
#
# * Neither the name of the Vienna University of Technology - Department of
#   Geodesy and Geoinformation nor the names of its contributors may be used to
#   endorse or promote products derived from this software without specific
#   prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED. IN NO EVENT SHALL VIENNA UNIVERSITY OF TECHNOLOGY,
# DEPARTMENT OF GEODESY AND GEOINFORMATION BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA,
# OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE,
# EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

# Author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-05-26

from cStringIO import StringIO
import os
from flask import Flask, render_template, jsonify, make_response
from flask.ext.cors import CORS
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from poets.timedate.dateindex import get_dtindex
from poets.web.overlays import bounds
import pytesmo.time_series as ts


def curpath():
    """
    Gets the current path of the module.

    Returns
    -------
    pth : str
        Path of the module.
    """
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


def to_dygraph_format(self):
    """
    Transforms pandas DataFrame to Dygraphs compatible format.

    Returns
    -------
    labels : list of str
        Labels of the Dygraphs array.
    values : list
        Values of the Dygraphs array.
    """

    labels = ['date']
    labels.extend(self.columns.values.tolist())
    data_values = np.hsplit(self.values, self.columns.values.size)
    data_index = self.index.values.astype('M8[s]').tolist()
    data_index = [x.strftime("%Y/%m/%d %H:%M:%S") for x in data_index]
    data_index = np.reshape(data_index, (len(data_index), 1))
    data_values.insert(0, data_index)
    data_values = np.column_stack(data_values)
    values = data_values.tolist()

    return labels, values

pd.DataFrame.to_dygraph_format = to_dygraph_format

dest = os.path.join(curpath(), 'static', 'temp')

app = Flask(__name__, static_folder='static', static_url_path='/static',
            template_folder="templates")
app.config['CORS_HEADERS'] = 'Content-Type'
cors = CORS(app, resources={r"/*": {"origins": "*"}})


def start(poet, host='127.0.0.1', port=5000, r_host=None, r_port=None,
          debug=False):
    """
    Starts application and sets global variables.

    Parameters
    ----------
    poet : Poet()
        Instance of Poet class.
    host : str, optional
        Host that is used by the app, defaults to 127.0.0.1.
    port : int, optional
        Port where app runs on, defaults to 50000.
    r_host : str, optional
        IP of router that is between host and internet.
    r_port : int, optional
        Port of router that is between host and internet.
    debug : bool, optional
        Starts app in debug mode if set True, defaults to False.
    """

    global p
    global variables
    global dates
    global vmin, vmax, cmap
    global host_gl
    global port_gl

    p = poet
    variables = poet.get_variables()
    if r_host is None:
        host_gl = host
    else:
        host_gl = r_host
    if r_port is None:
        port_gl = port
    else:
        port_gl = r_port

    if debug:
        app.run(debug=True, use_debugger=True, use_reloader=True, host=host,
                port=port)
    else:
        app.run(host=host, port=port)


@app.route('/', methods=['GET', 'POST'])
@app.route('/<reg>&<var>', methods=['GET', 'POST'])
def index(**kwargs):
    """
    Renders main page of the web application. Generates image arguments needed
    for OpenLayers overlay if parameters `reg` and `var` are set, renders
    entry page if not set.
    """

    global enddate
    global dates
    global ndate

    regions = []
    for i, reg in enumerate(p.regions):
        regions.append({'code': reg, 'name': p.region_names[i]})

    if len(kwargs) > 0:

        if 'reg' in kwargs:
            region = kwargs['reg']
        if 'var' in kwargs:
            variable = kwargs['var']

        for src in p.sources.keys():
            if variable in p.sources[src].get_variables():
                source = p.sources[src]

        ndate = source._check_current_date()
        begindate = ndate[region][variable][0]
        enddate = ndate[region][variable][1]

        if begindate is None and enddate is None:

            error = 'No data available for this dataset.'

            return render_template('index.html',
                                   regions=p.regions,
                                   sources=p.sources.keys(),
                                   variables=variables,
                                   error=error)

        d = get_dtindex(p.temporal_resolution, begindate, enddate)
        dates = d.to_pydatetime()

        fdates = []

        for i, d in enumerate(dates.tolist()):
            dat = {'id': i, 'date': d.strftime('%Y-%m-%d')}
            fdates.append(dat)

        lon_min, lon_max, lat_min, lat_max, c_lat, c_lon, _ = \
            bounds(region, p.shapefile)

        if source.valid_range is None:
            vrange = [-999, -999]
        else:
            vrange = source.valid_range

        return render_template('app.html',
                               max=len(dates) - 1,
                               coord=[c_lon, c_lat],
                               ex1=(lon_max, lat_min),
                               ex2=(lon_min, lat_max),
                               region=region,
                               source=source.name,
                               variable=variable,
                               regions=regions,
                               variables=variables,
                               dates=fdates,
                               host=host_gl,
                               port=port_gl,
                               sp_res=p.spatial_resolution,
                               range=vrange
                               )
    else:
        return render_template('index.html',
                               regions=regions,
                               sources=p.sources.keys(),
                               variables=variables,
                               host=host_gl,
                               port=port_gl)


@app.route('/_ts/<reg>&<src>&<var>&<loc>', methods=['GET', 'OPTIONS'])
@app.route('/_ts/<reg>&<src>&<var>&<loc>&<anom>', methods=['GET', 'OPTIONS'])
def get_ts(**kwargs):
    """
    Gets time series for selected location, gets anomaly of time series if
    `anom` parameter is passed.

    Returns
    -------
    jsonified str
        Time series (anomaly) in Dygraphs compatible json format.
    """

    anomaly = False

    if 'reg' in kwargs:
        region = kwargs['reg']
    if 'src' in kwargs:
        source = p.sources[kwargs['src']].name
    if 'var' in kwargs:
        variable = kwargs['var']
    if 'loc' in kwargs:
        loc = kwargs['loc']
    if 'anom' in kwargs:
        anomaly = True

    loc = loc.split(',')
    lonlat = (float(loc[0]), float(loc[1]))

    df = p.read_timeseries(source, lonlat, region, variable)

    if anomaly:
        df = ts.anomaly.calc_anomaly(df, window_size=100)
        columns = []
        for cols in df.columns:
            columns.append(cols + '_anomaly')
        df.columns = columns

    labels, values = df.to_dygraph_format()
    data = {'labels': labels, 'data': values}

    return jsonify(data)


@app.route('/_tsdown/<reg>&<src>&<var>&<loc>')
@app.route('/_tsdown/<reg>&<src>&<var>&<loc>&<anom>')
def download_ts(**kwargs):
    """
    Initiates download time series (anomaly) in comma separated values format.

    Returns
    -------
    jsonified str
        Time series (anomaly) in Dygraphs compatible json format.
    """

    anomaly = False

    if 'reg' in kwargs:
        region = kwargs['reg']
    if 'src' in kwargs:
        source = p.sources[kwargs['src']]
    if 'var' in kwargs:
        variable = kwargs['var']
    if 'loc' in kwargs:
        loc = kwargs['loc']
    if 'anom' in kwargs:
        anomaly = True

    loc = loc.split(',')
    lonlat = (float(loc[0]), float(loc[1]))

    filename = region + '_' + variable + '_' + loc[0][:6] + '_' + loc[1][:6]

    df = p.read_timeseries(source.name, lonlat, region, variable)

    if anomaly:
        df = ts.anomaly.calc_anomaly(df)
        columns = []
        for cols in df.columns:
            columns.append(cols + '_anomaly')
        df.columns = columns

        filename += '_anomaly'

    output = StringIO()

    df.to_csv(output)
    csv = output.getvalue()

    response = make_response(csv)
    response.headers["Content-Disposition"] = ("attachment; filename=" +
                                               filename + ".csv")

    return response


@app.route('/_rimg/<reg>&<src>&<var>&<idx>', methods=['GET', 'POST'])
def request_image(**kwargs):
    """
    Creates image for OpenLayers overlay.

    Returns
    -------
    StringIO
        Image in StringIO.
    """

    global vmin
    global vmax
    global metadata
    global cmap

    if 'reg' in kwargs:
        region = kwargs['reg']
    if 'src' in kwargs:
        source = p.sources[kwargs['src']]
    if 'var' in kwargs:
        variable = kwargs['var']
    if 'idx' in kwargs:
        idx = kwargs['idx']

    pidx = (dates[int(idx)])

    img, _, _, metadata = p.read_image(source.name, pidx, region, variable)

    if source.unit is not None:
        if metadata is not None and 'unit' not in metadata:
            metadata['unit'] = source.unit
        elif metadata is None:
            metadata = {}
            metadata['unit'] = source.unit

    if source.valid_range is not None:
        vmin = source.valid_range[0]
        vmax = source.valid_range[1]
    else:
        vmin = np.nanmin(img)
        vmax = np.nanmax(img)

    cmap = source.colorbar

    # Rescale the image
    n = 10
    img = np.kron(img, np.ones((n, n)))
    img[img == p.nan_value] = np.NAN

    buf = StringIO()
    plt.imsave(buf, img, vmin=vmin, vmax=vmax, cmap=cmap)

    image = buf.getvalue()

    response = make_response(image)
    response.headers["Content-Type"] = ("image/png; filename=data.png")

    return response


@app.route('/_rlegend/<reg>&<var>', methods=['GET', 'POST'])
@app.route('/_rlegend/<reg>&<var>&<idx>', methods=['GET', 'POST'])
def request_legend(**kwargs):
    """
    Creates Legend for OpenLayers overlay.

    Returns
    -------
    StringIO
        Legend in StringIO.
    """

    global vmin
    global vmax
    global metadata
    global cmap

    fig = plt.figure(figsize=(4, 0.7))
    ax1 = fig.add_axes([0.05, 0.7, 0.9, 0.10])
    norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
    cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm,
                                    orientation='horizontal')
    plt.xticks(fontsize=9)

    if metadata:
        units = ['units', 'unit', 'UNITS', 'UNIT']
        for unit in units:
            if unit in metadata:
                cb1.set_label(metadata[unit], fontsize=10)

    buf = StringIO()
    fig.patch.set_alpha(0.6)
    plt.savefig(buf)
    plt.close()

    image = buf.getvalue()

    response = make_response(image)
    response.headers["Content-Type"] = ("image/png; filename=legend.png")

    return response


@app.route('/_variables', methods=['GET', 'POST'])
@app.route('/_variables/<reg>', methods=['GET', 'POST'])
def request_variables(**kwargs):

    if 'reg' in kwargs:
        region = kwargs['reg']
    else:
        region = None

    variables = {}
    variables['variables'] = p.get_variables(region)

    return jsonify(variables)


@app.route('/about')
def about():
    """
    Creates the `about` page.
    """
    return render_template('about.html')
