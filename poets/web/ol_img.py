'''
Created on Jul 22, 2014

@author: Maximilian Wonaschuetz
'''
from flask import Flask, render_template, jsonify, request, views
from USER_DEV.mwona.bounds import bounds # function for the bounding box
from poets.poet import Poet
from poets.timedate.dekad import dekad_index
import datetime  # for handling the date request
# import numpy as np # for image classification
from PIL import Image
import os

# POETS SETTINGS
spatial_resolution = 0.25
temporal_resolution = 'dekad'
rootpath = '/media/sf_H/'
nan_value = -99
start_date = datetime.datetime(1978, 10, 1)
regions = ['ET']

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

country = 'ET'
var = 'rfe'
dest = '/media/sf_H/swdvlp/GEO_Python/USER_DEV/mwona/static/'

t = p.sources['TAMSAT']

ndate = t._check_current_date()
begindate = ndate[country][var][0]
enddate = ndate[country][var][1]

d = dekad_index(begindate, enddate)
dates = d.to_pydatetime()
idxdates = len(dates)


#==============================================================================
#     # image classification try
# pidx = (dates[266])
#   
# tamsat_img = t.read_img(pidx)
# a = tamsat_img[0].data
# max_value = a.max()  
# min_value = 0 #a.min()
# xsize = a.shape[0]
# ysize = a.shape[1]
#   
# classification_values = np.int32([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80])#The interval values to classify
# classification_output_values = np.int32([0, 5, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60, 65, 70, 75, 80])    
#   
# r = np.zeros((xsize, ysize), np.int32)
#   
# for k in range(len(classification_values) - 1):
#     if classification_values[k] < max_value and (classification_values[k + 1] > min_value ):  
#         r = r + classification_output_values[k] * np.logical_and(a >= classification_values[k], a < classification_values[k + 1])  
#     if classification_values[k + 1] < max_value:
#         r = r + classification_output_values[k] * (a >= classification_values[k + 1])  
#   
# img_d = Image.fromarray(r)
# Image._show(img_d)
# img_d.save(dest + country + str(266) + '.gif', transparency = 0)
#==============================================================================
 
class ol_osm(views.MethodView):
    def get(self):
        lon_min, lon_max, lat_min, lat_max, c_lat, c_lon, zoom = bounds(country)
        tamsat_img = t.read_img(enddate)
        img_d = Image.fromarray(tamsat_img[0].data)
        name = country + str(idxdates) + '.gif'
        img_d.save(dest + name, transparency = 0)
        return render_template('ol_osm_img.htm',
                               max=idxdates,
                               coord=[c_lon, c_lat],
                               zoom=zoom, # depends on map div width,
                               ex1=(lon_max, lat_min),
                               ex2=(lon_min, lat_max),
                               ovl="../static/" + name)

@app.route('/_pretty_date')
def pretty_date():
    idx = request.args.get('current', 0, type=int)
    min = request.args.get('min',0, type=int)
    max = request.args.get('max',idxdates, type=int)
    pretty = (dates[idx].strftime('%Y-%m-%d'))
    begin = (dates[min].strftime('%Y-%m-%d'))
    end = (dates[max - 1].strftime('%Y-%m-%d'))
    return jsonify(begin=begin, end=end, currentV=pretty)

@app.route('/_rdat')
def request_data():
    idx = request.args.get('current', 0, type=int)
    pidx = (dates[idx])
    if not os.path.isfile(dest + country + str(idx) + '.gif') == True:
        tamsat_img = t.read_img(pidx)
        img_d = Image.fromarray(tamsat_img[0].data)
        img_d.save(dest + country + str(idx) + '.gif', transparency = 0)
    path = '../static/' + country + str(idx) + '.gif'
    return jsonify(rdat=path)

if __name__ == '__main__':
    app.add_url_rule('/', view_func=ol_osm.as_view('main'),
                     methods=['GET', 'POST'])
    app.run(debug = True, use_debugger = True, use_reloader = True)