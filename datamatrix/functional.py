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
	Functions and decorators for functional programming.
---
"""

from datamatrix.py3compat import *
from datamatrix import DataMatrix, IntColumn, SeriesColumn, MixedColumn
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._index import Index


def map_(fnc, obj):
	
	"""
	desc: |
		Maps a function (`fnc`) onto rows of datamatrix or cells of a column.
	
		If `obj` is a column, the function `fnc` is mapped is mapped onto each
		cell of the column, and a new column is returned. In this case,
		`fnc` should be a function that accepts and returns a single value.
		
		If `obj` is a datamatrix, the function `fnc` is mapped onto each row,
		and a new datamatrix is returned. In this case, `fnc` should be a
		function that accepts a keyword `dict`, where column names are keys and
		cells are values. The return value should be another `dict`, again with
		column names as keys, and cells as values. Columns that are not part of
		the returned `dict` are left unchanged.
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import DataMatrix, functional as fnc
		 
		 dm = DataMatrix(length=3)
		 dm.old = 0, 1, 2
		 # Map a 2x function onto dm.old to create dm.new
		 dm.new = fnc.map_(lambda i: i*2, dm.old)
		 print(dm)
		 # Map a 2x function onto the entire dm to create dm_new, using a fancy
		 # dict comprehension wrapped inside a lambda function.
		 dm_new = fnc.map_(
		 	lambda **d: {col : 2*val for col, val in d.items()},
			dm)
		 print(dm_new)
		--%
		
	arguments:
		fnc:
			desc:	A function to map onto each row or each cell.
			type:	callable
		obj:
			desc:	A datamatrix or column to map `fnc` onto.
			type:	[BaseColumn, DataMatrix]

	returns:
		desc:	A new column or datamatrix.
		type:	[BaseColumn, DataMatrix]
	"""
	
	if not callable(fnc):
		raise TypeError('fnc should be callable')
	if isinstance(obj, _SeriesColumn):
		# For a SeriesColumn, we need to make a special case, because the depth
		# of the new SeriesColumn may be different from the depth of the
		# original column.
		for i, cell in enumerate(obj):	
			a = fnc(cell)
			if not i:
				newcol = _SeriesColumn(obj.dm, depth=len(a))
			newcol[i] = a
		return newcol		
	if isinstance(obj, BaseColumn):
		newcol = obj._empty_col()
		newcol[:] = [fnc(cell) for cell in obj]
		return newcol
	if isinstance(obj, DataMatrix):
		dm = obj[:]
		for row in dm:
			d = {col : val for col, val in row}
			d.update(fnc(**d))
			for col, val in d.items():
				row[col] = val
		return dm
	raise TypeError(u'obj should be DataMatrix or BaseColumn')
	
	
def filter_(fnc, obj):
	
	"""
	desc: |
		Filters rows from a datamatrix or column based on filter function
		(`fnc`).
		
		If `obj` is a column, `fnc` should be a function that accepts a single
		value. If `obj` is a datamatrix, `fnc` should be a function that accepts
		a keyword `dict`, where column names are keys and cells are values. In
		both cases, `fnc` should return a `bool` indicating whether the row or
		value should be included.
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import DataMatrix, functional as fnc
		 
		 dm = DataMatrix(length=5)
		 dm.col = range(5)
		 # Create a column with only odd values
		 col_new = fnc.filter_(lambda x: x % 2, dm.col)
		 print(col_new)
		 # Create a new datamatrix with only odd values in col
		 dm_new = fnc.filter_(lambda **d: d['col'] % 2, dm)
		 print(dm_new)
		--%
		
	arguments:
		fnc:
			desc:	A filter function.
			type:	callable
		obj:
			desc:	A datamatrix or column to filter.
			type:	[BaseColumn, DataMatrix]

	returns:
		desc:	A new column or datamatrix.
		type:	[BaseColumn, DataMatrix]		
	"""
	
	if not callable(fnc):
		raise TypeError('fnc should be callable')	
	if isinstance(obj, DataMatrix):
		dm = obj
		keep = lambda fnc, row: fnc(**{col : val for col, val in row})
	elif isinstance(obj, BaseColumn):
		dm = obj.dm
		keep = lambda fnc, row: fnc(row)
	else:
		raise TypeError(u'obj should be DataMatrix or BaseColumn')
	dm = dm._selectrowid(Index(
		[rowid for rowid, row in zip(dm._rowid, obj) if keep(fnc, row)]))
	if isinstance(obj, DataMatrix):
		return dm
	return dm[obj.name]


def setcol(dm, name, value):
	
	"""
	desc: |
		Returns a new DataMatrix to which a column has been added or in which
		a column has been modified.
		
		The main difference with regular assignment (`dm.col = 'x'`) is that
		`setcol()` does not modify the original DataMatrix, and can be used in
		`lambda` expressions.
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import DataMatrix, functional as fnc

		 dm1 = DataMatrix(length=5)
		 dm2 = fnc.setcol(dm1, 'y', range(5))
		 print(dm2)
		--%
		
	arguments:
		dm:
			desc:	A DataMatrix.
			type:	DataMatrix
		name:
			desc:	A column name.
			type:	str
		value:
			desc:	The value to be assigned to the column. This can be any
					value this is valid for a regular column assignment.

	returns:
		desc:	A new DataMatrix.
		type:	DataMatrix
	"""	
	
	if not isinstance(name, basestring):
		raise TypeError('name should be a string')
	newdm = dm[:]
	if isinstance(value, BaseColumn):
		if value._datamatrix is not dm:
			raise Exception('This column does not belong to this DataMatrix')
		value._datamatrix = newdm
	newdm[name] = value
	return newdm
