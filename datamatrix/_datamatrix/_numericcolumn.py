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
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._index import Index
import operator
import warnings
try:
	import numpy as np
	from numpy import nanmean, nanmedian, nanstd
	nan = np.nan
except ImportError:
	np = None
	nan = None
try:
	import fastnumbers
except ImportError:
	warnings.warn('Install fastnumbers for better performance')
	fastnumbers = None


class NumericColumn(BaseColumn):

	"""
	desc:
		A base class for FloatColumn and IntColumn. Don't use this class
		directly.
	"""

	dtype = float
	invalid = nan

	def __init__(self, datamatrix):

		if np is None:
			raise Exception(u'NumPy and SciPy are required, but not installed.')
		super(NumericColumn, self).__init__(datamatrix)

	@property
	def unique(self):

		return np.unique(self._seq)

	@property
	def mean(self):

		return nanmean(self._seq)

	@property
	def median(self):

		return nanmedian(self._seq)

	@property
	def std(self):

		# By default, ddof=0. The more normal calculation is to use ddof=1, so
		# we change that here. See also:
		# - http://stackoverflow.com/questions/27600207
		return nanstd(self._seq, ddof=1)

	@property
	def max(self):

		if not len(self._seq):
			return np.nan
		return np.nanmax(self._seq)

	@property
	def min(self):

		if not len(self._seq):
			return np.nan
		return np.nanmin(self._seq)

	@property
	def sum(self):

		if not len(self._seq):
			return np.nan
		return np.nansum(self._seq)

	def _printable_list(self):

		return list(self._seq)

	def _init_rowid(self):

		self._rowid = self._datamatrix._rowid.asarray

	def _init_seq(self):

		self._seq = np.empty(len(self._datamatrix), dtype=self.dtype)
		self._seq[:] = self.invalid

	def _checktype(self, value):

		if value is None:
			return self.invalid
		if fastnumbers is not None:
			if not fastnumbers.isreal(value, allow_inf=True, allow_nan=True):
				return self.invalid
			return fastnumbers.fast_real(value, nan=np.nan, inf=np.inf)		
		try:
			return float(value)
		except:
			return self.invalid

	def _tosequence(self, value, length=None):

		if length is None:
			length = len(self._datamatrix)		
		if value is None or isinstance(value, basestring):
			a = np.empty(length, dtype=self.dtype)
			a[:] = self._checktype(value)
			return a
		return super(NumericColumn, self)._tosequence(value, length)

	def _compare_value(self, other, op):

		_other = self._checktype(other)
		if np.isnan(_other):
			# NaN is usually not equal to itself. Here we implement equality
			# for NaN, as though NaN is equal to itself. This behavior may
			# change in the future
			if op is operator.eq:
				b = np.isnan(self._seq)
			elif op is operator.ne:
				b = ~np.isnan(self._seq)
			else:
				raise TypeError(u'Cannot compare FloatColumn to %s' % other)
		elif np.isinf(_other):
			if op is operator.eq:
				b = np.isinf(self._seq)
			elif op is operator.ne:
				b = ~np.isinf(self._seq)
			else:
				raise TypeError(u'Cannot compare FloatColumn to %s' % other)
		else:
			b = op(self._seq, _other)
		i = np.where(b)[0]
		return self._datamatrix._selectrowid(Index(self._rowid[i]))
		
	def _compare_sequence(self, other, op):
		
		_other = self._tosequence(other)
		i = np.where(op(self._seq, _other))
		return self._datamatrix._selectrowid(Index(self._rowid[i]))

	def _operate(self, other, number_op, str_op=None):

		col = self._empty_col()
		col._rowid = self._rowid
		col._seq = number_op(self._seq,
			self._tosequence(other, len(self._datamatrix)))
		return col

	def _addrowid(self, _rowid):

		old_length = len(self)
		self._rowid = np.concatenate((self._rowid, _rowid.asarray))
		a = np.empty(len(self._rowid), dtype=self.dtype)
		a[:old_length] = self._seq
		a[old_length:] = self.invalid
		self._seq = a

	def _getrowidkey(self, key):

		# We need to select all rows that match the rowids specified in key,
		# while preserving the order provided by key. To do this, we use the
		# following logic:
		# - Get a list of indices (`orig_indices`) that give a sorted view on
		#   self._rowid.
		# - Use this to search through a sorted view of _rowid for all items in
		#   key
		# - Map the matching indices, which refer to the sorted view of _rowid
		#   back to a list of indices in the original, non-sorted array.
		# See also: http://stackoverflow.com/questions/9566592/\
		#  find-multiple-values-within-a-numpy-array
		col = self._empty_col()
		orig_indices = self._rowid.argsort()
		matching_indices = np.searchsorted(self._rowid[orig_indices], key)
		selected_indices = orig_indices[matching_indices]
		col._rowid = self._rowid[selected_indices]
		col._seq = self._seq[selected_indices]
		return col
		
	def _getslicekey(self, key):

		# We need to override the original get slice key so that we get a deep
		# copy of the numpy array.
		col = self._empty_col()
		col._rowid = self._rowid[key]
		col._seq = np.copy(self._seq[key])
		return col		

	def _sortedrowid(self):

		return Index(self._rowid[self._seq.argsort()])

	def _merge(self, other, _rowid):

		col = self._empty_col()
		i_other = ~np.in1d(other._rowid, self._rowid) \
			& np.in1d(other._rowid, _rowid)
		i_self = np.in1d(self._rowid, _rowid)
		col._rowid = np.concatenate(
			(self._rowid[i_self], other._rowid[i_other]))
		col._seq = np.concatenate((self._seq[i_self], other._seq[i_other]))
		return col._getrowidkey(_rowid)


