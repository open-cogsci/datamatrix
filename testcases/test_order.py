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
	operations, SeriesColumn
from testcases.test_tools import check_col, check_integrity
import numpy as np


def check_sort(col_type):

	dm = DataMatrix(length=3, default_col_type=col_type)
	dm.col1 = 3,2,1
	dm.col2 = 1,2,3
	dm = operations.sort(dm, by=dm.col1)
	check_col(dm.col1, [1, 2, 3])
	check_col(dm.col2, [3, 2, 1])
	dm = operations.sort(dm, by=dm.col2)
	check_col(dm.col1, [3, 2, 1])
	check_col(dm.col2, [1, 2, 3])
	dm.col2 = operations.sort(dm.col2, by=dm.col1)
	check_col(dm.col2, [3, 2, 1])
	dm.col1 = operations.sort(dm.col1)
	dm.col2 = operations.sort(dm.col2)
	check_col(dm.col1, [1, 2, 3])
	check_col(dm.col2, [1, 2, 3])
	check_integrity(dm)


def check_nan_sort():

	dm = DataMatrix(length=3, default_col_type=FloatColumn)
	dm.col1 = 2,np.nan,1
	dm.col2 = 1,2,np.nan
	dm = operations.sort(dm, by=dm.col1)
	check_col(dm.col1, [1, 2, np.nan])
	check_col(dm.col2, [np.nan, 1, 2])
	dm = operations.sort(dm, by=dm.col2)
	check_col(dm.col1, [2, np.nan, 1])
	check_col(dm.col2, [1, 2, np.nan])
	dm.col1 = operations.sort(dm.col1)
	dm.col2 = operations.sort(dm.col2)
	check_col(dm.col1, [1, 2, np.nan])
	check_col(dm.col2, [1, 2, np.nan])
	check_integrity(dm)

def check_shuffle(col_type):

	dm = DataMatrix(length=3, default_col_type=col_type)
	dm.col1 = 11,12,13
	dm.col2 = 1,2,3
	dm = operations.shuffle(dm)
	for row in dm:
		assert row.col1 == row.col2+10
	dm.col1 = operations.shuffle(dm.col1)
	dm.col2 = operations.shuffle(dm.col2)
	check_integrity(dm)

def test_sort():

	check_sort(MixedColumn)
	check_sort(FloatColumn)
	check_sort(IntColumn)
	check_shuffle(MixedColumn)
	check_shuffle(FloatColumn)
	check_shuffle(IntColumn)
	check_nan_sort()
