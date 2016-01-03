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

class Row(object):

	"""
	desc:
		A single row from a DataMatrix.
	"""

	def __init__(self, datamatrix, index):

		"""
		desc:
			Constructor.

		arguments:
			datamatrix:		A DataMatrix object.
			index:			The row index.
		"""

		object.__setattr__(self, u'_datamatrix', datamatrix)
		object.__setattr__(self, u'_index', index)

	def __len__(self):

		return len(self._datamatrix.columns)

	def __getattr__(self, key):

		return self._datamatrix[key][self._index]

	def __getitem__(self, key):

		if isinstance(key, int):
			key = self._datamatrix.column_names[key]
		return self._datamatrix[key][self._index]

	def __setattr__(self, key, value):

		self._datamatrix[key][self._index] = value

	def __setitem__(self, key, value):

		if isinstance(key, int):
			key = self._datamatrix.column_names[key]
		self._datamatrix[key][self._index] = value

	def __str__(self):

		import prettytable
		t = prettytable.PrettyTable(["Name", "Value"])
		for name, col in self._datamatrix.columns:
			t.add_row([name, self[name]])
		return str(t)

	def __iter__(self):

		for col in self._datamatrix.column_names:
			yield col, self[col]
