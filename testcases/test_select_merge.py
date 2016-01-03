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

from datamatrix import DataMatrix, MixedColumn, FloatColumn, IntColumn

def check_select(col_type):

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


def test_mixedcolumn():

	check_select(MixedColumn)


def test_floatcolumn():

	check_select(FloatColumn)


def test_intcolumn():

	check_select(IntColumn)
