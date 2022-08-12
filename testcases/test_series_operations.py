# -*- coding: utf-8 -*-

"""
This file is part of datamatrix.

datamatrix is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

datamatrix is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with datamatrix.  If not, see <http://www.gnu.org/licenses/>.
"""

import pytest
from datamatrix.py3compat import *
from datamatrix import DataMatrix, SeriesColumn, series, NAN, INF
from testcases.test_tools import check_col, check_series, check_integrity
import numpy as np


def test_occurrence():
    
    dm = DataMatrix(length=3)
    dm.s = SeriesColumn(depth=4)
    dm.s[0] = 1,   NAN, NAN, INF
    dm.s[1] = 0,   INF, INF, 4
    dm.s[2] = NAN, 1,   3,   1
    check_col(series.first_occurrence(dm.s, NAN), [1, NAN, 0])
    check_col(series.last_occurrence(dm.s, NAN), [2, NAN, 0])
    check_col(series.first_occurrence(dm.s, NAN, equal=False), [0, 0, 1])
    check_col(series.last_occurrence(dm.s, NAN, equal=False), [3, 3, 3])
    check_col(series.first_occurrence(dm.s, INF), [3, 1, NAN])
    check_col(series.last_occurrence(dm.s, INF), [3, 2, NAN])
    check_col(series.first_occurrence(dm.s, INF, equal=False), [0, 0, 0])
    check_col(series.last_occurrence(dm.s, INF, equal=False), [2, 3, 3])
    check_col(series.first_occurrence(dm.s, 1), [0, NAN, 1])
    check_col(series.last_occurrence(dm.s, 1), [0, NAN, 3])
    check_col(series.first_occurrence(dm.s, 1, equal=False), [1, 0, 0])
    check_col(series.last_occurrence(dm.s, 1, equal=False), [3, 3, 2])


def test_nancount():
    dm = DataMatrix(length=2)
    dm.col1 = 'a', NAN
    dm.col2 = int
    dm.col2 = 1, 2
    dm.col3 = float
    dm.col3 = 1, NAN
    dm.s = SeriesColumn(depth=3)
    dm.s[0] = 1,NAN,NAN
    dm.s[1] = 1,INF,3
    a = np.ones(3)
    a[:2] = NAN
    assert series.nancount(dm.col1) == 1
    assert series.nancount(dm.col2) == 0
    assert series.nancount(dm.col3) == 1
    assert series.nancount(a) == 2
    check_col(series.nancount(dm.s), [2, 0])


def test_infcount():
    dm = DataMatrix(length=2)
    dm.col1 = 'a', INF
    dm.col2 = int
    dm.col2 = 1, 2
    dm.col3 = float
    dm.col3 = NAN, INF
    dm.s = SeriesColumn(depth=3)
    dm.s[0] = 1,NAN,NAN
    dm.s[1] = 1,INF,3
    a = np.ones(3)
    a[:2] = INF
    assert series.infcount(dm.col1) == 1
    assert series.infcount(dm.col2) == 0
    assert series.infcount(dm.col3) == 1
    assert series.infcount(a) == 2
    check_col(series.infcount(dm.s), [0, 1])


def test_flatten():
    
    dm = DataMatrix(length=2)
    dm.col = 'a', 'b'
    dm.s1 = SeriesColumn(depth=3)
    dm.s1[:] = 1,2,3
    dm.s2 = SeriesColumn(depth=3)
    dm.s2[:] = 3,2,1
    flat_dm = series.flatten(dm)
    check_col(flat_dm.col, ['a', 'a', 'a', 'b', 'b', 'b'])
    check_col(flat_dm.s1, [1, 2, 3, 1, 2, 3])
    check_col(flat_dm.s2, [3, 2, 1, 3, 2, 1])
    check_integrity(flat_dm)


def test_endlock():

    dm = DataMatrix(length=5)
    dm.series = SeriesColumn(depth=3)
    dm.series[0] = 1, 2, 3
    dm.series[1] = 1, np.nan, 3
    dm.series[2] = 1, 2, np.nan
    dm.series[3] = np.nan, 2, np.nan
    dm.series[4] = np.nan, np.nan, np.nan
    dm.series = series.endlock(dm.series)
    check_series(dm.series, [
        [1,2,3],
        [1,np.nan,3],
        [np.nan,1,2],
        [np.nan,np.nan,2],
        [np.nan,np.nan,np.nan],
    ])


