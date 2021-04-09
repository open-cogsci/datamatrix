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
import math
import numpy as np
import pytest
from testcases.test_tools import check_col
from datamatrix import (
    DataMatrix,
    FloatColumn,
    IntColumn,
    INF, NAN,
    operations as ops
)
from datamatrix._datamatrix import _basecolumn, _sort


def check_mixedcolumn_typing():

    dm = DataMatrix(length=4)
    dm.i = 1, '1', 2, '2'
    assert all(isinstance(v, int) for v in dm.i)
    dm.f = 1.1, '1.1', 2.1, '2.2'
    assert all(isinstance(v, float) for v in dm.f)
    dm.inf = INF, -INF, 'inf', '-inf'
    assert all(math.isinf(v) for v in dm.inf)
    dm.nan = NAN, NAN, 'nan', 'nan'
    assert all(math.isnan(v) for v in dm.nan)
    dm.none = None, None, None, None
    assert all(v is None for v in dm.none)
    dm.s = 'alpha', 'beta', 'None', ''
    assert all(isinstance(v, str) for v in dm.s)
    def _():
        with pytest.raises(TypeError):
            dm.err = Exception, tuple, str, map
    _()


def check_mixedcolumn_sorting():

    dm = DataMatrix(length=24)
    dm.c = [
        1, '1', 2, '2',
        1.1, '1.1', 2.1, '2.1',
        INF, -INF, 'inf', '-inf',
        NAN, NAN, 'nan', 'nan',
        None, None, None, None,
        'alpha', 'beta', 'None', ''
    ]
    dm.c = ops.shuffle(dm.c)
    dm = ops.sort(dm, by=dm.c)
    check_col(dm.c, [
        -INF, -INF, 1, 1, 1.1, 1.1, 2, 2, 2.1, 2.1, INF, INF,
        '', 'None', 'alpha', 'beta',
        None, None, None, None,
        NAN, NAN, NAN, NAN,
    ])


def check_floatcolumn_typing():

    dm = DataMatrix(length=4, default_col_type=FloatColumn)
    dm.f = 1.1, '1.1', 1, '2'
    assert all(isinstance(v, float) for v in dm.f)
    dm.inf = INF, -INF, 'inf', '-inf'
    assert all(math.isinf(v) for v in dm.inf)
    dm.nan = NAN, NAN, 'nan', 'nan'
    assert all(math.isnan(v) for v in dm.nan)
    dm.none = None, None, None, None
    assert all(math.isnan(v) for v in dm.none)
    dm.s = 'alpha', 'beta', 'None', ' '
    assert all(math.isnan(v) for v in dm.s)
    def _():
        with pytest.raises(TypeError):
            dm.err = Exception, tuple, str, map
    _()


def check_floatcolumn_sorting():

    dm = DataMatrix(length=24, default_col_type=FloatColumn)
    dm.c = [
        1, '1', 2, '2',
        1.1, '1.1', 2.1, '2.1',
        INF, -INF, 'inf', '-inf',
        NAN, NAN, 'nan', 'nan',
        None, None, None, None,
        'alpha', 'beta', 'None', ''
    ]
    dm.c = ops.shuffle(dm.c)
    dm = ops.sort(dm, by=dm.c)
    check_col(dm.c, [
        -INF, -INF, 1, 1, 1.1, 1.1, 2, 2, 2.1, 2.1, INF, INF,
        NAN, NAN, NAN, NAN,
        NAN, NAN, NAN, NAN,
        NAN, NAN, NAN, NAN,
    ])


def check_intcolumn_typing():

    dm = DataMatrix(length=4, default_col_type=IntColumn)
    dm.f = 1.1, '1.8', 2, '2'
    assert all(isinstance(v, int) for v in dm.f)
    def _():
        with pytest.raises(TypeError):
            dm.inf = INF, -INF, 'inf', '-inf'
    _()
    def _():
        with pytest.raises(TypeError):
            dm.nan = NAN, NAN, 'nan', 'nan'
    _()
    def _():
        with pytest.raises(TypeError):
            dm.none = None, None, None, None
    _()
    def _():
        with pytest.raises(TypeError):
            dm.s = 'alpha', 'beta', 'None', ' '
    _()
    def _():
        with pytest.raises(TypeError):
            dm.err = Exception, tuple, str, map
    _()


def check_intcolumn_sorting():

    dm = DataMatrix(length=8, default_col_type=IntColumn)
    dm.c = [
        1, '1', 2, '2',
        1.1, '1.1', 2.1, '2.8',
    ]
    dm.c = ops.shuffle(dm.c)
    dm = ops.sort(dm, by=dm.c)
    check_col(dm.c, [
        1, 1, 1, 1, 2, 2, 2, 2
    ])


def test_typing_and_sorting():

    _basecolumn.sortable = _sort._sortable_fastnumbers
    check_mixedcolumn_typing()
    check_mixedcolumn_sorting()
    check_floatcolumn_typing()
    check_floatcolumn_sorting()
    check_intcolumn_typing()
    check_intcolumn_sorting()
    _basecolumn.sortable = _sort._sortable_regular
    check_mixedcolumn_typing()
    check_mixedcolumn_sorting()
    check_floatcolumn_typing()
    check_floatcolumn_sorting()
    check_intcolumn_typing()
    check_intcolumn_sorting()
