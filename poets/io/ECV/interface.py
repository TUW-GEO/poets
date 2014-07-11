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

# Author: Isabella Pfeil, isy.pfeil@gmx.at
# Creation date: 2014-07-09

import datetime
import os
from poets.settings import Settings
from poets.io.source_base import BasicSource
import paramiko


class ECV(BasicSource):
    """

    Source Class for ECV data.
    ftp.ipf.tuwien.ac.at

    Attributes
    ----------
    name : str
        Name of the data source
    source_path : str
        Link to data source
    filename : str
        Structure/convention of the file name
    dirstruct : list of strings
        Structure of source directory
        Each list item represents a subdirectory
    begin_date : datetime.date
        Date, from which on data is available
    variables : list of strings
        Variables used from data source
    """

    def __init__(self, **kwargs):

        name = 'ECV'
        source_path = "ftp.ipf.tuwien.ac.at/_down/daily_files/COMBINED"
        dirstruct = ['YYYY']
        filename = "ESACCI-SOILMOISTURE-L3S-SSMV-COMBINED-{YYYY}{MM}{TT}{hh}{mm}{ss}-fv02.0.nc"
        temp_res = 'daily'
        begin_date = datetime.date(1978, 11, 01)
        variables = ['sm']

        if source_path[-1] != '/':
            source_path += '/'

        super(ECV, self).__init__(name, source_path, filename, temp_res,
                                  dirstruct, begin_date, variables)

    def download(self, download_path=None, begin=None, end=None):

        """
        Download latest ECV dekadal data

        Parameters
        ----------
        download_path : str
            Path where to save the downloaded files.
        begin : datetime.date
            Optional, set either to first date of remote repository or date of
            last file in local repository
        end : datetime.date
            Entered in [years]. End year is not downloaded anymore.
            Optional, set to today if none given
        """


        if download_path == None:
            download_path = os.path.join(Settings.tmp_path, self.name)

        if not os.path.exists(download_path):
            print('[INFO] output path does not exist... creating path')
            os.makedirs(download_path)

        if begin == None:
            begin = self.begin_date

        if end == None:
            end = datetime.datetime.now()

        print('[INFO] downloading data from ' + str(begin) + ' - '
              + str(end) + '-12-31')

        remotepath = '/_down/daily_files/COMBINED/'
        localpath = download_path

        # connect to ftp server
        host = 'ftp.ipf.tuwien.ac.at'
        port = 22
        transport = paramiko.Transport((host, port))
        password = "FRT$_22"  # hard-coded
        username = "ecv_sm_v2"  # hard-coded
        transport.connect(username=username, password=password)

        sftp = paramiko.SFTPClient.from_transport(transport)

        # download files to temporary path
        for year in sftp.listdir(remotepath):
            if int(year) == end.year:
                break
            files = sftp.listdir(os.path.join(remotepath, str(year)))
            files.sort()
            for filename in files:
                if os.path.isfile(os.path.join(localpath, filename)) is False:
                    sftp.get(remotepath + str(year) + '/' + filename,
                             os.path.join(localpath, filename))
                    sftp.close


if __name__ == "__main__":
    pass
