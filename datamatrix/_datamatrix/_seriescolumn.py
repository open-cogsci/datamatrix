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

class SeriesColumn(BaseColumn):

	"""
	desc:
		A column in which each cell is a numeric series.
	"""

	dtype = float

	def __init__(self, datamatrix, depth):

		global np, nanmean, nanmedian, nanstd
		try:
			import numpy as np
			from scipy.stats import nanmean, nanmedian, nanstd
		except ImportError:
			raise Exception(u'NumPy and SciPy are required, but not installed.')
		self._depth = depth
		BaseColumn.__init__(self, datamatrix)

	def setallrows(self, value):

		value = self._checktype(value)
		self._seq[:] = value

	@property
	def mean(self):

		return nanmean(self._seq, axis=0)

	@property
	def median(self):

		return nanmedian(self._seq, axis=0)

	@property
	def std(self):

		return nanstd(self._seq, axis=0)

	@property
	def max(self):

		return np.nanmax(self._seq, axis=0)

	@property
	def min(self):

		return np.nanmin(self._seq, axis=0)

	@property
	def sum(self):

		return np.nansum(self._seq, axis=0)

	# Private functions

	def _init_seq(self):

		self._seq = np.zeros( (len(self._datamatrix), self._depth),
			dtype=self.dtype)

	def _checktype(self, value):

		try:
			a = np.empty(self._depth, dtype=self.dtype)
			a[:] = value
		except:
			raise Exception('Invalid type: %s' % str(value))
		return a

	def _tosequence(self, value, length):

		# For float and integers, we simply create a new (length, depth) array
		# with only this value
		if isinstance(value, (float, int)):
			a = np.empty( (len(self._datamatrix), self._depth),
				dtype=self.dtype)
			a[:] = value
			return a
		try:
			a = np.array(value, dtype=self.dtype)
		except:
			raise Exception('Cannot convert to sequence: %s' % str(value))
		# For a 1D array with the length of the datamatrix, we create an array
		# in which the second dimension (i.e. the depth) is constant.
		if a.shape == (length, ):
			a2 = np.empty( (length, self._depth),
				dtype=self.dtype)
			np.rot90(a2)[:] = a
			return a2
		# For a 2D array that already has the correct dimensions, we return it.
		if a.shape == (length, self._depth):
			return a
		raise Exception('Cannot convert to sequence: %s' % str(value))

	def _empty_col(self):

		return self.__class__(self._datamatrix, depth=self._depth)

	def _addrowid(self, _rowid):

		old_length = len(self)
		self._rowid += _rowid
		a = np.zeros( (len(self._rowid), self._depth), dtype=self.dtype)
		a[:old_length] = self._seq
		self._seq = a

	# Implemented syntax

	def __getitem__(self, key):

		if isinstance(key, tuple) and len(key) == 2:
			return self._seq[key]
		return super(SeriesColumn, self).__getitem__(key)

	def __setitem__(self, key, value):

		if isinstance(key, tuple) and len(key) == 2:
			self._seq[key] = value
			return
		return super(SeriesColumn, self).__setitem__(key, value)
