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
    DataMatrix, MixedColumn, FloatColumn, IntColumn, MultiDimensionalColumn,
    SeriesColumn, NAN
)
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from testcases.test_tools import check_col, check_series, check_integrity
import pytest
import numpy as np


def _test_numericcolumn(cls):

    # Test init and change by single value
    dm = DataMatrix(length=2)
    dm.col = cls
    dm.col = 1
    check_col(dm.col, [1, 1])
    dm.col = 2
    check_col(dm.col, [2, 2])
    # Test init and change by sequence
    dm = DataMatrix(length=2)
    dm.col = cls
    dm.col = 1, 2
    check_col(dm.col, [1, 2])
    dm.col = 3, 4
    check_col(dm.col, [3, 4])
    # Test setting by slice
    dm = DataMatrix(length=3)
    dm.col = cls
    dm.col = 1
    dm.col[1:] = 2
    check_col(dm.col, [1, 2, 2])
    dm.col[:-1] = 4, 3
    check_col(dm.col, [4, 3, 2])
    # Test setting by DataMatrix
    dm = DataMatrix(length=10)
    dm.x = range(10)
    dm.y = FloatColumn
    dm = dm.x != {3, 6}
    dm.y[dm.x > 3] = 10
    dm.y[dm.x >= 8] = 11
    check_col(dm.y, [np.nan] * 3 + [10] * 3 + [11] * 2)
    # Test setting by row
    dm = DataMatrix(length=2)
    for i, row in enumerate(dm):
        row.col = i
    check_col(dm.col, [0, 1])
    # Test shortening and lengthening
    dm = DataMatrix(length=4)
    dm.length = 0
    dm.length = 4
    # Check uniqueness
    dm.col = 1, 2, 1, 2
    assert sorted(dm.col.unique) == [1, 2]
    dm.col[dm.col == 2] = 0, 0
    check_col(dm.col, [1, 0, 1, 0])
    check_integrity(dm)
    # Check if numericcolumns return right type
    dm = DataMatrix(length=5)
    dm.col = cls
    dm.col = 1, 2, 3, 4, 5
    # int -> float
    val = dm.col[2]
    assert isinstance(val, (int, float))
    assert val == 3
    # (int, int) -> FloatColumn
    val = dm.col[1, 3]
    assert isinstance(val, cls)
    check_col(val, [2, 4])
    # slice -> FloatColumn
    val = dm.col[1:-1]
    assert isinstance(val, cls)
    check_col(val, [2, 3, 4])
    # datamatrix → FloatColumn
    val = dm.col[dm[1:-1]]
    assert isinstance(val, cls)
    check_col(val, [2, 3, 4])
    # Check array setting and getting
    if cls != MixedColumn:
        a = dm.col.array
        assert isinstance(a, np.ndarray)
        assert a.shape == (5,)
        assert all(a == [1, 2, 3, 4, 5])


def _test_copying(cls):

    dm = DataMatrix(length=5)
    dm.d = cls
    dm2 = dm[:]
    dm2.e = dm.d
    dm2.f = dm2.d
    assert dm2 is not dm
    assert dm2.d is not dm.d
    assert dm2.e is not dm.d
    assert dm2.f is dm2.d
    assert dm2.d._seq is not dm.d._seq
    dm.c = dm.d
    assert dm.c is dm.d
    assert dm.c._seq is dm.d._seq
    dm.e = dm.d[:]
    assert dm.e is not dm.d
    assert dm.e._seq is not dm.d._seq
    check_integrity(dm)
    check_integrity(dm2)


def test_mixedcolumn():

    _test_numericcolumn(MixedColumn)
    _test_copying(MixedColumn)
    dm = DataMatrix(length=4)
    dm.col = '1.1', '1', 'x', None
    check_col(dm.col, [1.1, 1, 'x', None])
    dm.col[dm.col == {1, None}] = 'a', 'b'
    check_col(dm.col, [1.1, 'a', 'x', 'b'])


def test_intcolumn():

    _test_numericcolumn(IntColumn)
    _test_copying(IntColumn)
    # Test automatic conversion to int
    dm = DataMatrix(length=2)
    dm.col = IntColumn
    dm.col = 1.9, '2.9'
    check_col(dm.col, [1, 2])
    del dm.col
    dm.col = int
    dm.col = 1.9, '2.9'
    check_col(dm.col, [1, 2])
    # Test setting invalid values
    def _():
        with pytest.raises(TypeError):
            dm.col[0] = 'x'
    _()
    def _():
        with pytest.raises(TypeError):
            dm.col = 'x'
    _()
    def _():
        with pytest.raises(TypeError):
            dm.col[:-1] = 'x'
    _()
    # Check dtype
    assert dm.col._seq.dtype == np.int64
    check_integrity(dm)


