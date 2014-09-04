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
import matplotlib.pyplot as plt
from flask import Flask, render_template, jsonify, request, views
import datetime
from poets.web.overlays import bounds
from poets.timedate.dekad import dekad_index


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth

dest = os.path.join(curpath(), 'static')

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
    cmap = 'jet_r'

    app.run(debug=True, use_debugger=True, use_reloader=True)


@app.route('/<reg>-<src>-<var>', methods=['GET', 'POST'])
def index(**kwargs):
    global enddate
    global dates
    global ndate
    global idxdates
    global dates

    if 'reg' in kwargs:
        region = kwargs['reg']
    if 'src' in kwargs:
        source = sources[kwargs['src']]
    if 'var' in kwargs:
        variable = kwargs['var']

    print variables

    ndate = source._check_current_date()
    begindate = ndate[region][variable][0]
    enddate = ndate[region][variable][1]

    d = dekad_index(begindate, enddate)
    dates = d.to_pydatetime()
    idxdates = len(dates)

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

    return render_template('images.html',
                           max=idxdates,
                           coord=[c_lon, c_lat],
                           zoom=zoom,  # depends on map div width,
                           ex1=(lon_max, lat_min),
                           ex2=(lon_min, lat_max),
                           ovl="../static/" + filename,
                           legend="../static/" + legendname,
                           region=region,
                           source=source.name,
                           variable=variable,
                           regions=regions,
                           variables=variables)


@app.route('/_pretty_date')
def pretty_date():
    idx = request.args.get('current', 0, type=int)
    min = request.args.get('min', 0, type=int)
    max = request.args.get('max', idxdates, type=int)
    pretty = (dates[idx].strftime('%Y-%m-%d'))
    begin = (dates[min].strftime('%Y-%m-%d'))
    end = (dates[max - 1].strftime('%Y-%m-%d'))
    return jsonify(begin=begin, end=end, currentV=pretty)


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

    path = '../static/' + filename
    return jsonify(rdat=path)
