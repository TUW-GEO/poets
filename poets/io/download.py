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
# Creation date: 2014-07-30

"""
Provides download functions for FTP/SFTP, HTTP and local data sources.
"""
import calendar
from datetime import datetime
from ftplib import FTP, socket
import os
import shutil
import paramiko
import requests
import pandas as pd
from poets.timedate.dekad import dekad2day, runningdekad2date
from requests.exceptions import ConnectionError, Timeout


def download_ftp(download_path, host, directory, filedate, port=21,
                 username='', password='', dirstruct=None, ffilter='',
                 begin=None, end=None):
    """Downloads data via FTP.

    Parameters
    ----------
    download_path : str, optional
        Path where to save the downloaded files.
    host : str
        Link to host.
    directory : str
        Path to data on host.
    filedate : dict
        Dict which points to the date fields in the filename
    port : int, optional
        Port to host, defaults to 21.
    username : str, optional
        Username for source, defaults to emtpy str.
    password : str, optional
        Passwor for source, defaults to emtpy str.
    dirstruct : list of str, optional
        Folder structure on host, each list element represents a subdirectory.
    ffilter : str, optional
        Used for filtering files on a server, defaults to emtpy str.
    begin : datetime, optional
        Set either to first date of remote repository or date of last file in
        local repository.
    end : datetime, optional
        Date until which data should be downloaded.

    Returns
    -------
    bool
        True if data is available, False if not.
    """

    if begin is None:
        begin = datetime(1900, 1, 1)

    if end is None:
        end = datetime.now()

    if host[-1] == '/':
        host = host[:-1]

    try:
        ftp = FTP(host)
    except:
        print ''
        print '[ERROR] Cannot connect to source. Please contact data provider.'
        return False

    try:
        ftp.login(username, password)
    except:
        print ''
        print '[ERROR] Cannot login at source - wrong login credentials.'
        return False

    try:
        ftp.cwd(directory)
    except:
        print ''
        print '[ERROR] Directory not found on host!'
        return False

    subdirs = []

    ftp.retrlines("NLST", subdirs.append)  # NLIST retrieves filename only

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    os.chdir(download_path)
    print '[INFO] downloading data from ' + str(begin) + ' to ' + str(end),

    files = []

    if dirstruct is not None and len(dirstruct) > 0 and dirstruct[0] == 'YYYY':
        for year in subdirs:
            if begin.year > int(year):
                continue
            if end.year < int(year):
                continue
            year_filelist = []
            ftp.cwd(directory + year)
            ftp.retrlines("NLST", year_filelist.append)
            if len(dirstruct) == 2 and dirstruct[1] == ['MM', 'M']:
                mon_filelist = []
                for month in year_filelist:
                    if begin.year == int(year):
                        if begin.month > int(month):
                            continue
                    if end.year == int(year):
                        if end.month < int(month):
                            continue
                    ftp.cwd(directory + year + '/' + month)
                    ftp.retrlines("NLST", mon_filelist.append)
                files += mon_filelist
            else:
                files += year_filelist
    else:
        files = filesInDir_ftp(directory, ftp, filedate, begin, end, files)
        if files is False:
            print '[ERROR] Connection timed out, skipping source.'
            return False

    ftp.cwd(directory)
    if len(files) > 0:
        for fname in files:
            fname2 = fname.split('/')[-1]
            if not os.path.exists(os.path.join(download_path, fname2)):
                if ffilter is None or ffilter in fname2:
                    loc = '/'.join(fname.split('/')[:-1])
                    try:
                        ftp.cwd(loc)
                        ftp.retrbinary("RETR " + fname2,
                                       open(fname2, "wb").write)
                        print '.',
                    except:
                        print ''
                        print '[WARNING] Connection timed out, retrying...'
                        try:
                            ftp.close()
                            ftp = FTP(host)
                            ftp.login(username, password)
                            ftp.cwd(directory)
                            ftp.cwd(loc)
                            ftp.retrbinary("RETR " + fname2,
                                           open(fname2, "wb").write)
                            print '.',
                        except:
                            '[ERROR] Retry not successful, skipping download.'
                            return False
        ftp.close()
        print ''
        return True
    else:
        ftp.close()
        print ''
        return False

    return True


