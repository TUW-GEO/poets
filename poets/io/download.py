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
# Creation date: 2014-07-30

"""
Provides download functions for FTP/SFTP, HTTP and local data sources.
"""

import os
import datetime
import calendar
import requests
import paramiko
import pandas as pd
from ftplib import FTP


def download_ftp(download_path, host, remotepath, port, username, password,
                 filedate, dirstruct, begin, end=None):

    ftp = FTP(host)
    ftp.login(username, password)

    ftp.cwd(remotepath)
    subdirs = []

    ftp.retrlines("NLST", subdirs.append)  # NLIST retrieves filename only

    os.chdir(download_path)
    print '[INFO] downloading data from ' + str(begin) + ' to ' + str(end),

    if dirstruct[0] == 'YYYY':
        files = []
        for year in subdirs:
            filelist = []
            ftp.cwd(remotepath + year)
            ftp.retrlines("NLST", filelist.append)
            if len(dirstruct) == 2 and (dirstruct[1] == 'MM' or dirstruct[1] == 'M'):
                for month in filelist:
                    ftp.cwd(remotepath + year + '/' + month)
                    ftp.retrlines("NLST", files.append)
            else:
                files += filelist
    else:
        files = subdirs

    for fname in files:
        date = get_file_date(fname, filedate)
        if date >= begin and date <= end:
            ftp.retrbinary("RETR " + fname, open(fname, "wb").write)
            print '.',
    print ''

    return True


def download_sftp(download_path, host, remotepath, port, username, password,
                  filedate, dirstruct, begin, end=None):
    """Download data via SFTP

    Parameters
    ----------
    download_path : str, optional
        Path where to save the downloaded files.
    begin : datetime.date, optional
        Set either to first date of remote repository or date of
        last file in local repository
    end : datetime.date, optional
        Entered in [years]. End year is not downloaded anymore.
        Set to today if none given

    Returns
    -------
    bool
        true if data is available, false if not
    """

    if not os.path.exists(download_path):
        print('[INFO] output path does not exist... creating path')
        os.makedirs(download_path)

    if end == None:
        end = datetime.datetime.now()

    print '[INFO] downloading data from ' + str(begin) + ' - ' + str(end),

    localpath = download_path

    # connect to ftp server
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)

    sftp = paramiko.SFTPClient.from_transport(transport)

    subdirs = sftp.listdir(remotepath)

    files = []

    if dirstruct == ['YYYY']:
        if str(begin.year) not in subdirs:
            return False

        # download files to temporary path
        for year in subdirs:
            if str(begin.year) > year:
                continue
            if str(end.year) < year:
                continue
            subdir = remotepath + str(year) + '/'
            filelist = sftp.listdir(subdir)
            filelist.sort()
            for f in filelist:
                files.append(subdir + f)

    elif dirstruct == ['YYYY', 'MM'] or dirstruct == ['YYYY', 'M']:
        # download files to temporary path
        for year in subdirs:
            if begin.year > int(year):
                continue
            if end.year < int(year):
                continue
            for month in sftp.listdir(remotepath + str(year)):

                subdir = remotepath + str(year) + '/' + str(month) + '/'
                if begin.year == year:
                    if begin.month > int(month):
                        continue
                if end.year == year:
                    if end.month < int(month):
                        continue
                filelist = sftp.listdir(subdir)
                filelist.sort()
                for f in filelist:
                    files.append(subdir + f)

    for f in files:
        filename = os.path.basename(f)
        fdate = get_file_date(filename, filedate)
        if fdate >= begin and fdate <= end:
            print '.',
            if os.path.isfile(os.path.join(localpath, filename)) is False:
                sftp.get(f, os.path.join(localpath, filename))
                sftp.close

    sftp.close
    print ''
    return True


