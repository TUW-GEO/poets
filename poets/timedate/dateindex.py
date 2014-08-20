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

# Author: Thomas Mistelbauer thomas.mistelbauer@geo.tuwien.ac.at
# Creation date: 2014-05-27

import pandas as pd
from datetime import datetime
from poets.timedate.dekad import dekad_index


def get_dtindex(interval, begin, end=None):
    """Creates a pandas datetime index for a given interval.

    Parameters
    ----------
    interval : str or int
        Interval of the datetime index. Integer values will be treated as days.
    begin : datetime
        Datetime index start date.
    end : datetime, optional
        Datetime index end date, defaults to current date.

    Returns
    -------
    dtindex : pandas.tseries.index.DatetimeIndex
        Datetime index.
    """

    if end is None:
        end = datetime.now()

    if interval in ['dekad', 'dekadal', 'decadal', 'decade']:
        dtindex = dekad_index(begin, end)
    elif interval in ['daily', 'day', '1']:
        dtindex = pd.date_range(begin, end, freq='D')
    elif interval in ['weekly', 'week', '7']:
        dtindex = pd.date_range(begin, end, freq='7D')
    elif interval in ['monthly', 'month']:
        dtindex = pd.date_range(begin, end, freq='M')

    if type(interval) is int:
        dtindex = pd.date_range(begin, end, freq=str(str(interval) + 'D'))

    return dtindex
