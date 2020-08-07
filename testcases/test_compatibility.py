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
	DataMatrix, MixedColumn, FloatColumn, IntColumn,
	SeriesColumn, NAN
)
from testcases.test_tools import check_col
import pytest
import numpy as np


def _test_numpy(cls):
    
    a = np.array([1, 2, 3, 4])
    dm = DataMatrix(length=4)
    dm.col = cls
    dm.col = a
    assert np.mean(dm.col) == np.mean(a)
    assert np.std(dm.col) == np.std(a, ddof=1)
    assert np.median(dm.col) == np.median(a)
    assert np.min(dm.col) == np.min(a)
    assert np.max(dm.col) == np.max(a)
    assert np.sum(dm.col) == np.sum(a)    
    assert np.mean(dm.col) == dm.col.mean
    assert np.std(dm.col) == dm.col.std
    assert np.median(dm.col) == dm.col.median
    assert np.min(dm.col) == dm.col.min
    assert np.max(dm.col) == dm.col.max
    assert np.sum(dm.col) == dm.col.sum


def _test_equals(cls):
    
    dm1 = DataMatrix(length=4)
    dm1.col = cls
    dm1.col = 1, 2, 3, NAN
    dm2 = DataMatrix(length=4)
    dm2.col = cls
    dm2.col = 1, 2, 3, NAN
    dm3 = DataMatrix(length=4)
    dm3.col = cls
    dm3.col = 1, 2, NAN, 3
    assert dm1[2].equals(dm2[2])
    assert not dm1[2].equals(dm3[2])
    

def test_mixedcolumn():
    
    _test_numpy(MixedColumn)
    _test_equals(MixedColumn)
    
    
def test_floatcolumn():
    
    _test_numpy(FloatColumn)
    _test_equals(FloatColumn)


def test_intcolumn():
    
    _test_numpy(IntColumn)
