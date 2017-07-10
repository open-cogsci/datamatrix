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
from nose.tools import eq_, ok_


def test_map_():
	
	for coltype in (MixedColumn, FloatColumn, IntColumn):
		dm = DataMatrix(length=2, default_col_type=coltype)
		dm.a = 1, 2
		dm.a = fnc.map_(lambda x: x*2, dm.a)
		eq_(dm.a, [2, 4])
		ok_(isinstance(dm.a, coltype))
		dm = fnc.map_(lambda **d: {'a' : 0}, dm)
		eq_(dm.a, [0, 0])
		ok_(isinstance(dm.a, coltype))
		

def test_filter_():
	
	dm = DataMatrix(length=4)
	dm.a = range(4)
	odd = fnc.filter_(lambda x: x%2, dm.a)
	ok_(all([x%2 for x in odd]))
	print(type(dm._rowid))
	dm = fnc.filter_(lambda **d: d['a']%2, dm)
	print(type(dm._rowid))
	eq_(dm.a, [1, 3])


def test_setcol():
	
	dm1 = DataMatrix(length=2)
	dm2 = fnc.setcol(dm1, 'y', range(2))
	eq_(dm2.y, [0, 1])
	ok_('y' not in dm1)
