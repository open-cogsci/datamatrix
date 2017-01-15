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
try:
	import numpy as np
except ImportError:
	np = None


class Index(object):
	
	"""
	desc:
		An index object that resembles a list but is more efficient.
	"""
	
	def __init__(self, start=0):		
		
		if isinstance(start, int):
			self._l = list(range(start))			
			self._length = start
			self._metaindex = None
			self._max = start-1
		elif isinstance(start, list):
			self._l = start
			self._length = len(start)
			self._metaindex = None
			self._max = None			
		elif isinstance(start, Index):
			self._l = start._l[:]
			self._length = start._length
			self._max = start._max
			self._metaindex = start._metaindex
		elif isinstance(start, set) \
				or (np is not None and isinstance(start, np.ndarray)):
			self._l = list(start)
			self._length = len(self._l)
			self._metaindex = None
			self._max = None			
		else:
			raise Exception('Invalid Index start: %s' % type(start))

	def __getitem__(self, item):
				
		if isinstance(item, slice):
			return Index(self._l[item])
		if isinstance(item, (tuple, list)):
			i = Index(0)
			for row in item:
				i.append(self._l[row])
			return i			
		return self._l[item]
		
	def __setitem__(self, index, item):
		
		self._l[index] = item
		
	def __add__(self, other):
		
		self._l += other
		self._length = len(self._l)
		self._metaindex = None
		self._max = None
		return self
		
	def __len__(self):
		
		return self._length
		
	def __iter__(self):
		
		for i in self._l:
			yield i
			
	def index(self, i):
		
		if self._metaindex is None:
			self._metaindex = \
				{rowid : index for index, rowid in enumerate(self._l)}
		return self._metaindex[i]
		
	def append(self, i):
		
		self._l.append(i)
		self._length += 1
		self._metaindex = None
		if i > self._max:
			self._max = i
		
	def clone(self):
		
		i = Index(0)
		i._l = self._l[:]
		i._max = self._max
		i._length = self._length
		return i
		
	@property
	def max(self):
		
		if self._max is not None:
			return self._max
		self._max = max(self._l)
		return self._max
		
	@property
	def asarray(self):
				
		if np is None:
			raise Exception('numpy is not available')
		return np.array(self._l, dtype=int)

	def sorted(self):
		
		i = Index(0)
		i._l = sorted(self._l[:])
		i._max = self._max
		i._length = self._length
		return i		
