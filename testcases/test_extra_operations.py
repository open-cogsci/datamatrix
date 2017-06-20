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
from datamatrix import DataMatrix, MixedColumn, IntColumn, FloatColumn, \
	SeriesColumn
from datamatrix import operations as ops
from testcases.test_tools import check_col, check_row, check_series
from nose.tools import eq_, ok_, raises
import numpy as np


def test_replace():
	
	dm = DataMatrix(length=3)
	dm.a = 0, 1, 2
	dm.c = FloatColumn
	dm.c = np.nan, 1, 2
	dm.s = SeriesColumn(depth=3)
	dm.s[0] = 0, 1, 2
	dm.s[1] = np.nan, 1, 2
	dm.s[2] = np.nan, 1, 2
	dm.a = ops.replace(dm.a, {0 : 100, 2 : 200})
	dm.c = ops.replace(dm.c, {np.nan : 100, 2 : np.nan})
	dm.s = ops.replace(dm.s, {np.nan : 100, 2 : np.nan})
	check_col(dm.a, [100, 1, 200])
	check_col(dm.c, [100, 1, np.nan])
	check_series(dm.s, [
		[0, 1, np.nan],
		[100, 1, np.nan],
		[100, 1, np.nan],
		])


def test_z():

	dm = DataMatrix(length=5)
	dm.a = range(-2,3)
	dm.z = ops.z(dm.a)
	for x, y in zip(dm.z, [-1.26, -0.63, 0, .63, 1.26]):
		assert(abs(x-y) < .1)


def test_weight():

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
	# Without values
	g = ops.split(dm.a)
	val, dm = next(g)
	eq_(val, 'a')
	check_col(dm.a, ['a', 'a'])
	check_col(dm.b, [0, 1])
	val, dm = next(g)
	eq_(val, 'b')
	check_col(dm.a, ['b', 'b'])
	check_col(dm.b, [2, 3])	
	# With values
	dm = DataMatrix(length=4)
	dm.a = 'a', 'a', 'b', 'b'
	dm.b = 0, 1, 2, 3	
	dma, dmb = ops.split(dm.a, 'a', 'b')
	check_col(dma.a, ['a', 'a'])
	check_col(dma.b, [0, 1])
	check_col(dmb.a, ['b', 'b'])
	check_col(dmb.b, [2, 3])
	

def test_bin_split():

	dm = DataMatrix(length=4)
	dm.a = range(4)
	dm = ops.shuffle(dm)
	dm1, dm2 = ops.bin_split(dm.a, 2)
	check_col(dm1.a, [0,1])
	check_col(dm2.a, [2,3])
	dm1, dm2, dm3 = ops.bin_split(dm.a, 3)
	check_col(dm1.a, [0])
	check_col(dm2.a, [1])
	check_col(dm3.a, [2,3])
	dm1, = ops.bin_split(dm.a, 1)
	check_col(dm1.a, [0,1,2,3])
	@raises(ValueError)
	def _():
		x, = ops.bin_split(dm.a, 5)
	_()


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


def test_shuffle_horiz():

	dm = DataMatrix(length=2)
	dm.a = 'a', 'b'
	dm.b = 0, 1
	dm.c = '-', '-'
	while True:
		dm2 = ops.shuffle_horiz(dm)
		try:
			check_row(dm2[0], [0, '-', 'a'])
			break
		except:
			pass
	while True:
		dm2 = ops.shuffle_horiz(dm.a, dm.b)
		try:
			check_row(dm2[0], [0, 'a', '-'])
			break
		except:
			pass
	for i in range(1000):
		dm2 = ops.shuffle_horiz(dm.a, dm.b)
		check_col(dm.c, ['-', '-'])


def test_keep_only():

	dm = DataMatrix(length=2)
	dm.a = 'a', 'b'
	dm.b = 0, 1
	dm.c = 'y', 'z'
	for cols in (['b', 'c'], [dm.b, dm.c]):
		dm = ops.keep_only(dm, *cols)
		ok_('a' not in dm.column_names)
		ok_('b' in dm.column_names)
		ok_('c' in dm.column_names)


def test_auto_type():

	dm = DataMatrix(length=2)
	dm.a = 'a', 1
	dm.b = 0.1, 1
	dm.c = 0, 1
	dm = ops.auto_type(dm)
	ok_(isinstance(dm.a, MixedColumn))
	ok_(isinstance(dm.b, FloatColumn))
	ok_(isinstance(dm.c, IntColumn))


def test_map_():
	
	for coltype in (MixedColumn, FloatColumn, IntColumn):
		dm = DataMatrix(length=2, default_col_type=coltype)
		dm.a = 1, 2
		dm.a = ops.map_(lambda x: x*2, dm.a)
		eq_(dm.a, [2, 4])
		ok_(isinstance(dm.a, coltype))
		dm = ops.map_(lambda **d: {'a' : 0}, dm)
		eq_(dm.a, [0, 0])
		ok_(isinstance(dm.a, coltype))
		

def test_filter_():
	
	dm = DataMatrix(length=4)
	dm.a = range(4)
	odd = ops.filter_(lambda x: x%2, dm.a)
	ok_(all([x%2 for x in odd]))
	print(type(dm._rowid))
	dm = ops.filter_(lambda **d: d['a']%2, dm)
	print(type(dm._rowid))
	eq_(dm.a, [1, 3])
