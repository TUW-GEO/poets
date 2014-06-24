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

'''
Created on 23.05.2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import os
import glob
import pandas as pd
import requests
import general.root_path as root
from datetime import date

date_begin = date(1983, 01, 01)
filename = 'rfe{YYYY}_{MM}-dk{P}.nc'

file_path = os.path.join(root.r, 'Datapool_raw', 'TAMSAT', 'datasets',
                         'TAMSAT_rfe_dekadal', '')


def _get_current_file(download_path, date_from, date_to):
    """
    helper method to get the date of the last downloaded file in the local
    repository. Changes the date_from value to the date of the latest local
    file if newer. Also sets the end-date of the download request if none given.

    Parameters
    ----------
    download_path : str
        Path where to the files in the local repository
    date_from : datetime.date
        Optional
    date_to : datetime.date
        Optional

    Returns
    -------
    date_from : datetime.date
        Begin date to download data
    date_to : datetime.date
        End date for data download
    """

    dirs = [x[0] for x in os.walk(download_path)]

    filelist = []

    if date_to == None:
        date_to = date.today()

    for sdir in dirs:
        files = glob.glob(os.path.join(sdir, '') + '*.nc')
        filelist = filelist + files

    if len(filelist) == 0:
        curdate = None
    else:
        filelist.sort()
        curfile = filelist[-1].split('/')[-1]
        year = int(curfile[3:7])
        month = int(curfile[8:10])
        dekad = int(curfile[13])
        day = dekad * 10 - 9
        curdate = date(year, month, day)

    if date_from == None:
        if curdate == None:
            date_from = date_begin
        else:
            day = int(curdate.day + 10)
            date_from = date(curdate.year, curdate.month, day)
    else:
        if date_from.day < 11:
            date_from = date(date_from.year, date_from.month, 1)
        elif date_from.day >= 11 and date_from.day < 21:
            date_from = date(date_from.year, date_from.month, 11)
        else:
            date_from = date(date_from.year, date_from.month, 21)

        if curdate != None:
            if date_from < curdate:
                date_from = curdate

    return date_from, date_to


def download(url, download_path=None, date_from=None, date_to=None):
    """
    Download latest TAMSAT RFE dekadal data

    Parameters
    ----------
    url : str
        URL to TAMSAT datapool
    download_path : str
        Path where to save the downloaded files.
    date_from : datetime.date
        Optional, set either to first date of remote repository or date of last
        file in local repository
    date_to : datetime.date
        Optional, set to today if none given
    """

    if url[-1] != '/':
        url += '/'

    if download_path == None:
        download_path = file_path

    date_from, date_to = _get_current_file(download_path, date_from, date_to)

    print('[INFO] downloading data from ' + str(date_from) + ' - '
          + str(date_to))

    # create daterange on monthly basis
    mon_from = date(date_from.year, date_from.month, 1)
    mon_to = date(date_to.year, date_to.month, 1)
    daterange = pd.date_range(start=mon_from, end=mon_to, freq='MS')

    # loop through daterange
    for i, dat in enumerate(daterange):
        year = str(dat.year)
        month = str("%02d" % (dat.month,))
        path = url + year + '/' + month + '/'
        fname = filename.replace('{YYYY}', year).replace('{MM}', month)

        # get dekad of first and last interval based on input dates
        if i == 0 and date_from.day > 1:
            if date_from.day < 11:
                dekads = [0, 1, 2]
            elif date_from.day >= 11 and date_from.day < 21:
                dekads = [1, 2]
            elif date_from.day == 21:
                dekads = [2]
        elif i == (len(daterange) - 1) and date_to.day < 21:
            if date_to.day < 11:
                dekads = [0]
            else:
                dekads = [0, 1]
        else:
            dekads = range(3)

        # loop through dekads
        for j in dekads:
            filepath = path + fname.replace('{P}', str(j + 1))
            r = requests.get(filepath)
            if r.status_code == 200:
                # check if year folder is existing
                dpath = os.path.join(download_path, str(year), str(month), '')
                if not os.path.exists(dpath):
                    print '[INFO] output path does not exist... creating path'
                    os.makedirs(dpath)

                # download file
                newfile = dpath + filepath.split('/')[-1]
                if not os.path.exists(newfile):
                    r = requests.get(filepath, stream=True)
                    with open(newfile, 'wb') as f:
                        f.write(r.content)
                        print '[INFO] downloading file ' + filepath
                else:
                    print('[INFO] file ' + filepath.split('/')[-1] + ' already'
                          ' exists - nothing to download')


if __name__ == '__main__':

    url = "http://www.met.reading.ac.uk/~tamsat/public_data"
    # date_from = date(1983, 01, 01)
    beginn = date(2014, 05, 02)
    end = date(2014, 5, 5)
    # download_path = os.path.join(root.d, 'TAMSAT', 'test_download', '')
    path = os.path.join('/home', 'thomas', 'Downloads', 'TAMSAT', '')

    # download(url, download_path, date_from, date_to)
    download(url, download_path=path, date_from=beginn)
