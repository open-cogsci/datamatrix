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

from datamatrix import DataMatrix, FloatColumn, IntColumn
import random


def sort(obj, by=None):

	"""
	desc:
		Sorts a column or DataMatrix. In the case of a DataMatrix, a column must
		be specified to determine the sort order. In the case of a column, this
		needs to be specified if the column should be sorted by another column.

	arguments:
		obj:
			type:	[DataMatrix, BaseColumn]
		by:
			desc:	The sort key, that is, the column that is used for sorting
					the DataMatrix, or the other column.
			type:	BaseColumn

	returns:
		desc:	The sorted DataMatrix, or the sorted column.
		type:	[DataMatrix, BaseColumn]
	"""

	if isinstance(obj, DataMatrix):
		if by is None:
			raise ValueError(
				'The by keyword is required when sorting a DataMatrix')
		return obj._selectrowid(by._sortedrowid())
	if by is None:
		by = obj
	col = obj._getrowidkey(by._sortedrowid())
	col._rowid = obj._rowid
	return col


def shuffle(obj):

	"""
	desc:
		Shuffles a DataMatrix or a column. If a DataMatrix is shuffle, the order
		of the rows is shuffled, but values that were in the same row will stay
		in the same row.

	arguments:
		obj:
			type:	[DataMatrix, BaseColumn]

	returns:
		desc:	The shuffled DataMatrix or column.
		type:	[DataMatrix, BaseColumn]
	"""

	_rowid = list(obj._rowid)
	random.shuffle(_rowid)
	if isinstance(obj, DataMatrix):
		return obj._selectrowid(_rowid)
	col = obj._getrowidkey(_rowid)
	col._rowid = obj._rowid
	return col


def keep_only(dm, cols=[]):

	"""
	desc: |
		Removes all columns from the DataMatrix, except those listed in `cols`.

		*Note:* This modifies the DataMatrix in place.

	arguments:
		dm:
			type:	DataMatrix

	keywords:
		cols:
			desc:	A list of column names.
			type:	list
	"""

	for col in dm.column_names:
		if col not in cols:
			del dm[col]


def auto_type(dm):

	"""
	desc: |
		Converts all columns of type MixedColumn to IntColumn if all values are
		integer numbers, or FloatColumn if all values are non-integer numbes.

		*Note:* This modifies the DataMatrix in place.

	arguments:
		dm:
			type:	DataMatrix
	"""

	for name, col in dm.columns:
		if isinstance(col, (FloatColumn, IntColumn)):
			continue
		col_type = IntColumn
		for val in col:
			try:
				assert(int(val) == float(val))
			except:
				try:
					float(val)
					col_type = FloatColumn
				except:
					break
		else:
			new_col = IntColumn(col._datamatrix)
			new_col[:] = col
			del dm[name]
			dm[name] = new_col
