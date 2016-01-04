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

def check_iteration(col_type):

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


def test_iteration():

	check_iteration(MixedColumn)
	check_iteration(FloatColumn)
	check_iteration(IntColumn)
