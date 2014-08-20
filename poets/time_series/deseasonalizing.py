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
# Creation date: 2014-07-11

"""
This module provides different methods to do a seasonal detrending of
a time series.
"""

import numpy as np
import pandas as pd
from poets.time_series.filtering import group_months, group_seasons, ctrd_mov_avg


def seasonal_indices(ts, attribute):
    """
    Deseasonalizing of a time series using normalized seasonal indices as in
        http://people.duke.edu/~rnau/411outbd.htm

    Parameters:
    ----------
    ts : pandas.DataFrame
        Time Series
    attribute : string
        attribute, e.g. 'sm', 'data'

    Returns:
    -------
    ts_seas_adj : pandas DataFrame
        seasonally adjusted time series
    """

    ts_months, dates = group_months(ts, attribute)
    ts_seas, dates = group_seasons(ts_months, dates)
    ts_ctrd = ctrd_mov_avg(ts_seas)

    count = 0

    for item in ts_ctrd:
        if item >= 0:
            count += 1

    if count < 4:  # data from < xx seasons
        print 'Not enough data.'
    else:

        ts_tmp = ts_seas[:]
        del ts_tmp[0]
        del ts_tmp[0]
        del ts_tmp[0]
        del ts_tmp[-1]
        del ts_tmp[-1]

        # seasonal component
        seas = np.subtract(ts_tmp, ts_ctrd)

        # ratio: ts_seas/ts_ctrd
        ratio = np.divide(ts_tmp, ts_ctrd)

        ts_ctrd = np.insert(ts_ctrd, 0, np.repeat(np.nan, 3))
        ts_ctrd = np.append(ts_ctrd, np.repeat(np.nan, 2))

        seas = np.insert(seas, 0, np.repeat(np.nan, 3))
        seas = np.append(seas, np.repeat(np.nan, 2))

        # unnormalized seasonal index
        index_unnorm = []

        for j in range(0, 4):
            i = j
            index_month = []
            while i < len(ratio):
                if ratio[i] >= 0:
                    index_month.append(ratio[i])
                i = i + 4  # get all june/sept/dec/march values in a list

            index_unnorm.append(np.average(index_month))

        # normalized seasonal index
        index_norm = np.multiply(index_unnorm, 4) / np.sum(index_unnorm)
        index_norm = index_norm.tolist()

        # ts_norm is shifted by 3 seasons compared to ts_seas
        index_norm2 = index_norm[1:]
        index_norm2.append(index_norm[0])
        index_norm = index_norm2[:]

        while len(index_norm) < len(ts_seas):
            for i in range(0, 4):
                index_norm.append(index_norm[i])
                if len(index_norm) == len(ts_seas):
                    break

        # Seasonal adjustment of the data
        ts_seas_adj = np.divide(ts_seas, index_norm)

        ts_seas = pd.DataFrame(ts_seas, index=dates)
        ts_ctrd = pd.DataFrame(ts_ctrd, index=dates)
        seas = pd.DataFrame(seas, index=dates)
        ts_seas_adj = pd.DataFrame(ts_seas_adj, index=dates,
                                   columns=[attribute + '_seasadj'])

        return ts_seas_adj


def zscore(ts, attribute):
    """
    Deseasonalizing of a time series using z-score as in
        http://www.jenvstat.org/v04/i11/paper (p. 2)

    Parameters:
    ----------
    ts : pandas.DataFrame
        Time Series
    attribute : string
        attribute, e.g. 'sm', 'data'

    Returns:
    -------
    ts_seas_adj : pandas DataFrame
        seasonally adjusted time series
    """

    ts_months, dates = group_months(ts, attribute)
    ts_seas, dates = group_seasons(ts_months, dates)

    count = 0

    for item in ts_seas:
        if item >= 0:
            count += 1

    if count < 4:  # data from < xx seasons
        print 'Not enough data.'
    else:

        # mean of entire time series
        mean_ts = []
        for i in range(0, len(ts_seas)):
            if ts_seas[i] >= 0:
                mean_ts.append(ts_seas[i])

        mean_ts = np.mean(mean_ts)

        # mean of each season
        des_m = []

        for m in range(1, 5):
            i = m - 1

            seas = []
            seas_nan = []

            while i < len(ts_seas):
                seas_nan.append(ts_seas[i])
                if ts_seas[i] >= 0:
                    seas.append(ts_seas[i])
                i = i + 4

            seas_m = np.mean(seas)

            des_m.append(seas_m)

        # compute deseasonalized time series
        years = len(ts_seas) / 4
        rest = len(ts_seas) % 4

        des_m = des_m * years
        for i in range(0, rest):
            des_m.append(des_m[i])

        ts_seas_adj = np.add(ts_seas, np.subtract(mean_ts, des_m))

        ts_seas = pd.DataFrame(ts_seas, index=dates)
        ts_seas_adj = pd.DataFrame(ts_seas_adj, index=dates,
                                   columns=[attribute + '_zscore'])

        return ts_seas_adj


if __name__ == "__main__":
    pass
