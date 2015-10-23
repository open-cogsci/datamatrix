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

import collections
import numbers
import operator
import math

class BaseColumn(object):

	def __init__(self, datamatrix):

		self._datamatrix = datamatrix
		self._rowid = self._datamatrix._rowid[:]
		self._seq = [None]*len(datamatrix)

	def __len__(self):

		return len(self._seq)

	def __getitem__(self, key):

		if isinstance(key, int):
			return self.getintkey(key)
		if isinstance(key, slice):
			return self.getslicekey(key)
		if isinstance(key, collections.Sequence):
			return self.getsequencekey(key)
		raise Exception('Invalid assignment')

	def addrowid(self, _rowid):

		self._rowid += _rowid
		self._seq += [None]*len(_rowid)

	def getintkey(self, key):

		return self._seq[key]

	def getslicekey(self, key):

		col = self.__class__(self._datamatrix)
		col._rowid = self._rowid[key]
		col._seq = self._seq[key]
		return col

	def getsequencekey(self, key):

		col = self.__class__(self._datamatrix)
		col._rowid = []
		col._seq = []
		for i in key:
			col._rowid.append(self._rowid[i])
			col._seq.append(self._seq[i])
		return col

	def getrowidkey(self, key):

		col = self.__class__(self._datamatrix)
		col._rowid = key
		col._seq = []
		for _rowid, val in zip(self._rowid, self._seq):
			if _rowid in key:
				col._seq.append(val)
		return col

	def merge(self, other, _rowid):

		col = self.__class__(self._datamatrix)
		col._rowid = _rowid
		col._seq = []
		for row in _rowid:
			if row in self._rowid:
				col._seq.append(self._seq[self._rowid.index(row)])
			else:
				col._seq.append(other._seq[other._rowid.index(row)])
		return col

	def __setitem__(self, key, value):

		if isinstance(key, int):
			self.setintkey(key, value)
		elif isinstance(key, slice):
			self.setslicekey(key, value)
		elif isinstance(key, collections.Sequence):
			self.setsequencekey(key, value)
		else:
			raise Exception('Invalid assignment')
		self._datamatrix.mutate()

	def tosequence(self, value, length):

		if isinstance(value, float) or isinstance(value, int) or \
			isinstance(value, basestring):
			return [value]*length
		try:
			value = list(value)
		except:
			raise Exception('Cannot convert to sequence: %s' % value)
		if len(value) != length:
			raise Exception('Sequence has incorrect length: %s' % len(value))
		return value

	def setintkey(self, key, value):

		self._seq[key] = value

	def setslicekey(self, key, value):

		length = len(self._seq[key])
		self._seq[key] = self.tosequence(value, length)

	def setsequencekey(self, key, val):

		for _key, _val in zip(key, self.tosequence(val, len(key))):
			if _key < 0 or _key >= len(self):
				raise Exception('Outside of range')
			self._seq[_key] = _val

	def __str__(self):

		return 'col%s' % str(self._seq)

	def compare(self, other, op):

		_rowid = []
		for rowid, val in zip(self._rowid, self._seq):
			if op(val, other):
				_rowid.append(rowid)
		return self._datamatrix.selectrowid(_rowid)

	def __gt__(self, other):
		return self.compare(other, operator.gt)

	def __ge__(self, other):
		return self.compare(other, operator.ge)

	def __lt__(self, other):
		return self.compare(other, operator.lt)

	def __le__(self, other):
		return self.compare(other, operator.le)

	def __eq__(self, other):
		return self.compare(other, operator.eq)

	def __ne__(self, other):
		return self.compare(other, operator.ne)

	def tolist(self):

		return self._seq

	@property
	def numbers(self):

		return [float(val) for val in self._seq \
			if isinstance(val, numbers.Number)]

	@property
	def mean(self):

		if len(self) == 0:
			return None
		return sum(self.numbers) / len(self)

	@property
	def median(self):

		if len(self) == 0:
			return None
		n = sorted(self.numbers)
		if len(self) % 2 == 1:
			return n[len(self)/2]
		return .5*n[len(self)/2]+.5*n[len(self)/2-1]
		raise NotImplementedError()

	@property
	def std(self):

		m = self.mean
		return math.sqrt(sum((i-m)**2 for i in self.numbers)/len(self))
