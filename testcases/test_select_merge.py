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
from nose.tools import ok_

def check_select(col_type):

	dm = DataMatrix(length=2, default_col_type=col_type)
	dm.col = 1, 2
	dm_ = dm.col < 2
	ok_(list(dm_.col) == [1])
	dm_ = dm.col == 2
	ok_(list(dm_.col) == [2])
	dm_ = (dm.col == 1) | (dm.col == 2)
	ok_(list(dm_.col) == [1,2])
	dm_ = (dm.col == 1) & (dm.col == 2)
	ok_(list(dm_.col) == [])
	dm_ = (dm.col == 1) ^ (dm.col == 2)
	ok_(list(dm_.col) == [1,2])


def check_concat(col_type, invalid):

	dm1 = DataMatrix(length=2, default_col_type=col_type)
	dm1.col1 = 1, 2
	dm1.col_shared = 3, 4
	dm2 = DataMatrix(length=2, default_col_type=col_type)
	dm2.col2 = 5, 6
	dm2.col_shared = 7, 8
	dm3 = dm1 << dm2
	ok_(list(dm3.col1) == [1,2,invalid,invalid])
	ok_(list(dm3.col_shared) == [3,4,7,8])
	ok_(list(dm3.col2) == [invalid,invalid,5,6])


def test_mixedcolumn():

	check_select(MixedColumn)
	check_concat(MixedColumn, invalid=None)


def test_floatcolumn():

	check_select(FloatColumn)
	check_concat(FloatColumn, invalid=0)


def test_intcolumn():

	check_select(IntColumn)
	check_concat(IntColumn, invalid=0)


def test_seriescolumn():

	def check(col, ref):
		for i, j in zip(col, ref):
			ok_(all(i == j))

	dm1 = DataMatrix(length=2)
	dm1.col1 = SeriesColumn(2)
	dm1.col1 = 1, 2
	dm1.col_shared = SeriesColumn(2)
	dm1.col_shared = 3, 4
	dm2 = DataMatrix(length=2)
	dm2.col2 = SeriesColumn(2)
	dm2.col2 = 5, 6
	dm2.col_shared = SeriesColumn(2)
	dm2.col_shared = 7, 8
	dm3 = dm1 << dm2
	check(dm3.col1, [[1,1],[2,2],[0,0],[0,0]])
	check(dm3.col_shared, [[3,3],[4,4],[7,7],[8,8]])
	check(dm3.col2, [[0,0],[0,0],[5,5],[6,6]])
