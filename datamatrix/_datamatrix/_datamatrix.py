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

from datamatrix import BaseColumn, Row
import collections
_id = 0

class DataMatrix(object):

	def __init__(self, length=0):

		global _id
		object.__setattr__(self, u'_cols', collections.OrderedDict())
		object.__setattr__(self, u'_rowid', list(range(length)))
		object.__setattr__(self, u'_id', _id)
		_id += 1

	def fromdict(self, d={}):

		from datamatrix import MixedColumn

		for name, col in d.items():
			if len(col) > len(self):
				self.length = len(col)
			self[name] = MixedColumn
			self[name][:len(col)] = col
		return self

	@property
	def columns(self):
		return list(self._cols.items())

	@property
	def length(self):
		return len(self._rowid)

	def setlength(self, value):

		if value < len(self):
			object.__setattr__(self, u'_rowid', self._rowid[:value])
			for name, col in self._cols.items():
				self._cols[name] = self._cols[name][:value]
		else:
			if len(self) == 0:
				startid = 0
			else:
				startid = max(self._rowid)+1
			rowid = [rowid+startid for rowid in range(value-len(self))]
			object.__setattr__(self, u'_rowid', self._rowid+rowid)
			for name in self._cols:
				self._cols[name].addrowid(rowid)
		self.mutate()

	def __len__(self):

		return len(self._rowid)

	def __eq__(self, other):

		return isinstance(other, DataMatrix) and other._id == self._id

	def __ne__(self, other):

		return not isinstance(other, DataMatrix) or other._id != self._id

	def __and__(self, other):

		selection = set(self._rowid) & set(other._rowid)
		return self.merge(other, sorted(selection))

	def __or__(self, other):

		selection = set(self._rowid) | set(other._rowid)
		return self.merge(other, sorted(selection))

	def merge(self, other, _rowid):

		if self != other:
			raise Exception('Can only merge related datamatrices')
		dm = DataMatrix(len(_rowid))
		object.__setattr__(dm, u'_rowid', _rowid)
		object.__setattr__(dm, u'_id', self._id)
		for name, col in self._cols.items():
			dm._cols[name] = self._cols[name].merge(other._cols[name], _rowid)
		return dm

	def selectrowid(self, _rowid):

		dm = DataMatrix(len(_rowid))
		object.__setattr__(dm, u'_rowid', _rowid)
		object.__setattr__(dm, u'_id', self._id)
		for name, col in self._cols.items():
			dm._cols[name] = self._cols[name].getrowidkey(_rowid)
		return dm

	def __setattr__(self, name, value):

		if name == u'length':
			self.setlength(value)
			return
		if isinstance(value, type) and issubclass(value, BaseColumn):
			self._cols[name] = value(self)
			return
		self._cols[name][:] = value
		self.mutate()

	def __setitem__(self, name, value):

		self.__setattr__(name, value)

	def __getattr__(self, name):

		return self._cols[name]

	def __getitem__(self, key):

		if isinstance(key, BaseColumn):
			return self.getcolbyobject(key)
		if isinstance(key, basestring):
			return self.getcolbyname(key)
		if isinstance(key, int):
		 	return self.getrow(key)
		if isinstance(key, slice) or isinstance(key, collections.Sequence):
			return self.slice(key)
		raise Exception('Cannot get %s' % key)

	def slice(self, key):

		if isinstance(key, slice):
			_rowid = self._rowid[key]
		else:
			try:
				_rowid = [self._rowid[row] for row in key]
			except:
				raise Exception('Invalid row indices')
		dm = DataMatrix(len(_rowid))
		object.__setattr__(dm, u'_rowid', _rowid)
		object.__setattr__(dm, u'_id', self._id)
		for name, col in self._cols.items():
			dm._cols[name] = self._cols[name][key]
		return dm

	def getcolbyobject(self, key):

		for col in self._cols.values():
			if col is key:
				return col
		raise Exception('Column not found')

	def getcolbyname(self, key):

		for name, col in self._cols.items():
			if name == key:
				return col
		raise Exception('Column not found')

	def getrow(self, key):

		return Row(self, key)

	def __str__(self):

		import prettytable
		t = prettytable.PrettyTable()
		t.add_column('#', self._rowid)
		for name, col in self._cols.items():
			t.add_column(name, col.tolist())
		return str(t)

	def mutate(self):

		global _id
		object.__setattr__(self, u'_id', self._id)
		_id += 1

	def __add__(self, other):

		dm = DataMatrix(len(self)+len(other))
		for name, col in self._cols.items():
			dm[name] = col.__class__
			dm[name][:len(self)] = self[name]
		for name, col in other._cols.items():
			if name not in dm._cols:
				dm[name] = col.__class__
			dm[name][len(self):] = other[name]
		return dm

	def __iter__(self):
		object.__setattr__(self, u'_iterpos', 0)
		return self

	# Python 3 compatibility
	def __next__(self):
		return self.next()

	def next(self):

		if self._iterpos >= len(self):
			raise StopIteration()
		row = self[self._iterpos]
		object.__setattr__(self, u'_iterpos', self._iterpos+1)
		return row
