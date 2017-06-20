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
from datamatrix import DataMatrix, MixedColumn, FloatColumn, IntColumn	
from testcases.test_tools import all_nan
from nose.tools import eq_
import numpy as np


def _test_numeric_properties(coltype, nan):
	
	dm = DataMatrix(length=4, default_col_type=coltype)
	dm.c = 1, 1, nan, 4
	dm.d = [nan]*4
	eq_(dm.c.mean, 2)
	eq_(dm.c.median, 1)
	eq_(dm.c.std, np.std([1,1,4], ddof=1))
	eq_(dm.c.max, 4)
	eq_(dm.c.min, 1)
	eq_(dm.c.sum, 6)
	all_nan(dm.d.mean, nan)
	all_nan(dm.d.median, nan)
	all_nan(dm.d.std, nan)
	all_nan(dm.d.max, nan)
	all_nan(dm.d.min, nan)
	all_nan(dm.d.sum, nan)
	
	
def _test_basic_properties(coltype):
	
	dm = DataMatrix(length=4, default_col_type=coltype)
	dm.c = 3,1,2,3
	dm.d = dm.c
	dm.e = 3,1,2,3
	eq_(dm.c.name, ['c', 'd'])
	eq_(dm.d.name, ['c', 'd'])
	eq_(dm.e.name, 'e')
	eq_(list(dm.c.unique), [1,2,3])
	eq_(dm.c.count, 3)
	
	
def test_intcolumn():
	
	_test_basic_properties(IntColumn)


def test_floatcolumn():
	
	_test_numeric_properties(FloatColumn, np.nan)
	_test_basic_properties(FloatColumn)
	
	
def test_mixedcolumn():
	
	_test_numeric_properties(MixedColumn, float('nan'))
	_test_basic_properties(MixedColumn)
