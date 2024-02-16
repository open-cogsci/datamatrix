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
from datamatrix import (
    DataMatrix,
    MixedColumn,
    IntColumn,
    FloatColumn,
    SeriesColumn,
    MultiDimensionalColumn
)
from datamatrix import operations as ops
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
from testcases.test_tools import check_col, check_row, check_series, check_dm
import numpy as np
import itertools
import pytest
import math


def test_replace():

    dm = DataMatrix(length=3)
    dm.a = 0, 1, 2
    dm.c = FloatColumn
    dm.c = np.nan, 1, 2
    dm.s = SeriesColumn(depth=3)
    dm.s[0] = 0, 1, 2
    dm.s[1] = np.nan, 1, 2
    dm.s[2] = np.nan, 1, 2
    dm.a = ops.replace(dm.a, {0 : 100, 2 : 200})
    dm.c = ops.replace(dm.c, {np.nan : 100, 2 : np.nan})
    dm.s = ops.replace(dm.s, {np.nan : 100, 2 : np.nan})
    check_col(dm.a, [100, 1, 200])
    check_col(dm.c, [100, 1, np.nan])
    check_series(dm.s, [
        [0, 1, np.nan],
        [100, 1, np.nan],
        [100, 1, np.nan],
        ])


def test_z():

    dm = DataMatrix(length=5)
    dm.a = range(-2, 3)
    dm.z = ops.z(dm.a)
    for test, ref in zip(dm.z, [-1.26, -0.63, 0, .63, 1.26]):
        assert(math.isclose(test, ref, abs_tol=.01))
    # Add a non-numeric value, which should be ignored and its z value should
    # be NAN.
    dm.length = 6
    dm.z = ops.z(dm.a)
    assert(dm.z[5] != dm.z[5])
    for test, ref in zip(dm.z[:-1], [-1.26, -0.63, 0, .63, 1.26]):
        assert(math.isclose(test, ref, abs_tol=.01))
    # If there is no variability, the z-scores should be NAN
    dm.a = 2
    dm.z = ops.z(dm.a)
    assert(all(ref != ref for ref in dm.z))
    # Test series columns
    dm = DataMatrix(length=3)
    dm.s = SeriesColumn(depth=4)
    dm.s = [
        [1, 2, 3, np.nan],
        [10, 20, 30, np.nan],
        [100, 200, 300, np.nan]
    ]
    dm.z = ops.z(dm.s)
    assert math.isclose(np.nanmean(dm.z._seq), 0, abs_tol=1e-10)
    assert math.isclose(np.nanstd(dm.z._seq), 1, abs_tol=1e-10)


def test_weight():

    dm = DataMatrix(length=3)
    dm.a = 'a', 'b', 'c'
    dm.b = 1, 0, 2
    dm = ops.weight(dm.b)
    check_col(dm.a, ['a', 'c', 'c'])
    check_col(dm.b, [1, 2, 2])


