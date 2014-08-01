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
import matplotlib.pyplot as plt
from USER_DEV.ipfeil.filtering import group_months, group_seasons, ctrd_mov_avg


def seasonal_indices(TS, lon, lat, attribute):
    """
    Deseasonalizing of a time series using normalized seasonal indices as in
        http://people.duke.edu/~rnau/411outbd.htm

    Parameters:
    ----------
    TS : pandas.DataFrame
        Time Series
    lon : float
        Longitude
    lat : float
        Latitude
    attribute : string
        attribute, e.g. 'sm', 'data'

    Returns:
    -------
    TS_seas_adj : pandas DataFrame
        seasonally adjusted time series
    """

    TS_months, dates = group_months(TS, attribute)
    TS_seas, dates = group_seasons(TS_months, dates)
    TS_ctrd = ctrd_mov_avg(TS_seas)

    count = 0

    for item in TS_ctrd:
        if item >= 0:
            count += 1

    if count < 4:  # data from < xx seasons
        print 'Not enough data.'
    else:

        TS_tmp = TS_seas[:]
        del TS_tmp[0]
        del TS_tmp[0]
        del TS_tmp[0]
        del TS_tmp[-1]
        del TS_tmp[-1]

        # seasonal component
        seas = np.subtract(TS_tmp, TS_ctrd)

        # ratio: TS_seas/TS_ctrd
        ratio = np.divide(TS_tmp, TS_ctrd)

        TS_ctrd = np.insert(TS_ctrd, 0, np.repeat(np.nan, 3))
        TS_ctrd = np.append(TS_ctrd, np.repeat(np.nan, 2))

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

        # TS_norm is shifted by 3 seasons compared to TS_seas
        index_norm2 = index_norm[1:]
        index_norm2.append(index_norm[0])
        index_norm = index_norm2[:]

        while len(index_norm) < len(TS_seas):
            for i in range(0, 4):
                index_norm.append(index_norm[i])
                if len(index_norm) == len(TS_seas):
                    break

        # Seasonal adjustment of the data
        TS_seas_adj = np.divide(TS_seas, index_norm)

        TS_seas = pd.DataFrame(TS_seas, index=dates)
        TS_ctrd = pd.DataFrame(TS_ctrd, index=dates)
        seas = pd.DataFrame(seas, index=dates)
        TS_seas_adj = pd.DataFrame(TS_seas_adj, index=dates)

        return TS_seas_adj


def zscore(TS, lon, lat, attribute):
    """
    Deseasonalizing of a time series using z-score as in
        http://www.jenvstat.org/v04/i11/paper (p. 2)

    Parameters:
    ----------
    TS : pandas.DataFrame
        Time Series
    lon : float
        Longitude
    lat : float
        Latitude
    attribute : string
        attribute, e.g. 'sm', 'data'

    Returns:
    -------
    TS_seas_adj : pandas DataFrame
        seasonally adjusted time series
    """

    TS_months, dates = group_months(TS, attribute)
    TS_seas, dates = group_seasons(TS_months, dates)

    count = 0

    for item in TS_seas:
        if item >= 0:
            count += 1

    if count < 4:  # data from < xx seasons
        print 'Not enough data.'
    else:

        # mean of entire time series
        mean_ts = []
        for i in range(0, len(TS_seas)):
            if TS_seas[i] >= 0:
                mean_ts.append(TS_seas[i])

        mean_ts = np.mean(mean_ts)

        # mean of each season
        des_m = []

        for m in range(1, 5):
            i = m - 1

            seas = []
            seas_nan = []

            while i < len(TS_seas):
                seas_nan.append(TS_seas[i])
                if TS_seas[i] >= 0:
                    seas.append(TS_seas[i])
                i = i + 4

            seas_m = np.mean(seas)

            des_m.append(seas_m)

        # compute deseasonalized time series
        years = len(TS_seas) / 4
        rest = len(TS_seas) % 4

        des_m = des_m * years
        for i in range(0, rest):
            des_m.append(des_m[i])

        TS_seas_adj = np.add(TS_seas, np.subtract(mean_ts, des_m))

        TS_seas = pd.DataFrame(TS_seas, index=dates)
        TS_seas_adj = pd.DataFrame(TS_seas_adj, index=dates)

        return TS_seas_adj


def plot_results(TS1, TS2, lon, lat, attribute):
    """
    plots results of two different deseasonalizing methods for comparison

    Parameters:
    ----------
    TS1 : pandas.Dataframe
        deseasonalized time series
    TS2 : pandas.Dataframe
        deseasonalized time series
    lon : float
        Longitude
    lat : float
        Latitude
    """

    plt.plot(TS1.index, TS1, 'b', label='method 1: seas. indices')
    plt.hold(True)
    plt.plot(TS2.index, TS2, 'r', label='method 2: z-score')
    plt.legend(loc='upper right')
    labels = plt.xticks()[1]
    plt.setp(labels, rotation=60)
    plt.suptitle('Deseasonalizing with different methods, Lon = ' + str(lon) +
                 ', Lat = ' + str(lat), fontsize=20)
    plt.ylabel(attribute)
    plt.show()

if __name__ == "__main__":
    pass
