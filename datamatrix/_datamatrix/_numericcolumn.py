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
import operator

class NumericColumn(BaseColumn):

	"""
	desc:
		A base class for FloatColumn and IntColumn. Don't use this class
		directly.
	"""

	dtype = float

	def __init__(self, datamatrix):

		global np, nanmean, nanmedian, nanstd
		try:
			import numpy as np
			from scipy.stats import nanmean, nanmedian, nanstd
		except ImportError:
			raise Exception(u'NumPy and SciPy are required, but not installed.')
		super(NumericColumn, self).__init__(datamatrix)

	@property
	def mean(self):

		return nanmean(self._seq)

	@property
	def median(self):

		return nanmedian(self._seq)

	@property
	def std(self):

		return nanstd(self._seq)

	@property
	def max(self):

		return np.nanmax(self._seq)

	@property
	def min(self):

		return np.nanmin(self._seq)

	@property
	def sum(self):

		return np.nansum(self._seq)

	def tolist(self):

		return list(self._seq)

	def _init_seq(self):

		self._seq = np.zeros(len(self._datamatrix), dtype=self.dtype)

	def _checktype(self, value):

		try:
			return float(value)
		except:
			return np.nan

	def _tosequence(self, value, length):

		if isinstance(value, basestring):
			a = np.empty(length, dtype=self.dtype)
			a[:] = np.nan
			return a
		return super(NumericColumn, self)._tosequence(value, length)

	def _compare(self, other, op):

		i = np.where(op(self._seq, other))[0]
		return self._datamatrix._selectrowid(list(i))

	def _operate(self, other, number_op, str_op=None):

		col = self._empty_col()
		col._rowid = self._rowid
		col._seq = number_op(self._seq, other)
		return col

	def _addrowid(self, _rowid):

		old_length = len(self)
		self._rowid += _rowid
		a = np.zeros(len(self._rowid), dtype=self.dtype)
		a[:old_length] = self._seq
		self._seq = a


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

	def _tosequence(self, value, length):

		if not isinstance(value, basestring):
			try:
				value = list(value)
			except:
				pass
			else:
				return super(NumericColumn, self)._tosequence(value, length)
		try:
			value = int(value)
		except:
			raise TypeError(u'IntColumn expects integers!')
		return super(NumericColumn, self)._tosequence(value, length)

	def _checktype(self, value):

		try:
			return int(value)
		except:
			raise TypeError(u'IntColumn expects integers!')

	def _operate(self, other, number_op, str_op=None):

		col = super(IntColumn, self)._operate(other, number_op, str_op=None)
		col._seq = col._seq.astype(self.dtype)
		return col

	def __div__(self, other):

		return self._operate(other, operator.floordiv)

	def __truediv__(self, other):

		return self._operate(other, operator.floordiv)
