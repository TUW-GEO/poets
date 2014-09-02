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
import matplotlib.pyplot as plt
from flask import Flask, render_template, jsonify, request, views
import datetime
from poets.web.overlays import bounds
from poets.poet import Poet
from poets.timedate.dekad import dekad_index


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


def start(p):

    app = Flask(__name__, static_folder='static', static_url_path='/static',
                template_folder="templates")

    region = 'MO'
    source = 'TAMSAT'
    variable = 'TAMSAT_rfe'
    dest = os.path.join(curpath(), 'static')

    ndate = p.sources[source]._check_current_date()
    begindate = ndate[region][variable][0]
    enddate = ndate[region][variable][1]

    d = dekad_index(begindate, enddate)
    dates = d.to_pydatetime()
    idxdates = len(dates)

    vmin = 0
    vmax = 20
    cmap = 'jet_r'


    class ol_osm(views.MethodView):
        def get(self):
            lon_min, lon_max, lat_min, lat_max, c_lat, c_lon, zoom = bounds(region)
            img, _, _ = p.read_image(source, enddate, region, variable)
            filename = region + '_' + variable + '_' + str(idxdates) + '.png'
            filepath = os.path.join(dest, filename)
            plt.imsave(filepath, img, vmin=vmin, vmax=vmax, cmap=cmap)

            return render_template('images.html',
                                   max=idxdates,
                                   coord=[c_lon, c_lat],
                                   zoom=zoom,  # depends on map div width,
                                   ex1=(lon_max, lat_min),
                                   ex2=(lon_min, lat_max),
                                   ovl="../static/" + filename)


    @app.route('/_pretty_date')
    def pretty_date():
        idx = request.args.get('current', 0, type=int)
        min = request.args.get('min', 0, type=int)
        max = request.args.get('max', idxdates, type=int)
        pretty = (dates[idx].strftime('%Y-%m-%d'))
        begin = (dates[min].strftime('%Y-%m-%d'))
        end = (dates[max - 1].strftime('%Y-%m-%d'))
        return jsonify(begin=begin, end=end, currentV=pretty)


    @app.route('/_rdat')
    def request_data():
        idx = request.args.get('current', 0, type=int)
        pidx = (dates[idx])
        filename = region + '_' + variable + '_' + str(idx) + '.png'
        filepath = os.path.join(dest, filename)

        if not os.path.isfile(os.path.join(filepath, filename)):
            img, _, _ = p.read_image(source, pidx, region, variable)
            plt.imsave(filepath, img, vmin=vmin, vmax=vmax, cmap=cmap)

        path = '../static/' + filename
        return jsonify(rdat=path)

    @app.route('/')
    def index():

        return render_template('index.html', sources=sources)
    app.run(debug=True)


if __name__ == "__main__":
    app.run(debug=True)
