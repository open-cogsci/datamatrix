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

from datamatrix import DataMatrix, MixedColumn, FloatColumn, IntColumn, \
	SeriesColumn
import numpy as np

def test_mixedcolumn():

	dm = DataMatrix(length=2)
	# Test assignment
	dm.col = 1
	assert(list(dm.col) == [1, 1])
	dm.col = 2, 3
	assert(list(dm.col) == [2, 3])
	dm.col[:-1] = 4
	assert(list(dm.col) == [4, 3])
	dm.col[:] = 'test'
	assert(list(dm.col) == ['test', 'test'])
	# Test normal arithmatic
	dm.col = 0
	dm.col += 4
	dm.col -= 2
	dm.col *= 2.5
	dm.col /= 8
	assert(list(dm.col) == [.625, .625])
	# Test floor division
	dm.col = 2
	dm.col //= 1.5
	assert(list(dm.col) == [1, 1])
	# Test string concatenation
	dm.col = 'a'
	dm.col += 'b'
	assert(list(dm.col) == ['ab', 'ab'])
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 4
	# Test statistics
	dm.col = [1, 2, 4, 'test']
	assert(dm.col.mean == 7./3)
	assert(dm.col.median == 2)
	assert(dm.col.max == 4)
	assert(dm.col.min == 1)
	assert(dm.col.std == np.std([1, 2, 4], ddof=1))


def test_floatcolumn():

	dm = DataMatrix(length=2)
	# Test assignment
	dm.col = FloatColumn
	dm.col = 1
	assert(list(dm.col) == [1, 1])
	dm.col = 2, 3
	assert(list(dm.col) == [2, 3])
	dm.col[:-1] = 4
	assert(list(dm.col) == [4, 3])
	dm.col[:] = 'test'
	for value in dm.col:
		assert(np.isnan(value))
	# Test normal arithmatic
	dm.col = 0
	dm.col += 4
	dm.col -= 2
	dm.col *= 2.5
	dm.col /= 8
	assert(list(dm.col) == [.625, .625])
	# Test floor division
	dm.col = 2
	dm.col //= 1.5
	assert(list(dm.col) == [1, 1])
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 4
	# Test statistics
	dm.col = [1, 2, 4, np.nan]
	assert(dm.col.mean == 7./3)
	assert(dm.col.median == 2)
	assert(dm.col.max == 4)
	assert(dm.col.min == 1)
	assert(dm.col.std == np.std([1, 2, 4], ddof=1))
	# Check dtype
	assert(dm.col._seq.dtype == np.float64)


def test_intcolumn():

	dm = DataMatrix(length=2)
	# Test assignment
	dm.col = IntColumn
	dm.col = 1
	assert(list(dm.col) == [1, 1])
	dm.col = 2, 3
	assert(list(dm.col) == [2, 3])
	dm.col[:-1] = 4
	assert(list(dm.col) == [4, 3])
	try:
		dm.col[0] = 'test'
	except TypeError:
		pass
	else:
		assert(False)
	try:
		dm.col[:] = 'test'
	except TypeError:
		pass
	else:
		assert(False)
	# Test normal arithmatic
	dm.col = 0
	dm.col += 4
	dm.col -= 2
	dm.col *= 2.5
	dm.col /= 8
	assert(list(dm.col) == [0, 0])
	# Test floor division
	dm.col = 2
	dm.col //= 1.5
	assert(list(dm.col) == [1, 1])
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 3
	# Test statistics
	dm.col = [1, 2, 4]
	assert(dm.col.mean == 7./3)
	assert(dm.col.median == 2)
	assert(dm.col.max == 4)
	assert(dm.col.min == 1)
	assert(dm.col.std == np.std([1, 2, 4], ddof=1))
	# Check dtype
	assert(dm.col._seq.dtype == np.int64)


def test_seriescolumn():

	def check(ref):
		for i, j in zip(dm.col, ref):
			assert(all(i == j))

	dm = DataMatrix(length=2)
	dm.col = SeriesColumn(dm, depth=3)
	# Set all rows to a single value
	dm.col = 1
	check([[1,1,1], [1,1,1]])
	# Set rows to different single values
	dm.col = 2, 3
	check([[2,2,2], [3,3,3]])
	# Set one row to a single value
	dm.col[0] = 4
	check([[4,4,4], [3,3,3]])
	# Set one row to different single values
	dm.col[1] = 5, 6, 7
	check([[4,4,4], [5,6,7]])
	# Set all rows to different single values
	dm.col.setallrows([8,9,10])
	check([[8,9,10], [8,9,10]])
	# Set the first value in all rows
	dm.col[:,0] = 1
	check([[1,9,10], [1,9,10]])
	# Set all values in the first row
	dm.col[0,:] = 2
	check([[2,2,2], [1,9,10]])
	# Set all values
	dm.col[:,:] = 3
	check([[3,3,3], [3,3,3]])
	# Test shortening and lengthening
	dm.length = 0
	dm.length = 3
	# Test statistics
	dm.col[0] = [1,2,3]
	dm.col[1] = [3,3,3]
	dm.col[2] = [4,4,4]
	assert(all(dm.col.mean == [8./3, 9./3, 10/3.]))
	assert(all(dm.col.median == [3,3,3]))
	assert(all(dm.col.max == [4,4,4]))
	assert(all(dm.col.min == [1,2,3]))
	assert(all(dm.col.std == [
		np.std([4,3,1], ddof=1),
		np.std([4,3,2], ddof=1),
		np.std([4,3,3], ddof=1)
		]))


def test_select():

	def check(col_type):

		dm = DataMatrix(length=2, default_col_type=col_type)
		dm.col = 1, 2
		dm_ = dm.col < 2
		assert(list(dm_.col) == [1])
		dm_ = dm.col == 2
		assert(list(dm_.col) == [2])
		dm_ = (dm.col == 1) | (dm.col == 2)
		assert(list(dm_.col) == [1,2])
		dm_ = (dm.col == 1) & (dm.col == 2)
		assert(list(dm_.col) == [])
		dm_ = (dm.col == 1) ^ (dm.col == 2)
		assert(list(dm_.col) == [1,2])

	check(MixedColumn)
	check(FloatColumn)
	check(IntColumn)

def test_iteration():

	def check(col_type):

		dm = DataMatrix(length=2, default_col_type=col_type)
		dm.col1 = 1, 2
		dm.col2 = 3, 4
		# Row iteration
		ref = [
			[('col1', 1), ('col2', 3)],
			[('col1', 2), ('col2', 4)]
			]
		for row, rowref in zip(dm, ref):
			assert(list(row) == rowref)
		# Column iteration
		ref = [
			('col1', [1,2]),
			('col2', [3,4])
			]
		for (name, col), (ref_name, ref_col) in zip(dm.columns, ref):
			assert(name == ref_name)
			assert(list(col) == ref_col)
		# Cells within column iteration
		ref = [1,2]
		for val, ref_val in zip(dm.col1, ref):
			assert(val == ref_val)
		# Cells within row iteration
		ref = [
			('col1', 1),
			('col2', 3)
			]
		for (name, val), (ref_name, ref_val) in zip(dm[0], ref):
			assert(val == ref_val)
			assert(name == ref_name)

	check(MixedColumn)
	check(FloatColumn)
	check(IntColumn)


if __name__ == u'__main__':
	test_mixedcolumn()
	test_floatcolumn()
	test_intcolumn()
	test_seriescolumn()
	test_select()
	test_iteration()