def test_split():

    dm = DataMatrix(length=4)
    dm.a = 'a', 'a', 'b', 'b'
    dm.b = 0, 1, 2, 3
    # Without values
    g = ops.split(dm.a)
    val, dm = next(g)
    assert val == 'a'
    check_col(dm.a, ['a', 'a'])
    check_col(dm.b, [0, 1])
    val, dm = next(g)
    assert val == 'b'
    check_col(dm.a, ['b', 'b'])
    check_col(dm.b, [2, 3])
    # With values
    dm = DataMatrix(length=4)
    dm.a = 'a', 'a', 'b', 'b'
    dm.b = 0, 1, 2, 3
    dma, dmb = ops.split(dm.a, 'a', 'b')
    check_col(dma.a, ['a', 'a'])
    check_col(dma.b, [0, 1])
    check_col(dmb.a, ['b', 'b'])
    check_col(dmb.b, [2, 3])
    # With multiple columns
    dm = DataMatrix(length=8)
    dm.A = 0, 0, 1, 1, 0, 0, 1, 1
    dm.B = 'a', 'b', 'a', 'b', 'a', 'b', 'a', 'b'
    dm.C = 'x', 'x', 'x', 'x', 'y', 'y', 'y', 'y'
    g = ops.split(dm.A, dm.B)
    val1, val2, sdm = next(g)
    assert val1 == 0
    assert val2 == 'a'
    assert(len(sdm) == 2)
    val1, val2, sdm = next(g)
    assert val1 == 0
    assert val2 == 'b'
    assert(len(sdm) == 2)
    val1, val2, sdm = next(g)
    assert val1 == 1
    assert val2 == 'a'
    assert(len(sdm) == 2)
    val1, val2, sdm = next(g)
    assert val1 == 1
    assert val2 == 'b'
    assert(len(sdm) == 2)
    g = ops.split(dm.A, dm.B, dm.C)
    val1, val2, val3, sdm = next(g)
    assert val1 == 0
    assert val2 == 'a'
    assert val3 == 'x'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 0
    assert val2 == 'a'
    assert val3 == 'y'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 0
    assert val2 == 'b'
    assert val3 == 'x'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 0
    assert val2 == 'b'
    assert val3 == 'y'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 1
    assert val2 == 'a'
    assert val3 == 'x'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 1
    assert val2 == 'a'
    assert val3 == 'y'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 1
    assert val2 == 'b'
    assert val3 == 'x'
    assert(len(sdm) == 1)
    val1, val2, val3, sdm = next(g)
    assert val1 == 1
    assert val2 == 'b'
    assert val3 == 'y'
    assert(len(sdm) == 1)


def test_bin_split():

    dm = DataMatrix(length=4)
    dm.a = range(4)
    dm = ops.shuffle(dm)
    dm1, dm2 = ops.bin_split(dm.a, 2)
    check_col(dm1.a, [0,1])
    check_col(dm2.a, [2,3])
    dm1, dm2, dm3 = ops.bin_split(dm.a, 3)
    check_col(dm1.a, [0])
    check_col(dm2.a, [1])
    check_col(dm3.a, [2,3])
    dm1, = ops.bin_split(dm.a, 1)
    check_col(dm1.a, [0,1,2,3])
    def _():
        with pytest.raises(ValueError):
            x, = ops.bin_split(dm.a, 5)
    _()


def test_fullfactorial():

    dm = DataMatrix(length=3)
    dm.a = 'a', 'b', ''
    dm.b = 0, 1, 2
    dm = ops.fullfactorial(dm)
    check_col(dm.a, ['a', 'b', 'a', 'b', 'a', 'b'])
    check_col(dm.b, [0, 0, 1, 1, 2, 2])


def test_group():

    dm = DataMatrix(length=4)
    dm.a = 'b', 'b', 'a', 'a'
    dm.b = 'x', 'x', 'x', 'y'
    dm.c = IntColumn
    dm.c = 0, 1, 2, 3
    dm.s = SeriesColumn(depth=3)
    dm.s = 1, 2, 3
    dm.m = MultiDimensionalColumn(shape=(2, 2))
    dm.m = [[1, 2], [3, 4]]
    dm = ops.group(dm, [dm.a, dm.b])
    # Assert that at least one of the permutations passes
    for ref in itertools.permutations([[3, np.nan], [2, np.nan], [0, 1]]):
        try:
            check_series(dm.c, ref)
            break
        except AssertionError:
            pass
    else:
        assert(False)


def test_stack(invalid=''):

    dm1 = DataMatrix(length=2)
    dm1.col1 = 1, 2
    dm1.col_shared = 3, 4
    dm1.m = MultiDimensionalColumn(shape=(1,))
    dm2 = DataMatrix(length=2)
    dm2.col2 = 5, 6
    dm2.col_shared = 7, 8
    dm2.m = MultiDimensionalColumn(shape=(2,))
    dm3 = DataMatrix(length=2)
    dm3.col3 = 9, 10
    dm3.col_shared = 11, 12
    dm3.m = MultiDimensionalColumn(shape=(3,))
    dm4 = ops.stack(dm1, dm2, dm3)
    check_col(dm4.col1, [1, 2, invalid, invalid, invalid, invalid])
    check_col(dm4.col_shared, [3,4,7,8,11,12])
    check_col(dm4.col2, [invalid, invalid, 5, 6, invalid, invalid])
    check_col(dm4.col3, [invalid, invalid, invalid, invalid, 9, 10])
    assert dm4.m.shape == (6, 3)
    dm5 = DataMatrix()
    for row in dm1:
        dm5 <<= row
    for row in dm2:
        dm5 <<= row
    for row in dm3:
        dm5 <<= row
    check_dm(dm4, dm5)
    