def test_floatcolumn():

    _test_numericcolumn(FloatColumn)
    _test_copying(FloatColumn)
    # Test automatic conversion to float
    dm = DataMatrix(length=2)
    dm.col = FloatColumn
    dm.col = 1.9, '2.9'
    check_col(dm.col, [1.9, 2.9])
    del dm.col
    dm.col = float
    dm.col = 1.9, '2.9'
    check_col(dm.col, [1.9, 2.9])
    # Test nans
    dm.col = 'nan'
    check_col(dm.col, [np.nan, np.nan])
    with pytest.warns(UserWarning):
        dm.col = None
    check_col(dm.col, [np.nan, np.nan])
    dm.col = np.nan
    check_col(dm.col, [np.nan, np.nan])
    with pytest.warns(UserWarning):
        dm.col = 'x'
    check_col(dm.col, [np.nan, np.nan])
    # Test infs
    dm.col = 'inf'
    check_col(dm.col, [np.inf, np.inf])
    dm.col = np.inf
    check_col(dm.col, [np.inf, np.inf])
    # Test nans and infs
    dm.col = 'nan', 'inf'
    check_col(dm.col, [np.nan, np.inf])
    dm.col = np.inf, np.nan
    check_col(dm.col, [np.inf, np.nan])
    with pytest.warns(UserWarning):
        dm.col = 'x', None
    check_col(dm.col, [np.nan, np.nan])
    # Check dtype
    assert dm.col._seq.dtype == np.float64
    check_integrity(dm)


def test_seriescolumn():

    _test_copying(SeriesColumn(depth=1))
    dm = DataMatrix(length=2)
    dm.col = SeriesColumn(depth=3)
    # Set all rows to a single value
    dm.col = 1
    check_series(dm.col, [[1,1,1], [1,1,1]])
    # Set rows to different single values
    dm.col = 2, 3
    check_series(dm.col, [[2,2,2], [3,3,3]])
    # Set one row to a single value
    dm.col[0] = 4
    check_series(dm.col, [[4,4,4], [3,3,3]])
    # Set one row to different single values
    dm.col[1] = 5, 6, 7
    check_series(dm.col, [[4,4,4], [5,6,7]])
    # Set all rows to different single values
    dm.col.setallrows([8,9,10])
    check_series(dm.col, [[8,9,10], [8,9,10]])
    # Set the first value in all rows
    dm.col[:,0] = 1
    check_series(dm.col, [[1,9,10], [1,9,10]])
    # Set all values in the first row
    dm.col[0,:] = 2
    check_series(dm.col, [[2,2,2], [1,9,10]])
    # Set all values
    dm.col[:,:] = 3
    check_series(dm.col, [[3,3,3], [3,3,3]])
    # Test shortening and lengthening
    dm.length = 0
    check_series(dm.col, [])
    dm.length = 3
    dm.col = 1, 2, 3
    dm.col.depth = 1
    check_series(dm.col, [[1],[2],[3]])
    dm.col.depth = 3
    check_series(dm.col, [[1,NAN,NAN], [2,NAN,NAN], [3,NAN,NAN]])
    check_integrity(dm)
    # Test
    dm = DataMatrix(length=2)
    dm.col = SeriesColumn(depth=3)
    dm.col = 1, 2
    check_series(dm.col, [[1,1,1], [2,2,2]])
    dm.col = 3,4,5
    check_series(dm.col, [[3,4,5]]*2)
    dm.col.depth = 2
    dm.col[:] = 1,2
    check_series(dm.col, [[1,1], [2,2]])
    dm.col[:,:] = 3,4
    check_series(dm.col, [[3,4], [3,4]])
    # Check if series return right type
    dm = DataMatrix(length=4)
    dm.col = SeriesColumn(depth=5)
    dm.col = [
        [1, 2, 3, 4, 5],
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
        [16, 17, 18, 19, 20]
    ]
    # (int, int) -> float
    val = dm.col[2, 2]
    assert val == 13
    assert type(val) == float
    # (int) -> array
    val = dm.col[2]
    assert all(val == np.array([11,12,13,14,15]))
    assert type(val) == np.ndarray
    # (int, slice) -> array
    val = dm.col[2, 1:-1]
    assert all(val == np.array([12,13,14]))
    assert type(val) == np.ndarray
    # (int, (int, int)) -> array
    val = dm.col[2, (1, 3)]
    assert all(val == np.array([12,14]))
    assert type(val) == np.ndarray
    # (slice) -> SeriesColumn
    val = dm.col[1:-1]
    check_series(val, [
        [6, 7, 8, 9, 10],
        [11, 12, 13, 14, 15],
    ])
    # (slice, int) -> FloatColumn
    val = dm.col[1:-1, 2]
    assert isinstance(val, FloatColumn)
    check_col(val, [8, 13])
    # ((int, int), int) -> FloatColumn
    val = dm.col[(1, 3), 2]
    assert isinstance(val, FloatColumn)
    check_col(val, [8, 18])
    # (slice, slice) -> SeriesColumn
    val = dm.col[1:-1, 1:-1]
    assert isinstance(val, _SeriesColumn)
    check_series(val, [
        [7, 8, 9],
        [12, 13, 14],
    ])
    # ((int, int), slice) -> SeriesColumn
    val = dm.col[(1, 3), 1:-1]
    assert isinstance(val, _SeriesColumn)
    check_series(val, [
        [7, 8, 9],
        [17, 18, 19],
    ])
    # ((int, int), (int int)) -> SeriesColumn
    val = dm.col[(1, 3), (1, 3)]
    assert isinstance(val, _SeriesColumn)
    check_series(val, [
        [7, 9],
        [17, 19],
    ])
    # Check if assigning 2D arrays works
    a = np.ones((2, 3))
    a[0] = 1, 2, 3
    a[1] = 4, 5, 6
    b = np.ones((3, 2))
    b[:,0] = 1, 2, 3
    b[:,1] = 4, 5, 6
    dm = DataMatrix(length=2)
    dm.s = a
    dm.t = b
    check_series(dm.s, a)
    check_series(dm.t, a)


