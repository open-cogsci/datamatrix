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
from nose.tools import eq_, ok_
from nose.tools import assert_almost_equal as aeq

def check_odd(dm):

	aeq(dm.col.mean, 13./3)
	eq_(dm.col.median, 2)
	aeq(dm.col.std, np.std( [1,2,10], ddof=1 ))
	eq_(dm.col.min, 1)
	eq_(dm.col.max, 10)
	eq_(dm.col.sum, 13)


def check_even(dm):

	aeq(dm.col.mean, 4)
	eq_(dm.col.median, 2.5)
	aeq(dm.col.std, np.std( [1,2,3,10], ddof=1 ))
	eq_(dm.col.min, 1)
	eq_(dm.col.max, 10)
	eq_(dm.col.sum, 16)


def check_desc_stats(col_type, invalid, assert_invalid):

	dm = DataMatrix(length=4, default_col_type=col_type)
	# Even lengths
	dm.col = 1, 2, 3, 10
	check_even(dm)
	if col_type is not IntColumn:
		dm.length = 5
		dm.col = 1, 2, 3, 10, invalid
		check_even(dm)
	# Odd lengths (and even with one invalid)
	dm.length = 3
	dm.col = 1, 2, 10
	check_odd(dm)
	if col_type is not IntColumn:
		dm.length = 4
		dm.col[3] = invalid
		check_odd(dm)
	# One lengths
	dm.length = 1
	dm.col = 1
	eq_(dm.col.mean, 1)
	eq_(dm.col.median, 1)
	assert_invalid(dm.col.std)
	eq_(dm.col.min, 1)
	eq_(dm.col.max, 1)
	eq_(dm.col.sum, 1)
	# Zero lengths
	dm.length = 0
	assert_invalid(dm.col.mean)
	assert_invalid(dm.col.median)
	assert_invalid(dm.col.std)
	assert_invalid(dm.col.min)
	assert_invalid(dm.col.max)
	assert_invalid(dm.col.sum)

def assert_None(val):

	ok_(val is None)


def assert_nan(val):

	ok_(np.isnan(val))


def test_seriescolumn():

	dm = DataMatrix(length=3)
	dm.col = SeriesColumn(depth=3)
	dm.col[0] = [1,2,3]
	dm.col[1] = [3,3,3]
	dm.col[2] = [4,4,4]
	ok_(all(dm.col.mean == [8./3, 9./3, 10/3.]))
	ok_(all(dm.col.median == [3,3,3]))
	ok_(all(dm.col.max == [4,4,4]))
	ok_(all(dm.col.min == [1,2,3]))
	ok_(all(dm.col.std == [
		np.std([4,3,1], ddof=1),
		np.std([4,3,2], ddof=1),
		np.std([4,3,3], ddof=1)
		]))


def test_mixedcolumn():

	check_desc_stats(MixedColumn, invalid=None, assert_invalid=assert_None)


def test_floatcolumn():

	check_desc_stats(FloatColumn, invalid=np.nan, assert_invalid=assert_nan)


def test_intcolumn():

	check_desc_stats(IntColumn, invalid=np.nan, assert_invalid=assert_nan)
