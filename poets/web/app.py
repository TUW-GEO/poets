# Copyright (c) 2014, Vienna University of Technology (TU Wien), Department
# of Geodesy and Geoinformation (GEO).
# All rights reserved.

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

import os
import matplotlib as mpl
mpl.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from flask import Flask, render_template, jsonify, request
from poets.web.overlays import bounds
from poets.timedate.dekad import dekad_index


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


def to_dygraph_format(self):
    labels = ['date']
    labels.extend(self.columns.values.tolist())
    data_values = np.hsplit(self.values, self.columns.values.size)
    data_index = self.index.values.astype('M8[s]').tolist()
    data_index = [x.strftime("%Y/%m/%d %H:%M:%S") for x in data_index]
    data_index = np.reshape(data_index, (len(data_index), 1))
    data_values.insert(0, data_index)
    data_values = np.column_stack(data_values)

    return labels, data_values.tolist()

pd.DataFrame.to_dygraph_format = to_dygraph_format

dest = os.path.join(curpath(), 'static', 'temp')

app = Flask(__name__, static_folder='static', static_url_path='/static',
            template_folder="templates")


def start(poet):

    global regions
    global sources
    global variables
    global vmin, vmax, cmap

    regions = poet.regions
    sources = poet.sources
    variables = poet.get_variables()

    vmin = 0
    vmax = 20
    cmap = 'jet'

    app.run(debug=True, use_debugger=True, use_reloader=True)


@app.route('/', methods=['GET', 'POST'])
@app.route('/<reg>-<var>', methods=['GET', 'POST'])
def index(**kwargs):
    global enddate
    global dates
    global ndate
    global idxdates

    if len(kwargs) > 0:

        if 'reg' in kwargs:
            region = kwargs['reg']
        if 'var' in kwargs:
            variable = kwargs['var']

        for src in sources.keys():
            if src in variable:
                source = sources[src]

        ndate = source._check_current_date()
        begindate = ndate[region][variable][0]
        enddate = ndate[region][variable][1]

        d = dekad_index(begindate, enddate)
        dates = d.to_pydatetime()
        idxdates = len(dates) - 1

        fdates = []

        for i, d in enumerate(dates.tolist()):
            dat = {'id': i, 'date': d.strftime('%Y-%m-%d')}
            fdates.append(dat)

        lon_min, lon_max, lat_min, lat_max, c_lat, c_lon, zoom = bounds(region)
        img, _, _ = source.read_img(enddate, region, variable)
        filename = region + '_' + variable + '_' + str(idxdates) + '.png'
        legendname = region + '_' + variable + '_legend.png'
        filepath = os.path.join(dest, filename)
        legend = os.path.join(dest, legendname)
        if source.valid_range is not None:
            vmin = source.valid_range[0]
            vmax = source.valid_range[1]
            plt.imsave(filepath, img, vmin=vmin, vmax=vmax, cmap=cmap)

            fig = plt.figure(figsize=(5, 0.8))
            ax1 = fig.add_axes([0.05, 0.7, 0.9, 0.10])
            norm = mpl.colors.Normalize(vmin=vmin, vmax=vmax)
            cb1 = mpl.colorbar.ColorbarBase(ax1, cmap=cmap, norm=norm, orientation='horizontal')
            # cb1.set_label('unit', fontsize=10)
            plt.savefig(legend)

        else:
            plt.imsave(filepath, img, cmap=cmap)

        return render_template('dv.html',
                               max=idxdates,
                               coord=[c_lon, c_lat],
                               zoom=zoom,  # depends on map div width,
                               ex1=(lon_max, lat_min),
                               ex2=(lon_min, lat_max),
                               ovl="../static/temp/" + filename,
                               legend="../static/temp/" + legendname,
                               region=region,
                               source=source.name,
                               variable=variable,
                               regions=regions,
                               variables=variables,
                               dates=fdates)
    else:
        return render_template('index.html',
                               regions=regions,
                               sources=sources.keys(),
                               variables=variables)


@app.route('/_rdat/<reg>-<src>-<var>')
def request_data(**kwargs):

    if 'reg' in kwargs:
        region = kwargs['reg']
    if 'src' in kwargs:
        source = sources[kwargs['src']]
    if 'var' in kwargs:
        variable = kwargs['var']

    idx = request.args.get('current', 0, type=int)
    pidx = (dates[idx])
    filename = region + '_' + variable + '_' + str(idx) + '.png'
    filepath = os.path.join(dest, filename)

    if not os.path.isfile(os.path.join(filepath, filename)):
        img, _, _ = source.read_img(pidx, region, variable)
        if source.valid_range is not None:
            vmin = source.valid_range[0]
            vmax = source.valid_range[1]
            plt.imsave(filepath, img, vmin=vmin, vmax=vmax, cmap=cmap)
        else:
            plt.imsave(filepath, img, cmap=cmap)

    path = '../static/temp/' + filename
    return jsonify(rdat=path)


@app.route('/_ts/<reg>&<src>&<var>&<loc>')
def get_ts(**kwargs):

    if 'reg' in kwargs:
        region = kwargs['reg']
    if 'src' in kwargs:
        source = sources[kwargs['src']]
    if 'var' in kwargs:
        variable = kwargs['var']
    if 'loc' in kwargs:
        loc = kwargs['loc']

    loc = loc.split(',')
    lonlat = (float(loc[0]), float(loc[1]))

    ts = source.read_ts(lonlat, region, variable)

    labels, values = ts.to_dygraph_format()
    data = {'labels': labels, 'data': values}

    return jsonify(data)
