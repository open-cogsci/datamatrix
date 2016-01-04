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
from nose.tools import eq_, ok_
import numpy as np

def check_operations(col_type):

	dm = DataMatrix(length=2, default_col_type=col_type)
	dm.col = 1, 2
	dm.col += 1
	eq_(list(dm.col), [2, 3])
	dm.col += 1, 2
	eq_(list(dm.col), [3, 5])
	dm.col -= 1
	eq_(list(dm.col), [2, 4])
	dm.col -= 1, 2
	eq_(list(dm.col), [1, 2])
	dm.col *= 2
	eq_(list(dm.col), [2, 4])
	dm.col *= 1.5, 3
	eq_(list(dm.col), [3, 12])
	dm.col /= 3
	eq_(list(dm.col), [1, 4])
	dm.col /= 1, 2
	eq_(list(dm.col), [1, 2])
	dm.col //= 1.5, 2.5
	eq_(list(dm.col), [0, 0])


def check_int_operations():

	dm = DataMatrix(length=2, default_col_type=IntColumn)
	dm.col = 1.5, 2.5
	eq_(list(dm.col), [1, 2])
	dm.col *= 1.5
	eq_(list(dm.col), [1, 3])


def check_str_operations():

	dm = DataMatrix(length=2, default_col_type=MixedColumn)
	dm.col = 'a', 'b'
	eq_(list(dm.col), ['a', 'b'])
	dm.col += 'c', 'd'
	eq_(list(dm.col), ['ac', 'bd'])


def test_seriescolumn():

	def check(ref):
		for i, j in zip(dm.col, ref):
			ok_(all(i == j))

	dm = DataMatrix(length=2)
	dm.col = SeriesColumn(depth=2)
	dm.col[0] = 1, 2
	dm.col[1] = 3, 4
	dm.col += 1
	check([[2,3], [4,5]])
	dm.col += 1, 2
	check([[3,4], [6,7]])
	dm.col -= 1
	check([[2,3], [5,6]])
	dm.col -= 1, 2
	check([[1,2], [3,4]])
	dm.col *= 2
	check([[2,4], [6,8]])
	dm.col *= 1.5, 3
	check([[3,6], [18,24]])
	dm.col /= 3
	check([[1,2], [6,8]])
	dm.col /= 1, 2
	check([[1,2], [3,4]])
	dm.col //= 1.5, 2.5
	check([[0,1], [1,1]])
	dm.col += np.array([
		[0,0],
		[10, 10]
		])
	check([[0,1], [11,11]])


def test_mixedcolumn():

	check_operations(MixedColumn)
	check_str_operations()


def test_floatcolumn():

	check_operations(FloatColumn)


def test_intcolumn():

	check_operations(IntColumn)
	check_int_operations()
