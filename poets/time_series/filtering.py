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

# Author: Isabella Pfeil
# Creation date: 2014-07-14

"""
This module provides functions for the monthly and seasonal grouping of
a daily time series.
It also provides a function for calculating the Centered Moving Average as in
    http://de.slideshare.net/AzzurieyAhmad/classical-decomposition?related=1
"""

import numpy as np
import pandas as pd
import datetime


def group_months(TS, attribute):
    """
    groups daily time series in years and months

    Parameters:
    ----------
    TS : pandas DataFrame
        time series
    attribute : string
        attribute, e.g. 'sm', 'data'
    """

    grp = pd.DataFrame(TS.as_matrix(), columns=TS.columns,
                       index=(TS.index.year * 100 + TS.index.month))
    df = grp.groupby(level=0)
    TS_mean = df.mean()
    indices = []

    # create corresponding datetime indices
    for i in range(0, len(TS_mean)):
        indices.append(datetime.date(year=TS_mean.index[i] / 100,
                                         month=TS_mean.index[i] % 100, day=01))

    dates = [indices[0]]

    if indices[0].month % 3 == 0:
        i = 3
    elif indices[0].month % 3 == 1:
        i = 2
    elif indices[0].month % 3 == 2:
        i = 1

    while i < len(indices):
        dates.append(indices[i])
        i += 3

    if indices[-1].month % 3 != 0:
        dates.append(indices[-1])

    TS = TS_mean[attribute]
    TS = pd.np.array(TS)
    return TS, dates


def group_seasons(TS, dates):
    """
    groups monthly time series in seasons:
        Winter: Dec, Jan, Feb
        Spring: Mar, Apr, May
        Summer: June, July, Aug
        Fall: Sep, Oct, Nov

    Parameters:
    -----------
    TS : np.array
        monthly time series
    dates : pandas DataFrame
    """

    TS_seas = []

    # check if time series starts with Mar, Jun, Sep or Dec - if not,
    # put redundant values to beginning/end of seasonal time series

    if dates[0].month % 3 == 0:
        lB1 = 0
    elif dates[0].month % 3 == 1:
        lB1 = 2
        TS_seas.append(np.mean((TS[0], TS[1])))
    elif dates[0].month % 3 == 2:
        lB1 = 1
        TS_seas.append(TS[0])

    if dates[-1].month % 3 == 2:
        lB3 = 0
    elif dates[-1].month % 3 == 0:
        lB3 = 1
    elif dates[-1].month % 3 == 1:
        lB3 = 2

    lB2 = len(TS) - lB1 - lB3

    for j in range(0, lB2 / 3):
        TS_seas.append(np.mean((TS[3 * j + lB1], TS[3 * j + 1 + lB1],
                                TS[3 * j + 2 + lB1])))

    if lB3 == 0:
        del(dates[-1])
    if lB3 == 1:
        TS_seas.append(TS[-1])
    if lB3 == 2:
        TS_seas.append(np.mean((TS[-1], TS[-2])))
        del(dates[-1])

    if len(dates) != len(TS_seas):
        print 'Dimension mismatch between data and indices'

    return TS_seas, dates


def ctrd_mov_avg(TS_seas):
    """
    calculates centered moving average from seasonal time series,
    window : 1 year (4 seasons)

    Parameters:
    -----------
    TS_seas : np.array
        seasonal time series
    """

    # compute moving average
    TS_movavg = []
    i = 0

    while i < (len(TS_seas) - 4):
        TS_movavg.append((TS_seas[i] + 2 * (TS_seas[i + 1] + TS_seas[i + 2]
                                      + TS_seas[i + 3]) + TS_seas[i + 4]) / 8)
        i = i + 1

    # compute centered moving average
    TS_ctrd = []
    i = 0
    while i < (len(TS_movavg) - 1):
        TS_ctrd.append((TS_movavg[i] + TS_movavg[i + 1]) / 2)
        i = i + 1

    return TS_ctrd

if __name__ == "__main__":
    pass
