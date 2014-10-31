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
# Creation date: 2014-08-04

import pandas as pd
import numpy as np
import operator
from poets.timedate.dekad import get_dekad_period


def calc_CDI(data, refparam=None, lags=[-10, 11]):
    """
    Calculates a weighted average over all columns of a pandas DataFrame.

    Parameters
    ----------
    data : pandas.DataFrame
        Pandas DataFrame containing data to be averaged.
    refparam : str, optional
        Reference parameter. If not set, parameters will be weighted equally.
    lags : list of int, optional
        Time periods to shift parameter against refparam,
        defaults to [-10, 11].

    Returns
    -------
    df : pandas DataFrame
        Return the average of data
    """

    cols = data.keys()
    dat = np.array(data[cols])
    dat = np.ma.masked_invalid(dat)

    weights = calc_weights(data, refparam, lags)

    if refparam is None:
        avg = np.ma.average(dat, axis=1)
    else:
        avg = np.ma.average(dat, axis=1, weights=weights)
    df = pd.DataFrame(avg, columns=['CDI'], index=data.index)

    return df


def calc_weights(data, refparam, lags=[-10, 11]):
    """
    Calculates the weights of parameters for weighted averaging. Weights are
    calculated using correlation and time shift of each parameter against the
    reference parameter. Parameters must be direct proportional to reference
    parameter!

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing data in columns.
    refparam : str
        Reference parameter.
    lags : list of int, optional
        Time periods to shift parameter against refparam,
        defaults to [-10, 11].

    Returns
    -------
    sorted_weights : list of int
        Weights associated with the parameters in data.
    """

    params = data.keys()

    maxlag = {}
    maxcorr = {}
    weights = {}
    sorted_weights = []

    correlations = calc_correlation(data, refparam, lags)

    for param in params:
        maxlag[param] = correlations[param]['lag']
        maxcorr[param] = correlations[param]['corr']

    sorted_lag = sorted(maxlag.iteritems(), key=operator.itemgetter(1))
    sorted_corr = sorted(maxcorr.iteritems(), key=operator.itemgetter(1))

    for item in sorted_lag:
        weights[item[0]] = (float(maxlag[item[0]]) /
                            sum(maxlag.values()) * 100)

    for item in sorted_corr:
        weights[item[0]] = ((weights[item[0]] +
                             (maxcorr[item[0]] / sum(maxcorr.values())) *
                             100) / 2)

    for param in params:
        sorted_weights.append(weights[param])

    return sorted_weights


def calc_correlation(data, refparam, lags=[-10, 11]):
    """
    Calculates the correlations between parameters and a reference parameter
    given as columns in a DataFrame.

    Parameters
    ----------
    data : pandas.DataFrame
        DataFrame containing data in columns.
    refparam : str
        Reference parameter.
    lags : list of int, optional
        Time periods to shift parameter against refparam,
        defaults to [-10, 11].

    Returns
    -------
    correlation : dict
        Dictionary containing correlations and max time lags.
    """

    correlation = {}

    for param in data.keys():
        correlation[param] = {'corr': None, 'lag': None}
        for i in range(lags[0], lags[1]):
            corr = data[refparam].corr(data[param].shift(periods=i),
                                    method='pearson')
            if correlation[param]['corr'] is None:
                correlation[param]['corr'] = corr
                correlation[param]['lag'] = i
            if abs(corr) > abs(correlation[param]['corr']):
                correlation[param]['corr'] = corr
                correlation[param]['lag'] = i
            if abs(corr) == abs(correlation[param]['corr']):
                if abs(i) < abs(correlation[param]['lag']):
                    correlation[param]['corr'] = corr
                    correlation[param]['lag'] = i

    return correlation