def download_http(download_path, source_path, filename, filedate, dirstruct,
                  begin, end=None):
    """Download data via HTTP

    Parameters
    ----------
    download_path : str, optional
        Path where to save the downloaded files.
    begin : datetime.date, optional
        set either to first date of remote repository or date of
        last file in local repository
    end : datetime.date, optional
        set to today if none given

    Returns
    -------
    bool
        true if data is available, false if not
    """

    if end == None:
        end = datetime.datetime.now()

    print('[INFO] downloading data from ' + str(begin) + ' - '
          + str(end)),

    # create daterange on monthly basis
    mon_from = datetime.date(begin.year, begin.month, 1)
    mon_to = datetime.date(end.year, end.month, 1)
    daterange = pd.date_range(start=mon_from, end=mon_to, freq='MS')

    if '{MM}' in filename:
        leading_month = True
    else:
        leading_month = False

    path = source_path

    # loop through daterange
    for i, dat in enumerate(daterange):
        year = str(dat.year)
        month = str("%02d" % (dat.month,))

        if dirstruct == ['YYYY']:
            path = source_path + year + '/'
        elif dirstruct == ['YYYY', 'MM']:
            path = source_path + year + '/' + month + '/'
        elif dirstruct == ['YYYY', 'M']:
            path = source_path + year + '/' + dat.month + '/'

        if leading_month == True:
            month = str("%02d" % (dat.month,))
            fname = filename.replace('{YYYY}', year).replace('{MM}', month)
        else:
            fname = filename.replace('{YYYY}', year).replace('{M}', month)

        files = []

        if '{P}' in filename:

            dekads = range(3)

            # get dekad of first and last interval based on input dates
            if i == 0 and begin.day > 1:
                if begin.day < 11:
                    dekads = [0, 1, 2]
                elif begin.day >= 11 and begin.day < 21:
                    dekads = [1, 2]
                elif begin.day == 21:
                    dekads = [2]
            elif i == (len(daterange) - 1) and end.day < 21:
                if end.day < 11:
                    dekads = [0]
                else:
                    dekads = [0, 1]

            # loop through dekads
            for j in dekads:
                filepath = path + fname.replace('{P}', str(j + 1))
                files.append(filepath)

        elif '{D}' in filename or '{DD}':

            if '{DD}' in filename:
                leading_day = True
            else:
                leading_day = False

            mr = calendar.monthrange(2014, 7)
            fday = mr[0]
            lday = mr[1] + 1

            if i == 0 and begin.day > 1:
                days = range(begin.day, lday)
            elif i == (len(daterange) - 1) and end.day < lday:
                days = range(fday, end.day + 1)
            else:
                days = range(fday, lday)

            # loop through dekads
            for j in days:
                if leading_day == True:
                    day = str("%02d" % (j))
                    filepath = path + fname.replace('{DD}', day)
                else:
                    filepath = path + fname.replace('{D}', str(j + 1))
                files.append(filepath)

        else:
            files.append(fname)

        for fp in files:
            newfile = os.path.join(download_path, fp.split('/')[-1])
            r = requests.get(fp)
            if r.status_code == 200:
                # check if year folder is existing
                if not os.path.exists(download_path):
                    print('[INFO] output path does not exist...'
                          'creating path')
                    os.makedirs(download_path)

                # download file
                newfile = os.path.join(download_path,
                                       fp.split('/')[-1])
                r = requests.get(fp, stream=True)
                with open(newfile, 'wb') as f:
                    f.write(r.content)
                    print '.',

    print ''
    return True


def get_file_date(fname, fdate):
    """Gets the date from a file name.

    Parameters
    ----------
    fname : str
    Filename

    Returns
    -------
    datetime.datetime
    Date and, if given, time from filename
    """

    fname = str(fname)

    if 'YYYY' in fdate.keys():
        year = int(fname[fdate['YYYY'][0]:
                         fdate['YYYY'][1]])

    if 'MM' in fdate.keys():
        month = int(fname[fdate['MM'][0]:fdate['MM'][1]])

    if 'DD' in fdate.keys():
        day = int(fname[fdate['DD'][0]:fdate['DD'][1]])
    else:
        day = 1

    if 'hh' in fdate.keys():
        hour = int(fname[fdate['hh'][0]:fdate['hh'][1]])
    else:
        hour = 0

    if 'mm' in fdate.keys():
        minute = int(fname[fdate['mm'][0]:fdate['mm'][1]])
    else:
        minute = 0

    if 'ss' in fdate.keys():
        second = int(fname[fdate['ss'][0]:fdate['ss'][1]])
    else:
        second = 0

    return datetime.datetime(year, month, day)

if __name__ == "__main__":
    pass
