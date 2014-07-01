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
# Creation date: 2014-06-30

"""
Base Class for data sources.
"""

import os
import datetime


class Source(object):
    """
    Base Class for data sources.

    Parameters
    ----------
    source_path : string
        path to data source
    begin_date : datetime.date
        date, from which on data is available

    Attributes
    ----------
    """

    def __init__(self, source_path, begin_date, filename, dirstruct):
        """
        init method
        """

        self.source_path = source_path
        self.begin_date = begin_date
        self.filename = filename
        self.dirstruct = dirstruct

    def download(self):
        """
        Downloads data from source
        """

        # check path type:
        if ':' in self.source_path:
            prefix = self.source_path[:self.source_path.find(':')]
        else:
            if os.path.exists(self.source_path):
                prefix = 'local'

        return True

if __name__ == "__main__":

    url = "http://www.met.reading.ac.uk/~tamsat/public_data"
    # date_from = date(1983, 01, 01)
    begin = datetime.date(2014, 05, 02)
    filename = 'rfe{YYYY}_{MM}-dk{P}.nc'

    x = Source(url, begin, filename)
    x.download()

#===============================================================================
# if __name__ == "__main__":
#     pass
#===============================================================================