class FloatColumn(NumericColumn):

	"""
	desc:
		A column of numeric float values. Invalid values are marked as
		numpy.nan.
	"""

	pass


class IntColumn(NumericColumn):

	"""
	desc:
		A column of numeric int values. Does not support invalid values.
	"""

	dtype = int
	invalid = 0

	def _tosequence(self, value, length=None):

		if length is None:
			length = len(self._datamatrix)
		if not isinstance(value, basestring):
			try:
				value = list(value)
			except:
				pass
			else:
				return super(NumericColumn, self)._tosequence(value, length)
		value = self._checktype(value)
		return super(NumericColumn, self)._tosequence(value, length)

	def _checktype(self, value):
				
		if value is not None and fastnumbers is not None:
			value = fastnumbers.fast_forceint(value)
			if isinstance(value, int):
				return value
			raise TypeError(u'IntColumn expects integers, not %s' \
				% safe_decode(value))
		if isinstance(value, int):
			return value
		try:
			return int(float(value))
		except:
			raise TypeError(u'IntColumn expects integers, not %s' \
				% safe_decode(value))

	def _operate(self, other, number_op, str_op=None):

		col = super(IntColumn, self)._operate(other, number_op, str_op=None)
		col._seq = col._seq.astype(self.dtype)
		return col
		
	def __eq__(self, other):
		
		if isinstance(other, type):
			if other is self.dtype:
				return self._datamatrix
			return self._datamatrix._selectrowid(Index(0))
		if self._issequence(other):
			return super(IntColumn, self).__eq__(other)
		try:
			return super(IntColumn, self).__eq__(other)
		except TypeError:
			# If the other value is not an int, then nothing is equal to it
			return self._compare_value(0,
				lambda x, y: np.zeros(len(self._datamatrix)))

	def __ne__(self, other):
		
		if isinstance(other, type):
			if other is not self.dtype:
				return self._datamatrix
			return self._datamatrix._selectrowid(Index(0))		
		if self._issequence(other):
			return super(IntColumn, self).__eq__(other)		
		try:
			return super(IntColumn, self).__ne__(other)
		except TypeError:
			# If the other value is not an int, then everything is not equal
			# to it
			return self._compare_value(0,
				lambda x, y: np.ones(len(self._datamatrix)))

	def __div__(self, other):

		return self._operate(other, operator.floordiv)

	def __truediv__(self, other):

		return self._operate(other, operator.floordiv)
