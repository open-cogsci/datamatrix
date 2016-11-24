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
from datamatrix import DataMatrix, FloatColumn, IntColumn, SeriesColumn, \
	MixedColumn
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._index import Index
import random

try:
	from datamatrix import convert
	import pandas as pd
except ImportError as e:
	pass
else:
	pivot_table = convert.wrap_pandas(pd.pivot_table)


def z(col):

	"""
	desc:
		Transforms a column into z scores.

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

		For example:

		A B
		---
		1 X
		2 Y

		>>> weight(dm.A)

		A B
		---
		1 X
		2 Y
		2 Y

	arguments:
		col:
			desc:	The column to weight by.
			type:	BaseColumn

	returns:
		type:	DataMatrix
	"""

	dm1 = col._datamatrix
	dm2 = DataMatrix(length=int(col.sum))
	for colname, col in dm1.columns:
		dm2[colname] = type(col)
	i2 = 0
	for i1, weight in enumerate(col):
		if not isinstance(weight, int) or weight < 0:
			raise TypeError(u'Weights should be non-negative integer values')
		for c in range(weight):
			for colname in dm1.column_names:
				dm2[colname][i2] = dm1[colname][i1]
			i2 += 1
	return dm2


def split(col):

	"""
	desc:
		Splits a DataMatrix by unique values in a column.

	arguments:
		col:
			desc:	The column to split by.
			type:	BaseColumn

	returns:
		desc:	A iterator over (value, DataMatrix) tuples.
		type:	Iterator
	"""

	for val in col.unique:
		yield val, col == val


def tuple_split(col, *values):

	"""
	desc:
		Splits a DataMatrix by values in a column, and returns the split as a
		tuple of DataMatrix objects.

	arguments:
		col:
			desc:	The column to split by.
			type:	BaseColumn

	argument-list:
		values: A list values to split.

	returns:
		A tuple of DataMatrix objects.

	example: |
		dm1, dm2 = tuple_split(dm.col, 1, 2)
	"""

	n_total = len(col)
	n_select = 0
	l = []
	for val in values:
		dm = col == val
		n = len(dm)
		if not n:
			warn(u'No matching rows for %s' % val)
		n_select += n
		l.append(dm)
	if n_select != n_total:
		warn(u'Some rows have not been selected')
	return tuple(l)


def bin_split(col, bins):

	"""
	desc:
		Splits a DataMatrix into bins; that is, the DataMatrix is first sorted
		by a column, and then split into equal-size (or roughly equal-size)
		bins.

	arguments:
		col:
			desc:	The column to split by.
			type:	BaseColumn
		bins:
			desc:	The number of bins.
			type:	int

	returns:
		desc:	A generator that iterators over the splits.

	example: |
		# Get the mean response time for 10 bins
		for dm_ in op.split(dm.response_time, bins=10):
			print(dm_.response_time.mean)
	"""

	if len(col) < bins:
		raise ValueError('More bins than rows')
	dm = sort(col._datamatrix, by=col)
	for i in range(bins):
		start = int(len(dm)/bins*i)
		end = int(1.*len(dm)/bins*(i+1))
		yield dm[start:end]


def fullfactorial(dm, ignore=u''):

	"""
	desc: |
		*Requires numpy*

		Creates a new DataMatrix that uses a specified DataMatrix as the base of
		a full-factorial design. That is, each value of every row is combined
		with each value from every other row. For example:

			A B
			---
			x 3
			y 4

		>>> fullfactorial(dm)

			A B
			---
			x 3
			x 4
			y 3
			y 4

	arguments:
		dm:
			desc:	The source DataMatrix.
			type:	DataMatrix

	keywords:
		ignore:		A value that should be ignored.

	return:
		type:	DataMatrix
	"""


	for colname, col in dm.columns:
		if not isinstance(col, MixedColumn):
			raise ValueError(u'fullfactorial only works with MixedColumns')
	design = [len(col != ignore) for name, col in dm.columns]
	a = _fullfact(design)
	fdm = DataMatrix(a.shape[0])
	for name in dm.column_names:
		fdm[name] = u''
	for i in range(a.shape[0]):
		row = a[i]
		for rownr, name in enumerate(dm.column_names):
			fdm[name][i] = dm[name][int(row[rownr])]
	return fdm


