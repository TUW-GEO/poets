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
from poets.timedate.dekad import get_dekad_period


def calc_CDI(data, weights=None):
    """
    Calculates a weighted average over all columns of a pandas DataFrame.

    Parameters
    ----------
    data : pandas.DataFrame
        Pandas DataFrame containing data to be averaged.
    weights : list of int, optional
        A list of weights associated with the values in data. Values will be
        weighted equally if not given.

    Returns
    -------
    df : pandas DataFrame
        Return the average of data
    """
    cols = data.keys()
    dat = np.array(data[cols])
    dat = np.ma.masked_invalid(dat)
    if weights is None:
        avg = np.ma.average(dat, axis=1)
    else:
        avg = np.ma.average(dat, axis=1, weights=weights)
    df = pd.DataFrame(avg, columns=['CDI'], index=data.index)

    return df


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
    scale_zero : boolean
        Time series is shifted
    """

    ts_date = data.index
    variables = data.keys()
    data['period'] = get_dekad_period(ts_date)

    for var in variables:

        if parameter == 'precipitation':
            data['modf'] = data[var] + 1
            del data[var]
        elif parameter == 'temperature':
            data['modf'] = ((data[var].max() + 1) - data[var])
            del data[var]
        else:
            data['modf'] = data[var]

        data['modf_avg'] = data.groupby('period').modf.transform(lambda x: x.mean())

        # Excess
        # Dekads below long term average. If the statement is true the program
        # return 1
        data['exc'] = np.choose((data['modf_avg'] / data['modf']) >= 1, [0, 1])

        # Run length
        # Maximum number of successive dekads below long term average
        # precipitation
        rlen = lambda x: len(max((''.join(str(j) for j in map(int, x))).split('0')))

        for ip in interest_period:
            data['rlen' + str(ip)] = pd.rolling_apply(data['exc'], ip, rlen,
                                                      ip)

            # get modified run length
            max_rlen = data['rlen' + str(ip)].max()
            data['rlen' + str(ip)] = (max_rlen + 1) - data['rlen' + str(ip)]

            # average run lenghts
            rlen_avg = data.groupby('period').modf.transform(lambda x: x.mean())
            data['form' + str(ip)] = data['rlen' + str(ip)] / rlen_avg

            # sumip matrix
            # calculates sum of the values for each interest period
            sumip = lambda x: sum(x)
            data['sumip' + str(ip)] = pd.rolling_apply(data['modf'], ip, sumip,
                                                       ip)

            # average values for each interest period over all years
            sumip_avg = data.groupby('period')['sumip' + str(ip)].transform(lambda x: x.mean())
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
    pass
