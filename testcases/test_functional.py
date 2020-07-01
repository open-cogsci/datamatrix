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
from datamatrix import functional as fnc
from testcases.test_tools import capture_stdout


def test_map_():

	for coltype in (MixedColumn, FloatColumn, IntColumn):
		dm = DataMatrix(length=2, default_col_type=coltype)
		dm.a = 1, 2
		dm.a = fnc.map_(lambda x: x*2, dm.a)
		assert dm.a == [2, 4]
		assert isinstance(dm.a, coltype)
		dm = fnc.map_(lambda **d: {'a' : 0}, dm)
		assert dm.a == [0, 0]
		assert isinstance(dm.a, coltype)


def test_filter_():

	dm = DataMatrix(length=4)
	dm.a = range(4)
	odd = fnc.filter_(lambda x: x%2, dm.a)
	assert all([x%2 for x in odd])
	print(type(dm._rowid))
	dm = fnc.filter_(lambda **d: d['a']%2, dm)
	print(type(dm._rowid))
	assert dm.a == [1, 3]


def test_setcol():

	dm1 = DataMatrix(length=2)
	dm2 = fnc.setcol(dm1, 'y', range(2))
	assert dm2.y == [0, 1]
	assert 'y' not in dm1


def test_curry():

	@fnc.curry
	def add(a, b, c):

		"""test"""

		return a+b+c

	assert add(1,2,3) == 6
	assert add(1,2)(3) == 6
	assert add(1)(2,3) == 6
	assert add(1)(2)(3) == 6
	if py3:
		assert add.__doc__ == 'test'


def test_memoize():

	@fnc.memoize(debug=True)
	def add(a, b):

		"""test"""

		return a+b

	@fnc.memoize(debug=True, key='custom-key')
	def add2(a, b):

		return a+b

	@fnc.memoize()
	def add3(a, b):

		return a+b

	retval, memkey, src = add(1,2)
	assert retval == 3
	assert src == u'function'
	assert add(1,2) == (retval, memkey, u'memory')
	add.clear()
	assert add(1,2) == (retval, memkey, u'function')
	assert add(1,2) == (retval, memkey, u'memory')
	assert add2(1,2) == (retval, u'custom-key', u'function')
	assert add2(1,2) == (retval, u'custom-key', u'memory')
	add2.clear()
	assert add2(1,2), (retval, u'custom-key', u'function')
	assert add2(1,2), (retval, u'custom-key', u'memory')
	assert add3(1,2), add3(1,2)


def test_memoize_chain():

	@fnc.memoize(lazy=True, debug=True)
	def add_one(i):

		if isinstance(i, tuple):
			i = i[0]
		print(i)
		return i + 1

	chain = (0 >> add_one >> add_one >> add_one)
	with capture_stdout() as out:
		chain()
	l = out.getvalue().strip().split('\n')
	assert len(l) == 6
	with capture_stdout() as out:
		chain()
	l = out.getvalue().strip().split('\n')
	assert len(l) == 1