def test_multidimensional_assignment():
    dm = DataMatrix(length=2)
    dm.m = MultiDimensionalColumn(shape=(('x', 'y', 'z'),))
    # Set all columns in one row
    a = np.array([[1, 1, 1],
                  [0, 0, 0]])
    dm.m = 0
    dm.m[0] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0] = 1, 1, 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, (0, 1, 2)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ('x', 'y', 'z')] = 1
    assert np.all(dm.m._seq == a)
    # Set all columns in all rows
    a = np.array([[1, 1, 1],
                  [1, 1, 1]])
    dm.m = 0
    dm.m[:] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, ...] = 1
    assert np.all(dm.m._seq == a)
    # Set one column in all rows
    a = np.array([[0, 1, 0],
                  [0, 1, 0]])
    dm.m = 0
    dm.m[:, 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 'y'] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., 'y'] = 1
    assert np.all(dm.m._seq == a)
    # Set two column in all rows
    a = np.array([[1, 0, 1],
                  [1, 0, 1]])
    dm.m = 0
    dm.m[:, (0, 2)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, ('x', 'z')] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., (0, 2)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., ('x', 'z')] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0, 1), (0, 2)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0, 1), ('x', 'z')] = 1
    assert np.all(dm.m._seq == a)
    # Test a two-dimensional column (SurfaceColumn)
    dm = DataMatrix(length=2)
    dm.m = MultiDimensionalColumn(shape=(('x', 'y', 'z'),
                                         ('a', 'b', 'c', 'd')))
    # Set all dimensions
    a = np.array([[[1, 1, 1, 1],
                   [1, 1, 1, 1],
                   [1, 1, 1, 1]],
                  [[1, 1, 1, 1],
                   [1, 1, 1, 1],
                   [1, 1, 1, 1]]])
    dm.m = a
    assert np.all(dm.m._seq == a)
    dm.m[:] = a
    assert np.all(dm.m._seq == a)
    dm.m[...] = a
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, :, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0, 1), :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0, 1), (0, 1, 2)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0, 1), (0, 1, 2), (0, 1, 2, 3)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., :, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, ..., :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, ...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, :, ...] = 1
    assert np.all(dm.m._seq == a)
    # Set first dimension
    a = np.array([[[1, 1, 1, 1],
                   [1, 1, 1, 1],
                   [1, 1, 1, 1]],
                  [[0, 0, 0, 0],
                   [0, 0, 0, 0],
                   [0, 0, 0, 0]]])
    dm.m = 0
    dm.m[0] = a[0]
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, :] = a[0]
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ...] = a[0]
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, :, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ..., :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, (0, 1, 2), :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, :, (0, 1, 2, 3)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, (0, 1, 2), (0, 1, 2, 3)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0,)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0,), :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0,), :, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0,), (0, 1, 2), :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0,), :, (0, 1, 2, 3)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[(0,), (0, 1, 2), (0, 1, 2, 3)] = 1
    assert np.all(dm.m._seq == a)
    # Set second dimension
    a = np.array([[[0, 0, 0, 0],
                   [1, 1, 1, 1],
                   [0, 0, 0, 0]],
                  [[0, 0, 0, 0],
                   [1, 1, 1, 1],
                   [0, 0, 0, 0]]])
    dm.m = 0
    dm.m[:, 1] = a[:, 1]
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 1, ...] = a[:, 1]
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 1, :] = a[:, 1]
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 'y'] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 1, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 'y', :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 1, ...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, 'y', ...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., 1, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., 'y', :] = 1
    assert np.all(dm.m._seq == a)
    a = np.array([[[1, 1, 1, 1],
                   [0, 0, 0, 0],
                   [1, 1, 1, 1]],
                  [[1, 1, 1, 1],
                   [0, 0, 0, 0],
                   [1, 1, 1, 1]]])
    dm.m = 0
    dm.m[:, (0, 2)] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, ('x', 'z')] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, (0, 2), :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, ('x', 'z'), :] = 1
    assert np.all(dm.m._seq == a)
    # Set first and second dimension
    a = np.array([[[0, 0, 0, 0],
                   [1, 1, 1, 1],
                   [0, 0, 0, 0]],
                  [[0, 0, 0, 0],
                   [0, 0, 0, 0],
                   [0, 0, 0, 0]]])
    dm.m = 0
    dm.m[0, 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 'y'] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 1, :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 'y', :] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 1, ...] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 'y', ...] = 1
    assert np.all(dm.m._seq == a)
    # Set third dimension
    a = np.array([[[0, 1, 0, 0],
                   [0, 1, 0, 0],
                   [0, 1, 0, 0]],
                  [[0, 1, 0, 0],
                   [0, 1, 0, 0],
                   [0, 1, 0, 0]]])
    dm.m = 0
    dm.m[:, :, 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[:, :, 'b'] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[..., 'b'] = 1
    assert np.all(dm.m._seq == a)
    # Set first and third dimension
    a = np.array([[[0, 1, 0, 0],
                   [0, 1, 0, 0],
                   [0, 1, 0, 0]],
                  [[0, 0, 0, 0],
                   [0, 0, 0, 0],
                   [0, 0, 0, 0]]])
    dm.m = 0
    dm.m[0, :, 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, :, 'b'] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ..., 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, ..., 'b'] = 1
    assert np.all(dm.m._seq == a)
    # Set first, second, and third dimension
    a = np.array([[[0, 0, 0, 0],
                   [0, 1, 0, 0],
                   [0, 0, 0, 0]],
                  [[0, 0, 0, 0],
                   [0, 0, 0, 0],
                   [0, 0, 0, 0]]])
    dm.m = 0
    dm.m[0, 1, 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 1, 'b'] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 'y', 1] = 1
    assert np.all(dm.m._seq == a)
    dm.m = 0
    dm.m[0, 'y', 'b'] = 1
    assert np.all(dm.m._seq == a)
    

def test_resize():

    dm = DataMatrix(length=0)
    for l in range(1, 11):
        print('growing to %d' % l)
        dm.length += 1
        for x, y in zip(dm._rowid, range(l)):
            print(x, y)
            assert x == y
    for l in range(10, 0, -1):
        print('shrinking to %d' % l)
        dm.length -= 1
        for x, y in zip(dm._rowid, range(l)):
            print(x, y)
            assert x == y


def test_properties():
    
    dm = DataMatrix(length=0)
    dm.c = -1
    assert dm.empty
    dm = DataMatrix(length=1)
    assert dm.empty
    dm = DataMatrix(length=1)
    dm.c = -1
    assert not dm.empty
    dm = DataMatrix(length=3)
    dm.c = -1
    dm.d = -1
    assert len(dm) == 3


def test_where():
    
    dm = DataMatrix(length=4)
    dm.col = 1, 2, 3, 4
    assert dm[dm.col == {2, 4}] == [1, 3]