def group(dm, by=None):

	"""
	desc: |
		*Requires numpy*

		Groups the DataMatrix by unique values in a set of grouping columns.
		Grouped columns are stored as SeriesColumns. The columns that are
		grouped should contain numeric values.

		For example:

		A B
		---
		x 0
		x 1
		y 2
		y 3

		>>> group(dm, by=[dm.a])

		Gives:

		A B
		---
		x [0, 1]
		y [2, 3]

	arguments:
		dm:
			desc:	The DataMatrix to group.
			type:	DataMatrix

	keywords:
		by:			A list of columns to group by.
		type:		[list, None]

	returns:
		desc:	A grouped DataMatrix.
		type:	DataMatrix
	"""

	import numpy as np

	bycol = MixedColumn(datamatrix=dm)
	if by is not None:
		for col in by:
			if col._datamatrix is not dm:
				raise ValueError(u'By-columns are from a different DataMatrix')
			bycol += col
	keys = bycol.unique
	groupcols = [(name, col) for name, col in dm.columns if col not in by]
	nogroupcols = [(name, col) for name, col in dm.columns if col in by]
	cm = DataMatrix(length=len(keys))
	for name, col in groupcols:
		if isinstance(col, _SeriesColumn):
			warn(u'Failed to create series for SeriesColumn s%s' % name)
			continue
		cm[name] = SeriesColumn(depth=0)
	for name, col in nogroupcols:
		cm[name] = col.__class__

	for i, key in enumerate(keys):
		dm_ = bycol == key
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

	_rowid = Index(obj._rowid)
	random.shuffle(_rowid)
	if isinstance(obj, DataMatrix):
		return obj._selectrowid(_rowid)
	col = obj._getrowidkey(_rowid)
	col._rowid = obj._rowid
	return col


def shuffle_horiz(*obj):

	"""
	desc:
		Shuffles a DataMatrix, or several columns from a DataMatrix,
		horizontally. That is, the values are shuffled between columns from the
		same row.

	argument-list:
	 	desc:	A list of BaseColumns, or a single DataMatrix.

	returns:
		desc:	The shuffled DataMatrix.
		type:	DataMatrix

	example: |
		dm = DataMatrix(length=2)
		dm.col1 = 'a', 'b'
		dm.col2 = 1, 2
		dm.col3 = '-'
		# Shuffle all columns
		dm_shuffle = operations.shuffle_horiz(dm)
		print(dm_shuffle)
		# Shuffle only col1 and col2
		dm_shuffle = operations.shuffle_horiz(dm.col1, dm.col2)
		print(dm_shuffle)
	"""

	if len(obj) == 1 and isinstance(obj[0], DataMatrix):
		obj = [column for colname, column in obj[0].columns]
	try:
		assert(len(obj) > 1)
		for column in obj:
			assert(isinstance(column, BaseColumn))
		dm = obj[0]._datamatrix
		for column in obj:
			assert(dm == column._datamatrix)
	except AssertionError:
		raise ValueError(
			u'Expecting a DataMatrix or multiple BaseColumns from the same DataMatrix')
	dm = dm[:]
	dm_shuffle = dm[:]
	keep_only(dm_shuffle, obj)
	for row in dm_shuffle:
		random.shuffle(row)
	for colname, column in dm_shuffle.columns:
		dm._cols[colname] = column
	dm._mutate()
	return dm


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
			desc:	A list of column names, or columns.
			type:	list
	"""

	colnames = []
	for col in cols:
		if isinstance(col, basestring):
			colnames.append(col)
			continue
		if isinstance(col, BaseColumn):
			colnames.append(col.name)
			continue
		raise ValueError(u'Expecting column names or BaseColumn objects')
	for colname in dm.column_names:
		if colname not in colnames:
			del dm[colname]


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
			new_col = col_type(col._datamatrix)
			new_col[:] = col
			del dm[name]
			dm[name] = new_col
	dm._mutate()

# Private function

def _fullfact(levels):

	"""
	desc:
		Taken from pydoe. See:
		<https://github.com/tisimst/pyDOE/blob/master/pyDOE/doe_factorial.py>
	"""

	import numpy as np
	n = len(levels)  # number of factors
	nb_lines = np.prod(levels)  # number of trial conditions
	H = np.zeros((nb_lines, n))

	level_repeat = 1
	range_repeat = np.prod(levels)
	for i in range(n):
		range_repeat /= levels[i]
		lvl = []
		for j in range(levels[i]):
			lvl += [j]*level_repeat
		rng = lvl*range_repeat
		level_repeat *= levels[i]
		H[:, i] = rng

	return H
