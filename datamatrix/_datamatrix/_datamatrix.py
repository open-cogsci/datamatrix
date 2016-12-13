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
from datamatrix import Row
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._mixedcolumn import MixedColumn
from datamatrix._datamatrix._index import Index
import collections
_id = 0

class DataMatrix(object):

	"""
	desc:
		A DataMatrix is a tabular data structure.
	"""

	def __init__(self, length=0, default_col_type=MixedColumn):

		"""
		desc:
			Constructor.

		keywords:
			length:
				desc:	The starting length of the DataMatrix.
				type:	int
		"""

		global _id
		object.__setattr__(self, u'_cols', collections.OrderedDict())
		object.__setattr__(self, u'_rowid', Index(length))
		object.__setattr__(self, u'_default_col_type', default_col_type)
		object.__setattr__(self, u'_id', _id)
		_id += 1

	@property
	def columns(self):

		return list(self._cols.items())

	@property
	def column_names(self):

		return list(self._cols.keys())

	@property
	def rows(self):

		return list(range(len(self)))

	@property
	def length(self):

		return len(self._rowid)

	@property
	def default_col_type(self):

		return self._default_col_type

	@property
	def is_2d(self):

		for name, col in self.columns:
			if hasattr(col, u'depth'):
				return False
		return True

	def rename(self, old, new):

		"""
		desc:
			Renames a column. Modifies the DataMatrix in place.

		raises:
			ValueError: When an error occurs.

		arguments:
			old:	The old name.
			new:	The new name.
		"""

		if old == new:
			return
		if old not in self._cols:
			raise ValueError(u'Column name does not exist')
		if new in self._cols:
			raise ValueError(u'Column name already exists')
		try:
			exec(u'%s = None' % new)
		except SyntaxError:
			raise ValueError(u'Invalid column name')
		# A rename recipe that preservers order.
		_cols = collections.OrderedDict([(new, v) if k == old else (k, v) \
			for k, v in self._cols.items()])
		object.__setattr__(self, u'_cols', _cols)
		self._mutate()

	# Private functions. These can also be called by the BaseColumn (and
	# derived) classes.

	def _fromdict(self, d={}):

		"""
		visible: False

		desc:
			Merges a dict into the DataMatrix. Modifies the DataMatrix in place.

		keywords:
			d:	The dict to merge.

		returns:
			The modified DataMatrix.
		"""

		for name, col in d.items():
			if len(col) > len(self):
				self.length = len(col)
			self[name] = self._default_col_type
			self[name][:len(col)] = col
		return self

	def _selectrowid(self, _rowid):

		"""
		visible: False

		desc:
			Selects rows from the current DataMatrix by row id (i.e. not by
			index).

		arguments:
			_rowid:		An iterable list of row ids.

		returns:
			type:	DataMatrix.
		"""

		dm = DataMatrix(len(_rowid))
		object.__setattr__(dm, u'_rowid', _rowid)
		object.__setattr__(dm, u'_id', self._id)
		for name, col in self._cols.items():
			dm._cols[name] = self._cols[name]._getrowidkey(_rowid)
			dm._cols[name]._datamatrix = dm
		return dm

	def _slice(self, key):

		"""
		visible: False

		desc:
			Selects rows from the current DataMatrix by indices (i.e. not by
			row id).

		arguments:
			key:		A slice object, or a list of indices.

		returns:
			type:	DataMatrix.
		"""

		_rowid = self._rowid[key]
		dm = DataMatrix(len(_rowid))
		object.__setattr__(dm, u'_rowid', _rowid)
		object.__setattr__(dm, u'_id', self._id)
		for name, col in self._cols.items():
			dm._cols[name] = self._cols[name][key]
			dm._cols[name]._datamatrix = dm
		return dm

	def _setlength(self, value):

		"""
		visible: False

		desc: |
			Changes the length of the current DataMatrix, adding or removing
			rows as necessary.

			*This modifies the current DataMatrix.*

			__Note__: The preferred way to change the length is by setting the
			length property:

			~~~
			dm.length = 10
			~~~

		arguments:
			value:
				desc:	The new length.
				type:	int
		"""

		if value < len(self):
			object.__setattr__(self, u'_rowid', self._rowid[:value])
			for name, col in self._cols.items():
				self._cols[name] = self._cols[name][:value]
		else:
			startid = 0 if not len(self) else self._rowid.max+1
			rowid = Index([i+startid for i in range(value-len(self))])
			object.__setattr__(self, u'_rowid', self._rowid.clone()+rowid)
			for name in self._cols:
				self._cols[name]._addrowid(rowid)
		self._mutate()

	def _set_default_col_type(self, col_type):

		"""
		visible: False

		desc:
			Sets the default column type.

		arguments:
			col_type:	A column type (BaseColumn)
		"""

		if not isinstance(col_type, type) or not issubclass(col_type, BaseColumn):
			raise Exception(u'Not a valid column type')
		object.__setattr__(self, u'_default_col_type', col_type)

	def _merge(self, other, _rowid):

		"""
		visible: False

		desc:
			Merges the current DataMatrix with another DataMatrix, preserving
			only the rows indicated by _rowid.

		arguments:
			other:	Another DataMatrix.
			_rowid:	A list of row ids.

		returns:
			type:	DataMatrix.
		"""

		if self != other:
			raise Exception('Can only merge related datamatrices')
		dm = DataMatrix(len(_rowid))
		object.__setattr__(dm, u'_rowid', _rowid)
		object.__setattr__(dm, u'_id', self._id)
		for name, col in self._cols.items():
			dm._cols[name] = self._cols[name]._merge(other._cols[name], _rowid)
			dm._cols[name]._datamatrix = dm
		return dm

	def _mergedict(self, d={}):

		"""
		visible: False

		desc: |
			Merges a dict into the DataMatrix.

			*This modifies the current DataMatrix.*

		keywords:
			d:
				desc:	A dictionary, where each each key is a column name, and
						each value is a sequence of column values, or a single
						column value.
				type:	dict

		returns:
			desc:	The current DataMatrix.
		"""

		for name, col in d.items():
			if isinstance(col, basestring):
				self.length = 1
			elif len(col) > len(self):
				self.length = len(col)
			self[name] = self._default_col_type
			self[name][:len(col)] = col
		return self

	def _mutate(self):

		"""
		visible: False

		desc:
			Changes the id of the current DataMatrix. This is done whenever the
			DataMatrix has been modified.
		"""

		global _id
		object.__setattr__(self, u'_id', self._id)
		_id += 1

	def _getcolbyobject(self, key):

		"""
		visible: False

		desc:
			Retrieves a column by object; that is, just return the object
			itself.

		arguments:
			key:
				type:	BaseColumn

		returns:
			type:	BaseColumn
		"""

		for col in self._cols.values():
			if col is key:
				return col
		raise Exception('Column not found')

	def _getcolbyname(self, key):

		"""
		visible: False

		desc:
			Retrieves a column by name.

		arguments:
			key:
				type:	str

		returns:
			type:	BaseColumn
		"""

		if isinstance(key, bytes):
			key = safe_decode(key)
		for name, col in self._cols.items():
			if name == key:
				return col
		raise Exception('Column not found')

	def _getrow(self, key):

		"""
		visible: False

		desc:
			Retrieves a row by key.

		arguments:
			key:
				type:	A key that a Row object understands.

		returns:
			type:	Row
		"""

		return Row(self, key)

	def _check_name(self, name):

		"""
		visible: False

		desc:
			Checks whether a name is a valid column name.

		raises:
			ValueError:	If name is not valid.

		arguments:
			name:		The name to check.
		"""

		try:
			exec('%s = None' % name)
		except SyntaxError:
			raise ValueError(u'Invalid column name: %s' % name)

	# Implemented syntax

	def __contains__(self, item):

		return item in self._cols.keys()

	def __len__(self):

		return len(self._rowid)

	def __eq__(self, other):

		return isinstance(other, DataMatrix) and other._id == self._id

	def __ne__(self, other):

		return not isinstance(other, DataMatrix) or other._id != self._id

	def __and__(self, other):

		selection = Index(set(self._rowid) & set(other._rowid))
		return self._merge(other, selection.sorted())

	def __or__(self, other):

		selection = Index(set(self._rowid) | set(other._rowid))
		return self._merge(other, selection.sorted())

	def __xor__(self, other):

		selection = Index(set(self._rowid) ^ set(other._rowid))
		return self._merge(other, selection.sorted())

	def __delattr__(self, name):

		if name not in self._cols:
			raise AttributeError(u'No column named %s' % name)
		del self._cols[name]

	def __setattr__(self, name, value):

		if isinstance(name, bytes):
			name = safe_decode(name)
		if name == u'length':
			self._setlength(value)
			return
		if name == u'default_col_type':
			self._set_default_col_type(value)
			return
		# Create a new column by type
		if isinstance(value, type) and issubclass(value, BaseColumn):
			self._cols[name] = value(self)
			return
		# Create a new column by type, kwdict tuple
		if isinstance(value, tuple) and len(value) == 2 \
			and isinstance(value[0], type) and issubclass(value[0], BaseColumn):
				cls, kwdict = value
				self._cols[name] = cls(self, **kwdict)
				return
		# Create new column by existing column
		if isinstance(value, BaseColumn):
			if value._datamatrix is not self:
				raise Exception(
					u'This column does not belong to this DataMatrix')
			self._cols[name] = value
			return
		if name not in self:
			self._cols[name] = self._default_col_type(self)
		self._cols[name][:] = value
		self._mutate()

	def __delitem__(self, value):

		# Delete column by object
		if isinstance(value, BaseColumn):
			for name, col in self._cols.items():
				if col is value:
					del self._cols[name]
					return
			else:
				raise ValueError('Column not found: %s' % value)
		# Delete column by name
		if isinstance(value, basestring):
			if value in self._cols:
				del self._cols[value]
				return
			raise ValueError('Column not found: %s' % value)
		# Delete row by index. The trick is to first get the slice that we want
		# to delete, and then xor this with the current DataMatrix.
		if isinstance(value, int):
		 	value = value,
		_slice = self[value] ^ self
		object.__setattr__(self, u'_cols', _slice._cols)
		object.__setattr__(self, u'_rowid', _slice._rowid)

	def __setitem__(self, name, value):

		self.__setattr__(name, value)

	def __getattr__(self, name):

		if name in ('__getstate__', '_cols'):
			raise AttributeError()
		if name in self._cols:
			return self._cols[name]
		raise AttributeError()

	def __getitem__(self, key):

		if isinstance(key, BaseColumn):
			return self._getcolbyobject(key)
		if isinstance(key, basestring):
			return self._getcolbyname(key)
		if isinstance(key, int):
		 	return self._getrow(key)
		if isinstance(key, slice) or isinstance(key, collections.Sequence):
			return self._slice(key)
		raise Exception('Cannot get %s' % key)

	def __str__(self):

		if len(self) > 20:
			return str(self[:20]) + u'\n(+ %d rows not shown)' % (len(self)-20)
		import prettytable
		t = prettytable.PrettyTable()
		t.add_column('#', self._rowid)
		for name, col in list(self._cols.items())[:6]:
			t.add_column(name, col._printable_list())
		if len(self._cols) > 6:
			return str(t) + u'\n(+ %d columns not shown)' % (len(self._cols)-5)
		return str(t)

	def __lshift__(self, other):

		if isinstance(other, dict):
			other = DataMatrix()._fromdict(other)
		dm = DataMatrix(len(self)+len(other))
		for name, col in self._cols.items():
			if hasattr(col, 'depth'):
				dm[name] = col.__class__(dm, col.depth, col.defaultnan)
			else:
				dm[name] = col.__class__
			dm[name][:len(self)] = self[name]
			dm[name]._datamatrix = dm
		for name, col in other._cols.items():
			if name not in dm._cols:
				if hasattr(col, 'depth'):
					dm[name] = col.__class__(dm, col.depth, col.defaultnan)
				else:
					dm[name] = col.__class__
			elif hasattr(col, 'depth'):
				dm[name].depth = max(col.depth, dm[name].depth)
				other[name].depth = max(col.depth, dm[name].depth)
			dm[name][len(self):] = other[name]
			dm[name]._datamatrix = dm
		return dm

	def __iter__(self):

		for i in self.rows:
			yield self[i]
