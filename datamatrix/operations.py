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

---
desc:
	Functions that operate on DataMatrix objects and columns.
---
"""

import random
from datamatrix.py3compat import *
from datamatrix import DataMatrix, FloatColumn, IntColumn, SeriesColumn, \
	MixedColumn
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._index import Index
# For backwards compatibility
from datamatrix.functional import map_, filter_, setcol

try:
	from datamatrix import convert
	import pandas as pd
except (ImportError, AttributeError, RuntimeError) as e:
	# AttributeError and RuntimeError can occur due to a PyQt4/5 conflict
	pass
else:
	pivot_table = convert.wrap_pandas(pd.pivot_table)


def z(col):

	"""
	desc: |
		Transforms a column into z scores.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=5)
		 dm.col = range(5)
		 dm.z = operations.z(dm.col)
		 print(dm)
		--%

	arguments:
		col:
			desc:	The column to transform.
			type:	BaseColumn

	returns:
		type:	BaseColumn
	"""

	return (col-col.mean)/col.std


def weight(col):

	"""
	desc: |
		Weights a DataMatrix by a column. That is, each row from a DataMatrix is
		repeated as many times as the value in the weighting column.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=3)
		 dm.A = 1, 2, 0
		 dm.B = 'x', 'y', 'z'
		 print('Original:')
		 print(dm)
		 dm = operations.weight(dm.A)
		 print('Weighted by A:')
		 print(dm)
		--%

	arguments:
		col:
			desc:	The column to weight by.
			type:	BaseColumn

	returns:
		type:	DataMatrix
	"""

	dm1 = col._datamatrix
	dm2 = DataMatrix(length=int(col.sum))
	for colname, _col in dm1.columns:
		dm2[colname] = type(_col)
	i2 = 0
	for i1, weight in enumerate(col):
		if not isinstance(weight, int) or weight < 0:
			raise TypeError(
				u'Weights should be non-negative integer values, not %s (%s)' \
				% (weight, type(weight)))
		for c in range(weight):
			for colname in dm1.column_names:
				dm2[colname][i2] = dm1[colname][i1]
			i2 += 1
	return dm2


def replace(col, mappings={}):

	"""
	desc: |
		Replaces values in a column by other values.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations as ops

		 dm = DataMatrix(length=3)
		 dm.old = 0, 1, 2
		 dm.new = ops.replace(dm.old, {0 : 'a', 2 : 'c'})
		 print(dm_new)
		--%

	arguments:
		col:
			desc:	The column to weight by.
			type:	BaseColumn

	keywords:
		mappings:
			desc:	A dict where old values are keys and new values are values.
			type:	dict
	"""

	col = col[:]
	# For MixedColumns
	if isinstance(col._seq, list):
		for old, new in mappings.items():
			for i, val in enumerate(col):
				if old == val:
					col[i] = new
		return col
	# For NumericColumns and SeriesColumns
	import numpy as np
	for old, new in mappings.items():
		b = np.isnan(col._seq) if np.isnan(old) else col._seq == old
		i = np.where(b)
		col._seq[i] = new
	return col


def split(col, *values):

	"""
	desc: |
		Splits a DataMatrix by unique values in a column.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations as ops

		 dm = DataMatrix(length=4)
		 dm.A = 0, 0, 1, 1
		 dm.B = 'a', 'b', 'c', 'd'
		 # If no values are specified, a (value, DataMatrix) iterator is
		 # returned.
		 for A, dm in ops.split(dm.A):
		 	print('dm.A = %s' % A)
		 	print(dm)
		 # If values are specific an iterator over DataMatrix objects is
		 # returned.
		 dm_a, dm_c = ops.split(dm.B, 'a', 'c')
		 print('dm.B == "a"')
		 print(dm_a)
		 print('dm.B == "c"')
		 print(dm_c)
		--%

	arguments:
		col:
			desc:	The column to split by.
			type:	BaseColumn

	argument-list:
		values:		Splits the DataMatrix based on these values. If this is
					provided, an iterator over DataMatrix objects is returned,
					rather than an iterator over (value, DataMatrix) tuples.

	returns:
		desc:	A iterator over (value, DataMatrix) tuples if no values are
				provided; an iterator over DataMatrix objects if values are
				provided.
		type:	Iterator
	"""

	_values = values if values else col.unique
	for val in _values:
		dm = col == val
		if not dm:
			warn(u'No matching rows for %s' % val)
		if values:
			yield dm
		else:
			yield val, dm


def tuple_split(col, *values):

	"""
	visible: False
	"""

	warn('tuple_split() is deprecated. Please use split() instead.',
		DeprecationWarning)
	return split(col, *values)


def bin_split(col, bins):

	"""
	desc: |
		Splits a DataMatrix into bins; that is, the DataMatrix is first sorted
		by a column, and then split into equal-size (or roughly equal-size)
		bins.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=5)
		 dm.A = 1, 0, 3, 2, 4
		 dm.B = 'a', 'b', 'c', 'd', 'e'
		 for bin, dm in enumerate(operations.bin_split(dm.A, bins=3)):
		 	print('bin %d' % bin)
		 	print(dm)
		--%

	arguments:
		col:
			desc:	The column to split by.
			type:	BaseColumn
		bins:
			desc:	The number of bins.
			type:	int

	returns:
		desc:	A generator that iterates over the bins.
	"""

	if len(col) < bins:
		raise ValueError('More bins than rows')
	dm = sort(col._datamatrix, by=col)
	start = 0
	for i in range(bins):
		end = int(len(dm) * (i+1)/bins)
		yield dm[start:end]
		start = end

def fullfactorial(dm, ignore=u''):

	"""
	desc: |
		*Requires numpy*

		Creates a new DataMatrix that uses a specified DataMatrix as the base of
		a full-factorial design. That is, each value of every row is combined
		with each value from every other row. For example:

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=2)
		 dm.A = 'x', 'y'
		 dm.B = 3, 4
		 dm = operations.fullfactorial(dm)
		 print(dm)
		--%

	arguments:
		dm:
			desc:	The source DataMatrix.
			type:	DataMatrix

	keywords:
		ignore:		A value that should be ignored.

	return:
		type:	DataMatrix
	"""


	if not dm.columns:
		return DataMatrix()
	if not all(isinstance(col, MixedColumn) for colname, col in dm.columns):
		raise TypeError(u'fullfactorial only works with MixedColumns')
	# Create a new DataMatrix that strips all empty cells, and packs them such
	# that empty cells are moved toward the end.
	dm = dm[:]
	for colname, col in dm.columns:
		col = (col != ignore)[colname]
		dm[colname][:len(col)] = col
		dm[colname][len(col):] = ignore
	# A list where each value is an int X that corresponds to a factor with X
	# levels.
	design = [len(c != ignore) for n, c in dm.columns]
	a = _fullfact(design)
	# Create an DataMatrix with empty columns
	fdm = DataMatrix(a.shape[0])
	for name in dm.column_names:
		fdm[name] = u''
	for i in range(a.shape[0]):
		row = a[i]
		for rownr, name in enumerate(dm.column_names):
			fdm[name][i] = dm[name][int(row[rownr])]
	return fdm


def group(dm, by):

	"""
	desc: |
		*Requires numpy*

		Groups the DataMatrix by unique values in a set of grouping columns.
		Grouped columns are stored as SeriesColumns. The columns that are
		grouped should contain numeric values. The order in which groups appear
		in the grouped DataMatrix is unpredictable.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=4)
		 dm.A = 'x', 'x', 'y', 'y'
		 dm.B = 0, 1, 2, 3
		 print('Original:')
		 print(dm)
		 dm = operations.group(dm, by=dm.A)
		 print('Grouped by A:')
		 print(dm)
		--%

	arguments:
		dm:
			desc:	The DataMatrix to group.
			type:	DataMatrix
		by:
			desc:	A column or list of columns to group by.
			type:	[BaseColumn, list]

	returns:
		desc:	A grouped DataMatrix.
		type:	DataMatrix
	"""

	bycol = MixedColumn(datamatrix=dm)
	bynames = []
	if by is not None:
		if isinstance(by, BaseColumn):
			bynames = [by.name]
			by = [by]
		for col in by:
			if col._datamatrix is not dm:
				raise ValueError(u'By-columns are from a different DataMatrix')
			bycol += col
			bynames += [col.name]
	bycol_hashed = IntColumn(datamatrix=dm)
	bycol_hashed[:] = [hash(key) for key in bycol]
	keys = bycol_hashed.unique
	groupcols = [(name, col) for name, col in dm.columns if name not in bynames]
	nogroupcols = [(name, col) for name, col in dm.columns if name in bynames]
	cm = DataMatrix(length=len(keys))
	for name, col in groupcols:
		if isinstance(col, _SeriesColumn):
			warn(u'Failed to create series for SeriesColumn s%s' % name)
			continue
		cm[name] = SeriesColumn(depth=0)
	for name, col in nogroupcols:
		cm[name] = col.__class__

	for i, key in enumerate(keys):
		dm_ = bycol_hashed == key
		for name, col in groupcols:
			if isinstance(col, _SeriesColumn):
				continue
			if cm[name].depth < len(dm_[name]):
				cm[name].defaultnan = True
				cm[name].depth = len(dm_[name])
				cm[name].defaultnan = False
			try:
				cm[name][i,:len(dm_[name])] = dm_[name]
			except ValueError:
				warn(u'Failed to create series for MixedColumn %s' % name)
		for name, col in nogroupcols:
			cm[name][i] = dm_[name][0]
	return cm


def sort(obj, by=None):

	"""
	desc: |
		Sorts a column or DataMatrix. In the case of a DataMatrix, a column must
		be specified to determine the sort order. In the case of a column, this
		needs to be specified if the column should be sorted by another column.

		The sort order is as follows:

		- `-INF`
		- `int` and `float` values in increasing order
		- `INF`
		- `str` values in alphabetical order, where uppercase letters come first
		- `None`
		- `NAN`

		You can also sort columns (but not DataMatrix objects) using the
		built-in `sorted()` function. However, when sorting different mixed
		types, this may lead to Exceptions or (in the case of `NAN` values)
		unpredictable results.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=3)
		 dm.A = 2, 0, 1
		 dm.B = 'a', 'b', 'c'
		 dm = operations.sort(dm, by=dm.A)
		 print(dm)
		--%

	arguments:
		obj:
			type:	[DataMatrix, BaseColumn]

	keywords:
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
	desc: |
		Shuffles a DataMatrix or a column. If a DataMatrix is shuffled, the order
		of the rows is shuffled, but values that were in the same row will stay
		in the same row.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=5)
		 dm.A = 'a', 'b', 'c', 'd', 'e'
		 dm.B = operations.shuffle(dm.A)
		 print(dm)
		--%

	arguments:
		obj:
			type:	[DataMatrix, BaseColumn]

	returns:
		desc:	The shuffled DataMatrix or column.
		type:	[DataMatrix, BaseColumn]
	"""

	_rowid = Index(obj._rowid)
	random.shuffle(_rowid)
	if isinstance(obj, DataMatrix):
		return obj._selectrowid(_rowid)
	col = obj._getrowidkey(_rowid)
	col._rowid = obj._rowid
	return col


def shuffle_horiz(*obj):

	"""
	desc: |
		Shuffles a DataMatrix, or several columns from a DataMatrix,
		horizontally. That is, the values are shuffled between columns from the
		same row.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=5)
		 dm.A = 'a', 'b', 'c', 'd', 'e'
		 dm.B = range(5)
		 dm = operations.shuffle_horiz(dm.A, dm.B)
		 print(dm)
		--%

	argument-list:
	 	desc:	A list of BaseColumns, or a single DataMatrix.

	returns:
		desc:	The shuffled DataMatrix.
		type:	DataMatrix
	"""

	if len(obj) == 1 and isinstance(obj[0], DataMatrix):
		obj = [column for colname, column in obj[0].columns]
	try:
		assert(len(obj) > 0)
		for column in obj:
			assert(isinstance(column, BaseColumn))
		dm = obj[0]._datamatrix
		for column in obj:
			assert(dm == column._datamatrix)
	except AssertionError:
		raise ValueError(
			u'Expecting a DataMatrix or multiple BaseColumns from the same DataMatrix')
	dm = dm[:]
	dm_shuffle = keep_only(dm, *obj)
	for row in dm_shuffle:
		random.shuffle(row)
	for colname, column in dm_shuffle.columns:
		dm._cols[colname] = column
	dm._mutate()
	return dm


def keep_only(dm, *cols):

	"""
	desc: |
		Removes all columns from the DataMatrix, except those listed in `cols`.

		__Example:__

		%--
		python: |
		 from datamatrix import DataMatrix, operations as ops

		 dm = DataMatrix(length=5)
		 dm.A = 'a', 'b', 'c', 'd', 'e'
		 dm.B = range(5)
		 dm.C = range(5, 10)
		 dm_new = ops.keep_only(dm, dm.A, dm.C)
		 print(dm_new)
		--%

	arguments:
		dm:
			type:	DataMatrix

	argument-list:
		cols:	A list of column names, or column objects.
	"""

	# For backwards compatibility, accept also a list as a single argument
	if len(cols) == 1 and isinstance(cols[0], list):
		cols = cols[0]
	dm = dm[:]
	colnames = [_colname(col) for col in cols]
	for colname in colnames:
		if isinstance(colname, list):
			raise TypeError(
				(u'Column object has multiple names: %s. '
				u'Specify name as str instead.') % colname
			)
	for colname in dm.column_names:
		if colname not in colnames:
			del dm[colname]
	return dm


def auto_type(dm):

	"""
	desc: |
		*Requires fastnumbers*

		Converts all columns of type MixedColumn to IntColumn if all values are
		integer numbers, or FloatColumn if all values are non-integer numbes.

		%--
		python: |
		 from datamatrix import DataMatrix, operations

		 dm = DataMatrix(length=5)
		 dm.A = 'a'
		 dm.B = 1
		 dm.C = 1.1
		 dm_new = operations.auto_type(dm)
		 print('dm_new.A: %s' % type(dm_new.A))
		 print('dm_new.B: %s' % type(dm_new.B))
		 print('dm_new.C: %s' % type(dm_new.C))
		--%

	arguments:
		dm:
			type:	DataMatrix

	returns:
		type:	DataMatrix
	"""

	new_dm = DataMatrix(length=len(dm))
	for name, col in dm.columns:
		new_dm[name] = _best_fitting_col_type(col)
		new_dm[name][:] = col
	return new_dm

# Private function

def _colname(col):

	"""
	visible: False

	desc:
		Gets the name of column. Column can be specified as a name or as a
		BaseColumn.
	"""

	if isinstance(col, basestring):
		return col
	if isinstance(col, BaseColumn):
		return col.name
	raise ValueError(u'Expecting column names or BaseColumn objects')


def _best_fitting_col_type(col):

	"""
	visible: False

	desc:
		Determines the best fitting type for a column.
	"""

	from fastnumbers import isreal, isintlike

	if isinstance(col, _SeriesColumn):
		return SeriesColumn(depth=col.depth)
	if isinstance(col, (FloatColumn, IntColumn)):
		return type(col)
	if not all(isreal(val, allow_inf=True, allow_nan=True) for val in col):
		return MixedColumn
	if not all(isintlike(val) for val in col):
		return FloatColumn
	return IntColumn


def _fullfact(levels):

	"""
	visible: False

	desc: |
		Taken from pydoe. See:
		<https://github.com/tisimst/pyDOE/blob/master/pyDOE/doe_factorial.py>
	"""

	import numpy as np
	n = len(levels)  # number of factors
	nb_lines = np.prod(levels)  # number of trial conditions
	try:
		H = np.zeros((nb_lines, n))
	except (ValueError, MemoryError):
		raise MemoryError(u'DataMatrix too large for fullfact')
	level_repeat = 1
	range_repeat = np.prod(levels)
	for i in range(n):
		range_repeat //= levels[i]
		lvl = []
		try:
			for j in range(levels[i]):
				lvl += [j] * level_repeat
			rng = lvl * range_repeat
		except MemoryError:
			raise MemoryError(u'DataMatrix too large for fullfact')
		level_repeat *= levels[i]
		H[:, i] = rng
	return H
