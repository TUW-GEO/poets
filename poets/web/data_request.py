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
# Creation date: 2014-07-09

"""
Description of module.
"""

import numpy as np
import pandas as pd
from poets.io.TAMSAT.interface import TAMSAT
from poets.io.ECV.interface import ECV
from poets.grid.grids import CountryGrid


def to_dygraph_format(self):
    labels = ['date']
    labels.extend(self.columns.values.tolist())
    data_values = np.hsplit(self.values, self.columns.values.size)
    data_index = self.index.values.astype('M8[s]').tolist()
    data_index = [x.strftime("%Y/%m/%d %H:%M:%S") for x in data_index]
    data_index = np.reshape(data_index, (len(data_index), 1))
    data_values.insert(0, data_index)
    data_values = np.column_stack(data_values)

    return labels, data_values.tolist()

pd.DataFrame.to_dygraph_format = to_dygraph_format


def read_ts(gp, region=None, variable=None):

    tamsat = TAMSAT()
    dat = tamsat.read_ts(gp, region, variable)

    labels, values = dat.to_dygraph_format()
    ts = {'labels': labels, 'data': values}

    return ts


def get_gridpoints(region):

    grid = CountryGrid(region)
    gridpoints = grid.get_country_gridpoints()

    return gridpoints

if __name__ == "__main__":
    pass