def test_lock():

    dm = DataMatrix(length=2)
    dm.s = SeriesColumn(depth=3)
    dm.s[0] = 1, 2, 3
    dm.s[1] = -1, -2, -3
    dm.l, zero_point = series.lock(dm.s, [-1, 1])
    assert zero_point == 1
    check_series(dm.l, [
        [np.nan, np.nan, 1, 2, 3],
        [-1, -2, -3, np.nan, np.nan]
        ])


def test_reduce_():

    dm = DataMatrix(length=2)
    dm.series = SeriesColumn(depth=3)
    dm.series[0] = 1, 2, 3
    dm.series[1] = 2, 3, 4
    dm.col = series.reduce_(dm.series)
    check_col(dm.col, [2,3])
    check_integrity(dm)


def test_window():

    dm = DataMatrix(length=2)
    dm.series = SeriesColumn(depth=4)
    dm.series[0] = 0,1,1,0
    dm.series[1] = 0,2,2,0
    dm.window = series.window(dm.series, 1, 3)
    check_series(dm.window, [[1,1], [2,2]])
    check_integrity(dm)


def test_baseline():

    dm = DataMatrix(length=2)
    dm.series = SeriesColumn(depth=3)
    dm.series[0] = range(3)
    dm.series[1] = range(1,4)
    dm.baseline = SeriesColumn(depth=3)
    dm.baseline[0] = range(1,4)
    dm.baseline[1] = range(3)
    dm.norm = series.baseline(dm.series, dm.baseline)
    check_series(dm.norm, [[-2,-1,0], [0,1,2]])
    check_integrity(dm)


def test_downsample():

    dm = DataMatrix(length=2)
    dm.series = SeriesColumn(depth=10)
    dm.series[0] = range(10)
    dm.series[1] = [0,1]*5
    dm.d3 = series.downsample(dm.series, 3)
    dm.d5 = series.downsample(dm.series, 5)
    check_series(dm.d3, [[1,4,7], [1./3, 2./3, 1./3]])
    check_series(dm.d5, [[2,7], [.4, .6]])
    check_integrity(dm)


def test_smooth():

    dm = DataMatrix(length=2)
    dm.series = SeriesColumn(depth=6)
    dm.series[0] = range(6)
    dm.series[1] = [0,1,2]*2
    dm.s = series.smooth(dm.series, winlen=3, wintype='flat')
    check_series(dm.s, [
        [2./3, 1, 2, 3, 4, 4+1./3],
        [2./3, 1, 1, 1, 1, 1+1./3]
        ])
    check_integrity(dm)


def test_threshold():

    dm = DataMatrix(length=2)
    dm.series = SeriesColumn(depth=4)
    dm.series[0] = range(4)
    dm.series[1] = range(1,5)
    dm.t1 = series.threshold(dm.series, lambda v: v > 1)
    dm.t2 = series.threshold(dm.series, lambda v: v > 1 and v < 3)
    dm.t3 = series.threshold(dm.series, lambda v: v < 3, min_length=3)
    check_series(dm.t1, [[0,0,1,1], [0,1,1,1]])
    check_series(dm.t2, [[0,0,1,0], [0,1,0,0]])
    check_series(dm.t3, [[1,1,1,0], [0,0,0,0]])
    check_integrity(dm)


def test_concatenate():

    dm = DataMatrix(length=1)
    dm.s1 = SeriesColumn(depth=3)
    dm.s1[:] = 1,2,3
    dm.s2 = SeriesColumn(depth=3)
    dm.s2[:] = 3,2,1
    dm.s = series.concatenate(dm.s1, dm.s2)
    check_series(dm.s, [[1,2,3,3,2,1]])


def test_interpolate():

    dm = DataMatrix(length=3)
    dm.s = SeriesColumn(depth=4)
    dm.s = 1, 2, 3, 4
    dm.s[0] = np.nan
    dm.s[1, 0] = np.nan
    dm.s[1, 2] = np.nan
    with pytest.warns(UserWarning):
        dm.i = series.interpolate(dm.s)
    check_series(dm.i, [
        [np.nan]*4,
        [2,2,3,4],
        [1,2,3,4]])


def test_normalize_time():

    dm = DataMatrix(length=2)
    dm.s = SeriesColumn(depth=2)
    dm.s[0] = 1,2
    dm.s[1] = np.nan, 3
    dm.t = SeriesColumn(depth=2)
    dm.t[0] = 0,3
    dm.t[1] = 1, 2
    dm.n = series.normalize_time(dm.s, dm.t)
    check_series(dm.n, [
        [1, np.nan, np.nan, 2],
        [np.nan, np.nan, 3, np.nan]
    ])
