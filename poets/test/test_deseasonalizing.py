'''
Created on Jul 18, 2014

@author: pydev
'''
import unittest
from poets.time_series.filtering import group_months, group_seasons, ctrd_mov_avg
from poets.time_series.deseasonalizing import seasonal_indices
from poets.time_series.deseasonalizing import zscore
import pandas as pd
from datetime import datetime
import os


def curpath():
    pth, _ = os.path.split(os.path.abspath(__file__))
    return pth


class Test(unittest.TestCase):

    def setUp(self):
        # read WACMOS soil moisture time series for lon=15, lat=10
        self.testfilename = os.path.join(curpath(), 'data', 'ts_sm.csv')
        self.ts = pd.read_csv(self.testfilename, index_col=0)
        ts2 = []
        for ind in range(0, len(self.ts.index)):
            ts2.append(datetime.strptime(self.ts.index[ind], '%Y-%m-%d'))
        self.ts.index = ts2
        self.attribute = 'sm'

    def tearDown(self):
        pass

    def test_group_months(self):
        len_ts_mon = 396
        lenDates = 133

        ts_mon = len(group_months(self.ts, self.attribute)[0])
        ts_dat = len(group_months(self.ts, self.attribute)[1])

        assert len_ts_mon == ts_mon
        assert lenDates == ts_dat

    def test_group_seasons(self):
        len_ts_seas = 133
        lenDates = 133

        ts_months, dates = group_months(self.ts, self.attribute)

        ts_seas = len(group_seasons(ts_months, dates)[0])
        ts_dat = len(group_seasons(ts_months, dates)[1])

        assert len_ts_seas == ts_seas
        assert lenDates == ts_dat

    def test_ctrd_mov_avg(self):
        len_ts_ctrd = 128
        ts_months, dates = group_months(self.ts, self.attribute)
        ts_seas, _ = group_seasons(ts_months, dates)
        ts_ctrd = len(ctrd_mov_avg(ts_seas))

        assert len_ts_ctrd == ts_ctrd

    def test_seasonal_indices(self):
        len_ts_des = 133

        ts_des = len(seasonal_indices(self.ts, self.attribute))

        assert len_ts_des == ts_des

    def test_zscore(self):
        len_ts_des = 133

        ts_des = len(zscore(self.ts, self.attribute))

        assert len_ts_des == ts_des


if __name__ == "__main__":
    # import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