def calc_DI(data, parameter, interest_period=[6, 12, 24], scale_zero=False):
    """
    Calculates a Drought Index based on an algorithm developed by FAO SWALIM.

    Parameters
    ----------
    data : pandas.DataFrame
        input data
    parameter : str
        thematical parameter (precipitation, temperature, vegetation,
        soil moisture)
    interest_period : list of int, optional
        interest periods used to calculate drought index,
        defaults to [6, 12, 24]
    scale_zero : boolean, optional
        If True values will be shifted around zero, defaults to False.
    """

    ts_date = data.index
    variables = data.keys()
    data['period'] = get_dekad_period(ts_date)

    for var in variables:

        if parameter in ['precipitation', 'rainfall', 'rain']:
            data['modf'] = data[var] + 1
            del data[var]
        elif parameter == 'temperature':
            data['modf'] = ((data[var].max() + 1) - data[var])
            del data[var]
        else:
            data['modf'] = data[var]

        data['modf_avg'] = (data.groupby('period').modf
                            .transform(lambda x: x.mean()))

        # Excess
        # Dekads below long term average. If the statement is true the program
        # return 1
        data['exc'] = np.choose((data['modf_avg'] / data['modf']) >= 1, [0, 1])

        # Run length
        # Maximum number of successive dekads below long term average
        # precipitation
        rlen = lambda x: len(max((''.join(str(j) for j in map(int, x)))
                                 .split('0')))

        for ip in interest_period:
            data['rlen' + str(ip)] = pd.rolling_apply(data['exc'], ip, rlen,
                                                      ip)

            # get modified run length
            max_rlen = data['rlen' + str(ip)].max()
            data['rlen' + str(ip)] = (max_rlen + 1) - data['rlen' + str(ip)]

            # average run lenghts
            rlen_avg = (data.groupby('period').modf
                        .transform(lambda x: x.mean()))
            data['form' + str(ip)] = data['rlen' + str(ip)] / rlen_avg

            # sumip matrix
            # calculates sum of the values for each interest period
            sumip = lambda x: sum(x)
            data['sumip' + str(ip)] = pd.rolling_apply(data['modf'], ip, sumip,
                                                       ip)

            # average values for each interest period over all years
            sumip_avg = (data.groupby('period')['sumip' + str(ip)]
                         .transform(lambda x: x.mean()))
            data['nrl' + str(ip)] = data['sumip' + str(ip)] / sumip_avg

            # calculating PDI/TDI
            data['val' + str(ip)] = (data['nrl' + str(ip)] *
                                     np.sqrt(data['form' + str(ip)]))

            # scaled index
            dkey = var + '_DI_' + str(ip)
            data[dkey] = ((data['val' + str(ip)] - data['val' + str(ip)].min())
                          / (data['val' + str(ip)].max() -
                             data['val' + str(ip)].min()))

            if scale_zero:
                data[dkey] = data[dkey] - data[dkey].mean()

            del (data['val' + str(ip)], data['nrl' + str(ip)],
                 data['sumip' + str(ip)], data['rlen' + str(ip)],
                 data['form' + str(ip)])

        # deletes not further relevant columns
        del (data['period'], data['modf'], data['modf_avg'],
             data['exc'])

    return data

if __name__ == "__main__":
    params = ['A', 'B', 'C']

    data = pd.DataFrame(columns=params, index=range(0, 20))

    a = [1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5]
    b = [3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2, 3, 4, 5, 1, 2]
    c = [0, 3, 4, 5, 1, 2, 0, 4, 5, 1, 2, 3, 4, 4, 1, 2, 3, 2, 5, 1]

    data['A'] = a
    data['B'] = b
    data['C'] = c

    x = calc_CDI(data, 'A', [-5, 5])

    a = calc_DI(data, 'vegetation')

    data_di = pd.DataFrame(columns=params, index=range(0, 20))
    data_di['A_DI'] = calc_DI(a, 'vegetation')
    data_di['B_DI'] = calc_DI(b, 'soil moisture')
    data_di['C_DI'] = calc_DI(c, 'precipitation')

    y = calc_CDI(data_di, 'A', [-5, 5])

    pass