def download_sftp(download_path, host, directory, port, username, password,
                  filedate, dirstruct=None, ffilter='',
                  begin=None, end=None):
    """Download data via SFTP.

    Parameters
    ----------
    download_path : str, optional
        Path where to save the downloaded files.
    host : str
        Link to host.
    directory : str
        Path to data on host.
    port : int
        Port to host.
    username : str
        Username for source.
    password : str
        Password for source.
    filedate : dict
        Dict which points to the date fields in the filename.
    dirstruct : list of str, optional
        Folder structure on host, each list element represents a subdirectory.
    ffilter : str, optional
        Used for filtering files on a server, defaults to emtpy str.
    begin : datetime, optional
        Set either to first date of remote repository or date of last file in
        local repository.
    end : datetime, optional
        Date until which data should be downloaded.

    Returns
    -------
    bool
        True if data is available, false if not.
    """

    if begin is None:
        begin = datetime(1900, 1, 1)

    if end is None:
        end = datetime.now()

    if not os.path.exists(download_path):
        print('[INFO] output path does not exist... creating path')
        os.makedirs(download_path)

    print '[INFO] downloading data from ' + str(begin) + ' - ' + str(end),

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    localpath = download_path

    # connect to ftp server
    if host[-1] == '/':
        host = host[:-1]

    try:
        transport = paramiko.Transport((host, port))
    except paramiko.ssh_exception.SSHException:
        print ''
        print '[ERROR] Cannot connect to source. Please contact data provider.'
        return False

    try:
        transport.connect(username=username, password=password)
        sftp = paramiko.SFTPClient.from_transport(transport)
    except:
        print ''
        print '[ERROR] Cannot login at source.'
        return False

    try:
        subdirs = sftp.listdir(directory)
    except:
        print ''
        print '[ERROR] Directory not found on host!'
        return False

    files = []

    if dirstruct is not None and len(dirstruct) > 0 and dirstruct[0] == 'YYYY':
        for year in subdirs:
            if begin.year > int(year):
                continue
            if end.year < int(year):
                continue
            year_subdir = directory + str(year) + '/'
            year_filelist = sftp.listdir(year_subdir)
            year_filelist.sort()
            if len(dirstruct) == 1:
                for f in year_filelist:
                    files.append(year_subdir + f)
            elif len(dirstruct) > 1 and dirstruct[1] in ['MM', 'M']:
                for month in year_filelist:
                    if begin.year == int(year):
                        if begin.month > int(month):
                            continue
                    if end.year == int(year):
                        if end.month < int(month):
                            continue
                    mon_subdir = year_subdir + month + '/'
                    mon_filelist = sftp.listdir(mon_subdir)
                    mon_filelist.sort()
                    if len(dirstruct) == 2:
                        for f in mon_filelist:
                            files.append(mon_subdir + f)
                    elif dirstruct[2] in ['DD', 'D']:
                        for day in mon_filelist:
                            if begin.year == int(year):
                                if begin.month == int(month):
                                    if begin.day > int(day):
                                        continue
                            if end.year == int(year):
                                if begin.month == int(month):
                                    if end.day < int(day):
                                        continue
                            day_subdir = mon_subdir + day + '/'
                            day_filelist = sftp.listdir(day_subdir)
                            day_filelist.sort()
                            if len(dirstruct) == 2:
                                for f in day_filelist:
                                    files.append(day_subdir + f)
    else:
        files = filesInDir_sftp(directory, sftp, filedate, begin, end, files)

    if len(files) > 0:
        for f in files:
            filename = os.path.basename(f)
            fdate = get_file_date(filename, filedate)
            if fdate >= begin and fdate <= end:
                if ffilter is not None and ffilter not in f:
                    continue
                print '.',
                if os.path.isfile(os.path.join(localpath, filename)) is False:
                    try:
                        sftp.get(f, os.path.join(localpath, filename))
                    except:
                        print ''
                        print '[WARNING] Connection timed out, retrying...'
                        try:
                            sftp.close
                            transport = paramiko.Transport((host, port))
                            transport.connect(username=username,
                                              password=password)
                            sftp = (paramiko.SFTPClient
                                    .from_transport(transport))
                            sftp.get(f, os.path.join(localpath, filename))
                        except:
                            '[ERROR] Retry not successful, skipping download.'
                            return False
        sftp.close
        print ''
        return True
    else:
        sftp.close
        print ''
        return False


