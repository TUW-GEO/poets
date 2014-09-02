'''
Created on Jul 22, 2014

@author: Maximilian Wonaschuetz
'''

import os

import datetime
from flask import Flask, render_template, jsonify, request, views
from poets.web.overlays import bounds
from poets.poet import Poet
from poets.timedate.dekad import dekad_index
import matplotlib.pyplot as plt


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth

# POETS SETTINGS
spatial_resolution = 0.25
temporal_resolution = 'dekad'
rootpath = '/media/sf_D/TEST/poets'
nan_value = -99
start_date = datetime.datetime(2000, 1, 1)
regions = ['MO']

p = Poet(rootpath, regions, spatial_resolution, temporal_resolution,
         start_date, nan_value)

# SOURCE SETTINGS
name = 'TAMSAT'
filename = "rfe{YYYY}_{MM}-dk{P}.nc"
filedate = {'YYYY': (3, 7), 'MM': (8, 10), 'P': (13, 14)}
temp_res = 'dekad'
host = "http://www.met.reading.ac.uk"
protocol = 'HTTP'
directory = '~tamsat/public_data'
dirstruct = ['YYYY', 'MM']
begin_date = datetime.datetime(1983, 11, 1)
variables = ['rfe']

p.add_source(name, filename, filedate, temp_res, host, protocol,
             directory=directory, dirstruct=dirstruct,
             begin_date=begin_date, variables=variables)

app = Flask(__name__, static_folder='static', static_url_path='/static')

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

if __name__ == '__main__':
    app.add_url_rule('/', view_func=ol_osm.as_view('main'),
                     methods=['GET', 'POST'])
    app.run(debug=True, use_debugger=True, use_reloader=True)
