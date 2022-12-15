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

from datamatrix.py3compat import *
from datamatrix import DataMatrix, MixedColumn, FloatColumn, IntColumn, \
    SeriesColumn
from testcases.test_tools import check_series
import numpy as np
import pytest


def check_odd(dm):

    assert dm.col[...] == np.mean(dm.col) == dm.col.mean == \
        pytest.approx(13./3)
    assert dm.col.median == 2
    assert np.std(dm.col, ddof=1) == dm.col.std  == \
        pytest.approx(np.std( [1,2,10], ddof=1))
    assert np.min(dm.col) == dm.col.min == 1
    assert np.max(dm.col) == dm.col.max == 10
    assert np.sum(dm.col) == dm.col.sum == 13


def check_even(dm):

    assert dm.col[...] == dm.col.mean == pytest.approx(4)
    assert dm.col.median == 2.5
    assert dm.col.std == pytest.approx(np.std( [1,2,3,10], ddof=1))
    assert dm.col.min == 1
    assert dm.col.max == 10
    assert dm.col.sum == 16


def check_desc_stats(col_type, invalid, assert_invalid):

    dm = DataMatrix(length=4, default_col_type=col_type)
    # Even lengths
    dm.col = 1, 2, 3, 10
    check_even(dm)
    if col_type is not IntColumn:
        dm.length = 5
        dm.col = 1, 2, 3, 10, invalid
        check_even(dm)
    # Odd lengths (and even with one invalid)
    dm.length = 3
    dm.col = 1, 2, 10
    check_odd(dm)
    if col_type is not IntColumn:
        dm.length = 4
        dm.col[3] = invalid
        check_odd(dm)
    # One lengths
    dm.length = 1
    dm.col = 1
    assert dm.col[...] == dm.col.mean == 1
    assert dm.col.median == 1
    if col_type in (IntColumn, FloatColumn):
        with pytest.warns(RuntimeWarning):
            assert_invalid(dm.col.std)
    else:
        assert_invalid(dm.col.std)
    assert dm.col.min == 1
    assert dm.col.max == 1
    assert dm.col.sum == 1
    # Zero lengths
    dm.length = 0
    if col_type in (IntColumn, FloatColumn):
        with pytest.warns(RuntimeWarning):
            assert_invalid(dm.col[...])
            assert_invalid(dm.col.mean)
            assert_invalid(dm.col.median)
            assert_invalid(dm.col.std)
            assert_invalid(dm.col.min)
            assert_invalid(dm.col.max)
            assert_invalid(dm.col.sum)
    else:
        assert_invalid(dm.col[...])
        assert_invalid(dm.col.mean)
        assert_invalid(dm.col.median)
        assert_invalid(dm.col.std)
        assert_invalid(dm.col.min)
        assert_invalid(dm.col.max)
        assert_invalid(dm.col.sum)
    # NAN values
    if col_type is not IntColumn:
        dm.col = invalid
        assert_nan(dm.col[...])
        assert_nan(dm.col.mean)
        assert_nan(dm.col.median)
        assert_nan(dm.col.std)
        assert_nan(dm.col.min)
        assert_nan(dm.col.max)
        assert_nan(dm.col.sum)
        np.mean(dm.col) == dm.col.mean
        np.std(dm.col) == dm.col.std
        np.max(dm.col) == dm.col.max
        np.min(dm.col) == dm.col.min
        np.sum(dm.col) == dm.col.sum


def assert_None(val):

    assert val is None


def assert_nan(val):

    assert np.isnan(val)


def test_seriescolumn():

    dm = DataMatrix(length=3)
    dm.col = SeriesColumn(depth=3)
    dm.col[0] = [1,2,3]
    dm.col[1] = [3,3,3]
    dm.col[2] = [4,4,4]
    assert all(dm.col[:, ...] == [2, 3, 4])
    assert all(dm.col[...] == [8./3, 9./3, 10/3.])
    assert all(dm.col.mean == [8./3, 9./3, 10/3.])
    assert all(dm.col.median == [3,3,3])
    assert all(dm.col.max == [4,4,4])
    assert all(dm.col.min == [1,2,3])
    assert all(dm.col.std == [
        np.std([4,3,1], ddof=1),
        np.std([4,3,2], ddof=1),
        np.std([4,3,3], ddof=1)
        ])


def test_mixedcolumn():

    check_desc_stats(MixedColumn, invalid=u'', assert_invalid=assert_nan)


def test_floatcolumn():

    check_desc_stats(FloatColumn, invalid=np.nan, assert_invalid=assert_nan)


def test_intcolumn():

    check_desc_stats(IntColumn, invalid=0, assert_invalid=assert_nan)
