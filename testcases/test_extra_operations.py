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
from datamatrix import DataMatrix, MixedColumn, IntColumn, FloatColumn
from datamatrix import operations as ops
from testcases.test_tools import check_col, check_series, check_integrity
from nose.tools import eq_, ok_
import numpy as np


def weight():

	dm = DataMatrix(length=3)
	dm.a = 'a', 'b', 'c'
	dm.b = 1, 0, 2
	dm = ops.weight(dm.b)
	check_col(dm.a, ['a', 'c', 'c'])
	check_col(dm.b, [1, 2, 2])


def test_split():

	dm = DataMatrix(length=4)
	dm.a = 'a', 'a', 'b', 'b'
	dm.b = 0, 1, 2, 3
	g = ops.split(dm.a)
	val, dm = g.next()
	eq_(val, 'a')
	check_col(dm.a, ['a', 'a'])
	check_col(dm.b, [0, 1])
	val, dm = g.next()
	eq_(val, 'b')
	check_col(dm.a, ['b', 'b'])
	check_col(dm.b, [2, 3])


def test_tuple_split():

	dm = DataMatrix(length=4)
	dm.a = 'a', 'a', 'b', 'b'
	dm.b = 0, 1, 2, 3
	dma, dmb = ops.tuple_split(dm.a, 'a', 'b')
	check_col(dma.a, ['a', 'a'])
	check_col(dma.b, [0, 1])
	check_col(dmb.a, ['b', 'b'])
	check_col(dmb.b, [2, 3])


def test_fullfactorial():

	dm = DataMatrix(length=3)
	dm.a = 'a', 'b', ''
	dm.b = 0, 1, 2
	dm = ops.fullfactorial(dm)
	check_col(dm.a, ['a', 'b', 'a', 'b', 'a', 'b'])
	check_col(dm.b, [0, 0, 1, 1, 2, 2])


def test_group():

	dm = DataMatrix(length=4)
	dm.a = 'b', 'b', 'a', 'a'
	dm.b = 'x', 'x', 'x', 'y'
	dm.c = IntColumn
	dm.c = 0, 1, 2, 3
	dm = ops.group(dm, [dm.a, dm.b])
	check_series(dm.c, [[2, np.nan], [3, np.nan], [0, 1]])


def test_sort():

	dm = DataMatrix(length=2)
	dm.a = 'b', 'a'
	dm.b = 1, 0
	dm.a = ops.sort(dm.a)
	check_col(dm.a, ['a', 'b'])
	check_col(dm.b, [1, 0])
	dm = ops.sort(dm, by=dm.b)
	check_col(dm.a, ['b', 'a'])
	check_col(dm.b, [0, 1])


def test_shuffle():

	dm = DataMatrix(length=2)
	dm.a = 'a', 'b'
	dm.b = 0, 1
	while True:
		dm.a = ops.shuffle(dm.a)
		check_col(dm.b, [0, 1])
		try:
			check_col(dm.a, ['b', 'a'])
			break
		except:
			pass
	dm = DataMatrix(length=2)
	dm.a = 'a', 'b'
	dm.b = 0, 1
	while True:
		dm = ops.shuffle(dm)
		try:
			check_col(dm.a, ['b', 'a'])
			check_col(dm.b, [1, 0])
			break
		except:
			pass


def test_keep_only():

	dm = DataMatrix(length=2)
	dm.a = 'a', 'b'
	dm.b = 0, 1
	ops.keep_only(dm, ['b'])
	ok_('a' not in dm.column_names)
	ok_('b' in dm.column_names)


def test_auto_type():

	dm = DataMatrix(length=2)
	dm.a = 'a', 1
	dm.b = 0.1, 1
	dm.c = 0, 1
	ops.auto_type(dm)
	ok_(isinstance(dm.a, MixedColumn))
	ok_(isinstance(dm.b, FloatColumn))
	ok_(isinstance(dm.c, IntColumn))