def test_sort():

    dm = DataMatrix(length=2)
    dm.a = 'b', 'a'
    dm.b = 1, 0
    dm.a = ops.sort(dm.a)
    check_col(dm.a, ['a', 'b'])
    check_col(dm.b, [1, 0])
    dm = ops.sort(dm, by=dm.b)
    check_col(dm.a, ['b', 'a'])
    check_col(dm.b, [0, 1])
    
    
def test_random_sample():
    
    dm = DataMatrix(length=3)
    dm.a = 0, 1, 2
    options = [
        [0, 1],
        [0, 2],
        [1, 2],
        [1, 0],
        [2, 0],
        [2, 1]
    ]
    o = options[:]
    while o:
        col = ops.random_sample(dm.a, k=2)
        if list(col) in o:
            o.remove(list(col))
    o = options[:]
    while o:
        dm2 = ops.random_sample(dm, k=2)
        if list(dm2.a) in o:
            o.remove(list(dm2.a))


def test_shuffle():

    dm = DataMatrix(length=2)
    dm.a = 'a', 'b'
    dm.b = 0, 1
    while True:
        dm.a = ops.shuffle(dm.a)
        check_col(dm.b, [0, 1])
        try:
            check_col(dm.a, ['b', 'a'])
            break
        except:
            pass
    dm = DataMatrix(length=2)
    dm.a = 'a', 'b'
    dm.b = 0, 1
    while True:
        dm = ops.shuffle(dm)
        try:
            check_col(dm.a, ['b', 'a'])
            check_col(dm.b, [1, 0])
            break
        except:
            pass


def test_shuffle_horiz():

    dm = DataMatrix(length=2)
    dm.a = 'a', 'b'
    dm.b = 0, 1
    dm.c = '-', '-'
    while True:
        dm2 = ops.shuffle_horiz(dm)
        try:
            check_row(dm2[0], [0, '-', 'a'])
            break
        except:
            pass
    while True:
        dm2 = ops.shuffle_horiz(dm.a, dm.b)
        try:
            check_row(dm2[0], [0, 'a', '-'])
            break
        except:
            pass
    for i in range(1000):
        dm2 = ops.shuffle_horiz(dm.a, dm.b)
        check_col(dm.c, ['-', '-'])
    ops.shuffle_horiz(dm.a)

def test_keep_only():

    dm = DataMatrix(length=2)
    dm.a = 'a', 'b'
    dm.b = 0, 1
    dm.c = 'y', 'z'
    for cols in (['b', 'c'], [dm.b, dm.c]):
        dm = ops.keep_only(dm, *cols)
        assert 'a' not in dm.column_names
        assert 'b' in dm.column_names
        assert 'c' in dm.column_names
        dm = dm[cols]
        assert 'a' not in dm.column_names
        assert 'b' in dm.column_names
        assert 'c' in dm.column_names


def test_auto_type():

    dm = DataMatrix(length=2)
    dm.a = 'a', 1
    dm.b = 0.1, 1
    dm.c = 0, 1
    dm.s = SeriesColumn(depth=2)
    dm.m = MultiDimensionalColumn(shape=(2, 2))
    dm = ops.auto_type(dm)
    assert isinstance(dm.a, MixedColumn)
    assert isinstance(dm.b, FloatColumn)
    assert isinstance(dm.c, IntColumn)
    assert isinstance(dm.s, _SeriesColumn)
    assert isinstance(dm.m, _MultiDimensionalColumn)
