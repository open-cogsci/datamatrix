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
from testcases.test_tools import check_col, check_series, check_integrity
from nose.tools import ok_, raises
import numpy as np

def test_mixedcolumn():

	dm = DataMatrix(length=2)
	# Test assignment
	dm.col = 1
	check_col(dm.col, [1, 1])
	dm.col = 2, 3
	check_col(dm.col, [2, 3])
	dm.col[:-1] = 4
	check_col(dm.col, [4, 3])
	dm.col[:] = 'test'	
	check_col(dm.col, ['test', 'test'])
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 4
	# Check uniqueness
	dm.col = 1,2,1,2
	ok_(sorted(dm.col.unique) == [1,2])
	check_integrity(dm)


def test_floatcolumn():

	dm = DataMatrix(length=2)
	# Test assignment
	dm.col = FloatColumn
	dm.col = 1
	check_col(dm.col, [1, 1])
	dm.col = 2, 3
	check_col(dm.col, [2, 3])
	dm.col[:-1] = 4
	check_col(dm.col, [4, 3])
	dm.col[:] = 'test'
	for value in dm.col:
		ok_(np.isnan(value))
	# Test nans and infs
	dm.col = 'nan', 'inf'
	check_col(dm.col, [np.nan, np.inf])
	dm.col = np.nan, np.inf
	check_col(dm.col, [np.nan, np.inf])
	dm.col = 'x', None
	check_col(dm.col, [np.nan, np.nan])
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 4
	# Check uniqueness
	dm.col = 1,2,1,2
	ok_(sorted(dm.col.unique) == [1,2])
	# Check dtype
	ok_(dm.col._seq.dtype == np.float64)
	check_integrity(dm)


def test_intcolumn():

	dm = DataMatrix(length=2)
	# Test assignment
	dm.col = IntColumn
	dm.col = 1
	check_col(dm.col, [1, 1])
	dm.col = 2, '3'
	check_col(dm.col, [2, 3])
	dm.col[:-1] = '4'
	check_col(dm.col, [4, 3])
	@raises(TypeError)
	def _():
		dm.col[0] = 'test'
	_()
	@raises(TypeError)
	def _():
		dm.col[:] = 'test'
	_()
	@raises(TypeError)
	def _():
		dm.col[0] = None
	_()
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 4
	# Check uniqueness
	dm.col = 1,2,1,2
	ok_(sorted(dm.col.unique) == [1,2])
	# Check dtype
	ok_(dm.col._seq.dtype == np.int64)
	check_integrity(dm)

def test_seriescolumn():

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
	check_series(dm.col, [[1,0,0], [2,0,0], [3,0,0]])
	check_integrity(dm)


def test_resize():
	
	dm = DataMatrix(length=0)
	for l in range(1, 11):
		print('growing to %d' % l)
		dm.length += 1
		for x, y in zip(dm._rowid, range(l)):
			print(x, y)
			ok_(x == y)
	for l in range(10, 0, -1):
		print('shrinking to %d' % l)
		dm.length -= 1
		for x, y in zip(dm._rowid, range(l)):
			print(x, y)
			ok_(x == y)
