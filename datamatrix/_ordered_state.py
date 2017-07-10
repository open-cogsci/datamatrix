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
from collections import OrderedDict


class OrderedState(object):
	
	"""
	desc:
		A base object that preserves the order of the object's __dict__ for
		serialization (pickling). This is necessary to identify identical
		objects.
	"""
	
	def __getstate__(self, ignore=[]):
				
		d = OrderedDict()
		for k in sorted(self.__dict__):
			if k in ignore:
				continue
			d[k] = self.__dict__[k]
		return d
