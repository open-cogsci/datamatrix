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
from datamatrix import DataMatrix, MixedColumn, FloatColumn, IntColumn, SeriesColumn
from nose.tools import raises
from testcases.test_tools import check_col, check_series, check_integrity
import numpy as np


def check_operations(col_type):

	dm = DataMatrix(length=2, default_col_type=col_type)
	dm.col = 1, '2'
	dm.col += 1
	check_col(dm.col, [2, 3])
	dm.col += 1, '2'
	check_col(dm.col, [3, 5])
	dm.col -= 1
	check_col(dm.col, [2, 4])
	dm.col -= 1, '2'
	check_col(dm.col, [1, 2])
	dm.col *= 2
	check_col(dm.col, [2, 4])
	dm.col *= 1, '2'
	check_col(dm.col, [2, 8])
	dm.col /= 2
	check_col(dm.col, [1, 4])
	dm.col /= 1, '2'
	check_col(dm.col, [1, 2])
	# Right-hand operations
	dm.col = 1 + dm.col
	check_col(dm.col, [2, 3])
	dm.col = (1, 2) + dm.col
	check_col(dm.col, [3, 5])
	dm.col = 5 - dm.col
	check_col(dm.col, [2, 0])
	dm.col = (3, 1) - dm.col
	check_col(dm.col, [1, 1])
	dm.col = 2 * dm.col
	check_col(dm.col, [2, 2])
	dm.col = (1, 2) * dm.col
	check_col(dm.col, [2, 4])
	dm.col = 4 / dm.col
	check_col(dm.col, [2, 1])
	dm.col = (4, 2) / dm.col
	check_col(dm.col, [2, 2])
	dm.col = 2 ** dm.col
	check_col(dm.col, [4, 4])
	dm.col = (2, 4) ** dm.col
	check_col(dm.col, [16, 256])
	dm.col = 17 % dm.col
	check_col(dm.col, [1, 17])
	dm.col = (2, 16) % dm.col
	check_col(dm.col, [0, 16])
	check_integrity(dm)


def check_int_operations():

	dm = DataMatrix(length=2, default_col_type=IntColumn)
	dm.col = 1.5, 2.5
	check_col(dm.col, [1, 2])
	dm.col *= 2.5
	check_col(dm.col, [2, 4])
	@raises(TypeError)
	def _():
		dm.col *= 'x'
	_()
	check_integrity(dm)


def check_float_operations():

	dm = DataMatrix(length=2, default_col_type=FloatColumn)
	dm.col = 1, 2
	check_col(dm.col, [1, 2])
	dm.col *= 2.5
	check_col(dm.col, [2.5, 5])
	dm.col *= np.inf, np.nan
	check_col(dm.col, [np.inf, np.nan])
	check_integrity(dm)


def check_str_operations():

	dm = DataMatrix(length=2, default_col_type=MixedColumn)
	dm.col = 'a', 'b'
	check_col(dm.col, ['a', 'b'])
	dm.col += 'c', 'd'
	check_col(dm.col, ['ac', 'bd'])
	check_integrity(dm)


def test_seriescolumn():

	dm = DataMatrix(length=2)
	dm.col = SeriesColumn(depth=2)
	dm.col[0] = 1, 2
	dm.col[1] = 3, 4
	dm.col += 1
	check_series(dm.col, [[2,3], [4,5]])
	dm.col += 1, 2
	check_series(dm.col, [[3,4], [6,7]])
	dm.col -= 1
	check_series(dm.col, [[2,3], [5,6]])
	dm.col -= 1, 2
	check_series(dm.col, [[1,2], [3,4]])
	dm.col *= 2
	check_series(dm.col, [[2,4], [6,8]])
	dm.col *= 1.5, 3
	check_series(dm.col, [[3,6], [18,24]])
	dm.col /= 3
	check_series(dm.col, [[1,2], [6,8]])
	dm.col /= 1, 2
	check_series(dm.col, [[1,2], [3,4]])
	dm.col //= 1.5, 2.5
	check_series(dm.col, [[0,1], [1,1]])
	dm.col += np.array([
		[0,0],
		[10, 10]
		])
	check_series(dm.col, [[0,1], [11,11]])


def test_mixedcolumn():

	check_operations(MixedColumn)
	check_str_operations()


def test_floatcolumn():

	check_operations(FloatColumn)
	check_float_operations()


def test_intcolumn():

	check_int_operations()
	check_operations(IntColumn)