def download_http(download_path, host, directory, filename, filedate,
                  dirstruct, ffilter=None, begin=None,
                  end=datetime.now()):
    """Download data via HTTP

    Parameters
    ----------
    download_path : str, optional
        Path where to save the downloaded files.
    host : str
        Link to host.
    directory : str
        Path to data on host.
    filename : str
        Structure/convention of the file name.
    filedate : dict
        Dict which points to the date fields in the filename.
    dirstruct : list of str
        Folder structure on host, each list element represents a subdirectory.
    ffilter : str, optional
        Used for filtering files on a server, defaults to None.
    begin : datetime, optional
        Set either to first date of remote repository or date of last file in
        local repository.
    end : datetime, optional
        Date until which data should be downloaded.

    Returns
    -------
    bool
        true if data is available, false if not
    """

    if begin is None:
        begin = datetime(1900, 1, 1)

    if end is None:
        end = datetime.now()

    print('[INFO] downloading data from ' + str(begin) + ' - '
          + str(end)),

    # create daterange on monthly basis
    mon_from = datetime(begin.year, begin.month, 1)
    mon_to = datetime(end.year, end.month, 1)
    daterange = pd.date_range(start=mon_from, end=mon_to, freq='MS')

    if '{MM}' in filename:
        leading_month = True
    else:
        leading_month = False

    path = host + directory

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    # loop through daterange
    for i, dat in enumerate(daterange):
        year = str(dat.year)
        month = str("%02d" % (dat.month,))

        if dirstruct is not None and dirstruct == ['YYYY']:
            path = host + directory + year + '/'
        elif dirstruct == ['YYYY', 'MM']:
            path = host + directory + year + '/' + month + '/'
        elif dirstruct == ['YYYY', 'M']:
            path = host + directory + year + '/' + dat.month + '/'
        else:
            path = host + directory  # + subdirectories!

        if leading_month is True:
            month = str("%02d" % (dat.month,))
            fname = filename.replace('{YYYY}', year).replace('{MM}', month)
        else:
            fname = filename.replace('{YYYY}', year).replace('{M}', month)

        files = []

        if '{P}' in filename:

            dekads = range(3)

            # get dekad of first and last interval based on input dates
            if begin.year == end.year and begin.month == end.month:
                if begin.day < 11:
                    if end.day > 10:
                        if end.day > 20:
                            dekads = range(3)
                        else:
                            dekads = [0, 1]
                    else:
                        dekads = [0]
                elif begin.day > 10 and begin.day < 21:
                    if end.day < 21:
                        dekads = [1]
                    elif end.day > 20:
                        dekads = [1, 2]
                else:
                    dekads = [2]
            else:
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
                if leading_day is True:
                    day = str("%02d" % (j))
                    filepath = path + fname.replace('{DD}', day)
                else:
                    filepath = path + fname.replace('{D}', str(j + 1))
                files.append(filepath)

        else:
            files.append(fname)

        for fp in files:
            newfile = os.path.join(download_path, fp.split('/')[-1])
            if os.path.exists(newfile):
                continue

            try:
                r = requests.get(fp, timeout=20.)
            except ConnectionError:
                print ''
                print '[WARNING] File not available at resource, skipping...'
                continue
            except Timeout:
                print ''
                print '[WARNING] File not available at resource, skipping...'
                continue

            if r.status_code == 200:
                # check if year folder is existing
                if ffilter is None or ffilter in os.path.split(fp)[-1]:
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

    if len(files) > 0:
        print ''
        return True
    else:
        print ''
        return False


def download_local(download_path, directory, filedate, dirstruct=None,
                   ffilter='', begin=datetime(1900, 1, 1), end=datetime.now()):
    """Download data from local path

    Parameters
    ----------
    download_path : str
        Path where to save the downloaded files.
    directory : str
        Path to locally stored data.
    filedate : dict
        Dict which points to the date fields in the filename.
    dirstruct : list of str, optional
        Folder structure in directory, each list element represents
        a subdirectory.
    ffilter : str, optional
        Used for filtering files on a server, defaults to empty string.
    begin : datetime, optional
        Set either to first date of remote repository or date of last file in
        local repository, defaults to datetime(1900, 1, 1).
    end : datetime, optional
        Date until which data should be downloaded, defaults to datetime.now()

    Returns
    -------
    bool
        True if data is available, false if not.
    """

    if not os.path.exists(download_path):
        os.makedirs(download_path)

    files = []

    print '[INFO] downloading data from ' + str(begin) + ' to ' + str(end),

    # directory/folder (len(dirstruct) == 1)
    if dirstruct is not None and len(dirstruct) == 1:
        folders = os.listdir(directory)
        for folder in folders:
            filelist = os.listdir(os.path.join(directory, folder))
            for fname in sorted(filelist):
                date = get_file_date(fname, filedate)
                if date >= begin and date <= end:
                    files.append(fname)
                    if not os.path.exists(os.path.join(download_path,
                                                       fname)):
                        shutil.copy(os.path.join(directory, folder, fname),
                                    os.path.join(download_path, fname))

    # directory/folder/subfolder (len(dirstruct) == 2)
    elif dirstruct is not None and len(dirstruct) == 2:
        folders = os.listdir(directory)
        for folder in folders:
            subfolders = os.listdir(os.path.join(directory, folder))
            for subfolder in subfolders:
                filelist = os.listdir(os.path.join(directory, folder,
                                                   subfolder))
                for fname in sorted(filelist):
                    if date >= begin and date <= end:
                        files.append(fname)
                        if not os.path.exists(os.path.join(download_path,
                                                           fname)):
                            shutil.copy(os.path.join(directory, folder,
                                                     subfolder, fname),
                                        os.path.join(download_path, fname))

    # general case: unknown folder structure
    if dirstruct is None:
        for path, _, filelist in os.walk(directory):
            for fname in filelist:
                if ffilter is None or ffilter in fname:
                    date = get_file_date(fname, filedate)
                    if date >= begin and date <= end:
                        files.append(fname)
                        if not os.path.exists(os.path.join(download_path,
                                                           fname)):
                            shutil.copy(os.path.join(path, fname),
                                        os.path.join(download_path, fname))

    if len(files) > 0:
        print ''
        return True
    else:
        print ''
        return False


