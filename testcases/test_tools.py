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

from nose.tools import eq_, ok_
from datamatrix._datamatrix._index import Index
import numpy as np


def all_nan(*l):
	
	return all([np.isnan(v) for v in l])
	

def check_dm(dm, ref):

	ok_(dm.column_names == ref.column_names)
	for column_name in dm.column_names:
		ok_(not isinstance(column_name, bytes))
	for colname in dm.column_names:
		check_col(dm[colname], ref[colname])
	ok_(isinstance(dm._rowid, Index))


def check_col(col, ref):

	check_integrity(col._datamatrix)
	ok_(len(col) == len(ref))
	for x, y in zip(col, ref):
		if x != y:
			if not (x is None or y is None) and np.isnan(x) and np.isnan(y):
				continue
			print(u'Column error: %s != %s' % (col, ref))
			ok_(False)


def check_row(row, ref):

	check_integrity(row._datamatrix)
	ok_(len(row) == len(ref))
	for (colname, x), y in zip(row, ref):
		if x != y:
			if not (x is None or y is None) and np.isnan(x) and np.isnan(y):
				continue
			print(u'Row error: %s != %s' % (row, ref))
			ok_(False)


def check_series(col, ref):

	check_integrity(col._datamatrix)
	for i, j in zip(col, ref):
		for x, y in zip(i, j):
			if not (x is None or y is None) and np.isnan(x) and np.isnan(y):
				continue
			if not np.isclose(x, y):
				print(u'Column error: %s != %s' % (col, ref))
				ok_(False)


def check_integrity(dm):

	for name, col in dm.columns:
		if len(dm._rowid) != len(col._rowid):
			print('Integrity failure: %s != %s' % (dm._rowid, col._rowid))
			ok_(False)
		for i, j in zip(dm._rowid, col._rowid):
			if i != j:
				print('Integrity failure: %s != %s (col: %s)' \
					% (dm._rowid, col._rowid, name))
				ok_(False)
