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
import numpy as np


def check_col(col, ref):

	check_integrity(col._datamatrix)
	for x, y in zip(col, ref):
		if x != y and not (np.isnan(x) and np.isnan(y)):
			print(u'Column error: %s != %s' % (col, ref))
			ok_(False)


def check_series(col, ref):

	check_integrity(col._datamatrix)
	for i, j in zip(col, ref):
		ok_(all(i == j))


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
