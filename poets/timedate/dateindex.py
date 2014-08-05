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
Created on May 27, 2014

@author: Thomas Mistelbauer Thomas.Mistelbauer@geo.tuwien.ac.at
'''

import pandas as pd
from poets.timedate.dekad import dekad_index


def get_dtindex(interval, begin, end=None):
    """Creates a pandas datetime index.

    Datetime index is based on the temporal resolution given in the settings
    file

    Parameters
    ----------
    interval : str, int
        interval of the datetime index
    begin : datetime.date
        datetime index start date
    end : datetime.date, optional
        datetime index end date, set to current date if None

    Returns
    -------
    dtindex : pandas.tseries.index.DatetimeIndex
        datetime index
    """

    if interval in ['dekad', 'dekadal', 'decadal', 'decade']:
        dtindex = dekad_index(begin, end)
    elif interval in ['daily', 'day', '1']:
        dtindex = pd.date_range(begin, end, freq='D')
    elif interval in ['weekly', 'week', '7']:
        dtindex = pd.date_range(begin, end, freq='7D')
    elif interval in ['monthly', 'month']:
        dtindex = pd.date_range(begin, end, freq='M')

    if type(interval) is int:
        dtindex = pd.date_range(begin, end, str(interval + 'D'))

    return dtindex
