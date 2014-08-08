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
# Creation date: 2014-08-06

import datetime
from poets.io.source_base import BasicSource


class SWI_Geoland(BasicSource):
    """Source Class for Geoland SWI data.

    Parameters
    ----------
    name : str
        Name of the data source
    filename : str
        Structure/convention of the file name
    filedate : dict
        Position of date fields in filename, given as tuple
    temp_res : str
        Temporal resolution of the source
    host : str
        Link to data host
    protocol : str
        Protocol for data transfer
    username : str, optional
        Username for data access
    password : str, optional
        Password for data access
    port : int, optional
        Port to data host, defaults to 22
    directory : str, optional
        Path to data on host
    dirstruct : list of strings
        Structure of source directory, each list item represents a subdirectory
    begin_date : datetime.date, optional
        Date from which on data is available, defaults to 2000-01-01
    variables : list of strings, optional
        Variables used from data source

    Attributes
    ----------
    name : str
        Name of the data source
    filename : str
        Structure/convention of the file name
    filedate : dict
        Position of date fields in filename, given as tuple
    temp_res : str
        Temporal resolution of the source
    host : str
        Link to data host
    protocol : str
        Protocol for data transfer
    username : str
        Username for data access
    password : str
        Password for data access
    port : int
        Port to data host
    directory : str
        Path to data on host
    dirstruct : list of strings
        Structure of source directory, each list item represents a subdirectory
    begin_date : datetime.date
        Date from which on data is available
    variables : list of strings
        Variables used from data source
    """

    def __init__(self, **kwargs):

        name = 'Geoland'
        filename = "g2_BIOPAR_SWI_{YYYY}{MM}{DD}0000_GLOBE_ASCAT_V2.0.0.zip"
        filedate = {'YYYY': (14, 18), 'MM': (18, 20), 'DD': (20, 22)}
        temp_res = 'daily'

        host = "catftp.vgt.vito.be"
        protocol = 'ftp'
        port = 21
        username = 'menenkel'
        password = 'satida2014'

        directory = 'S0014580'
        dirstruct = [directory]
        begin_date = datetime.datetime(2000, 01, 01)

        super(SWI_Geoland, self).__init__(name, filename, filedate,
                                          temp_res, host=host,
                                          protocol=protocol, port=port,
                                          username=username,
                                          password=password,
                                          directory=directory,
                                          dirstruct=dirstruct,
                                          begin_date=begin_date)
