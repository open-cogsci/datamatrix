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
from nose.tools import raises, eq_
from testcases.test_tools import check_col, check_series, check_integrity
import numpy as np


def check_select(col_type):

	dm = DataMatrix(length=2, default_col_type=col_type)
	dm.col = 1, 2
	dm_ = dm.col < 2
	check_col(dm_.col, [1])
	dm_ = dm.col == 2
	check_col(dm_.col, [2])
	dm_ = (dm.col == 1) | (dm.col == 2) # or
	check_col(dm_.col, [1,2])
	dm_ = (dm.col == 1) & (dm.col == 2) # and
	check_col(dm_.col, [])
	dm_ = (dm.col == 1) ^ (dm.col == 2) # xor
	check_col(dm_.col, [1,2])
	# Pair-wise select by matching-length sequence
	dm_ = dm.col == (1,3)
	check_col(dm_.col, [1])
	# Check by set multimatching
	dm_ = dm.col == {2, 3, 4}
	check_col(dm_.col, [2])
	dm_ = dm.col != {1, 3, 4}
	check_col(dm_.col, [2])
	# Check by lambda comparison
	dm_ = dm.col == (lambda x: x == 2)
	check_col(dm_.col, [2])
	dm_ = dm.col != (lambda x: x == 2)
	check_col(dm_.col, [1])
	check_integrity(dm)


def check_getrow(col_type):

	dm = DataMatrix(length=2, default_col_type=col_type)
	dm.col = 1, 2
	row = dm[0]
	assert(row.col == 1)
	row = dm[-1]
	assert(row.col == 2)
	@raises(IndexError)
	def _():
		row = dm[2]
	_()
	@raises(IndexError)
	def _():
		row = dm[-3]
	_()


def check_concat(col_type, invalid):

	dm1 = DataMatrix(length=2, default_col_type=col_type)
	dm1.col1 = 1, 2
	dm1.col_shared = 3, 4
	dm2 = DataMatrix(length=2, default_col_type=col_type)
	dm2.col2 = 5, 6
	dm2.col_shared = 7, 8
	dm3 = dm1 << dm2
	check_col(dm3.col1, [1,2,invalid,invalid])
	check_col(dm3.col_shared, [3,4,7,8])
	check_col(dm3.col2, [invalid,invalid,5,6])


def test_mixedcolumn():

	check_getrow(MixedColumn)
	check_select(MixedColumn)
	check_concat(MixedColumn, invalid=u'')
	# Check type selectors
	dm = DataMatrix(length=6)
	dm.col = 1, 2, 3, 1.1, 2.1, 'a'
	eq_(len(dm.col == float), 2)
	eq_(len(dm.col != float), 4)
	eq_(len(dm.col == str), 1)
	eq_(len(dm.col != str), 5)
	eq_(len(dm.col == int), 3)
	eq_(len(dm.col != int), 3)


def test_floatcolumn():

	check_getrow(FloatColumn)
	check_select(FloatColumn)
	check_concat(FloatColumn, invalid=np.nan)
	# Check selections with non-int types
	dm = DataMatrix(length=4, default_col_type=FloatColumn)
	dm.col = 1, 2, np.nan, np.inf
	dm2 = dm.col == '1'
	check_col(dm2.col, [1])
	dm2 = dm.col == ''
	check_col(dm2.col, [np.nan])
	dm2 = dm.col != ''
	check_col(dm2.col, [1, 2, np.inf])
	dm2 = dm.col == np.nan
	check_col(dm2.col, [np.nan])
	dm2 = dm.col != np.nan
	check_col(dm2.col, [1, 2, np.inf])
	dm2 = dm.col == np.inf
	check_col(dm2.col, [np.inf])
	dm2 = dm.col != np.inf
	check_col(dm2.col, [1, 2, np.nan])
	@raises(TypeError)
	def _():
		dm.col > ''
	_()
	# Check type selectors
	dm = DataMatrix(length=2, default_col_type=FloatColumn)
	dm.col = 1, 2
	eq_(len(dm.col == float), 2)
	eq_(len(dm.col != float), 0)
	eq_(len(dm.col == str), 0)
	eq_(len(dm.col != str), 2)
	eq_(len(dm.col == int), 0)
	eq_(len(dm.col != int), 2)


def test_intcolumn():

	check_getrow(IntColumn)
	check_select(IntColumn)
	check_concat(IntColumn, invalid=0)
	# Check selections with non-int types
	dm = DataMatrix(length=2, default_col_type=IntColumn)
	dm.col = 1, 2
	dm2 = dm.col == '1.1' # Floored to 1
	check_col(dm2.col, [1])
	dm2 = dm.col == ''
	check_col(dm2.col, [])
	dm2 = dm.col != ''
	check_col(dm2.col, [1, 2])
	@raises(TypeError)
	def _():
		dm.col > ''
	_()
	# Check type selectors
	dm = DataMatrix(length=2, default_col_type=IntColumn)
	dm.col = 1, 2
	eq_(len(dm.col == int), 2)
	eq_(len(dm.col != int), 0)
	eq_(len(dm.col == float), 0)
	eq_(len(dm.col != float), 2)
	eq_(len(dm.col == str), 0)
	eq_(len(dm.col != str), 2)

def test_seriescolumn():

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
	check_series(dm3.col1, [[1,1],[2,2],[np.nan,np.nan],[np.nan,np.nan]])
	check_series(dm3.col_shared, [[3,3],[4,4],[7,7],[8,8]])
	check_series(dm3.col2, [[np.nan,np.nan],[np.nan,np.nan],[5,5],[6,6]])
	dm3.i = [4,0,2,1]
	dm4 = dm3.i <= 2
	dm5 = (dm3.i <= 2) | (dm3.i >= 3)
	check_integrity(dm1)
	check_integrity(dm2)
	check_integrity(dm3)
	check_integrity(dm4)
	check_integrity(dm5)