def get_file_date(fname, fdate):
    """Gets the date from a file name.

    Parameters
    ----------
    fname : str
        Filename.
    fdate : str
        Structure of the date in filename, dict which points to the date fields
        in the filename.

    Returns
    -------
    datetime
        Date and, if given, time from filename
    """

    fname = str(fname)

    if 'YYYY' in fdate.keys():
        year = int(fname[fdate['YYYY'][0]:fdate['YYYY'][1]])

    if 'MM' in fdate.keys():
        month = int(fname[fdate['MM'][0]:fdate['MM'][1]])

    if 'DD' in fdate.keys():
        day = int(fname[fdate['DD'][0]:fdate['DD'][1]])
    else:
        day = 1

    if 'P' in fdate.keys():
        dekad = int(fname[fdate['P'][0]:fdate['P'][1]])
        day = dekad2day(year, month, dekad)

    if 'RP' in fdate.keys():
        dat = runningdekad2date(year,
                                int(fname[fdate['RP'][0]:fdate['RP'][1]]))
        month = dat.month
        day = dat.day

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

    return datetime(year, month, day, hour, minute, second)


def filesInDir_sftp(path, sftp, filedate, begin, end, filelist):
    """List all files in directory and subdirectories on an SFTP server.

    Parameters
    ----------
    path : str
        Path to data on host.
    sftp : paramiko Transport
        Connection to Server.
    filedate : dict
        Dict which points to the date fields in the filename.
    begin : datetime,
        Date from which on to download data.
    end : datetime
        Date until which to download data.
    filelist : list of str
        List of filepaths or empty list.

    Returns
    -------
    filelist : list
        List containing all files in directory and subdirectories
    """

    files = sorted(sftp.listdir(path))

    for fname in files:
        lstatout = str(sftp.lstat(os.path.join(path, fname))).split()[0]
        if 'd' not in lstatout:  # fname is file
            date = get_file_date(fname, filedate)
            if date >= begin and date <= end:
                filelist.append(path + fname)
        elif 'd' in lstatout:  # fname is dir
            filelist = filesInDir_sftp(path + fname + '/', sftp, filedate,
                                       begin, end, filelist)

    return filelist


def filesInDir_ftp(path, ftp, filedate, begin, end, filelist):
    """List all files in directory and subdirectories on an FTP server.

    Parameters
    ----------
    path : str
        Path to data on host.
    ftp : ftplib connection
        Connection to Server.
    filedate : dict
        Dict which points to the date fields in the filename.
    begin : datetime,
        Date from which on to download data.
    end : datetime
        Date until which to download data.
    filelist : list of str
        List of filepaths or empty list.

    Returns
    -------
    filelist : list
        List containing all files in directory and subdirectories
    """

    files = []
    ftp.cwd(path)
    try:
        ftp.retrlines('NLST', files.append)
    except socket.error:
        return False

    stats = []
    ftp.retrlines("LIST", stats.append)

    for idx, fname in enumerate(files):
        lstatout = stats[idx].split()[0]
        if 'd' not in lstatout:  # fname is file
            date = get_file_date(fname, filedate)
            if date >= begin and date <= end:
                filelist.append(path + fname)
        elif 'd' in lstatout:  # fname is dir
            filelist = filesInDir_ftp(path + fname + '/', ftp, filedate,
                                      begin, end, filelist)

    return filelist
