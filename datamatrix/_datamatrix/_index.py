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
from datamatrix._ordered_state import OrderedState
import array
try:
    import numpy as np
except ImportError:
    ITERABLES = list, set
else:
    ITERABLES = list, set, np.ndarray


class Index(OrderedState):

    """
    desc:
        An index object that resembles a list but is more efficient.
    """

    def __init__(self, start=0):

        if isinstance(start, int):
            self._a = array.array('I', range(start))
            self._length = start
            self._metaindex = None
            self._max = start - 1
        elif isinstance(start, ITERABLES):
            self._a = array.array('I', start)
            self._length = len(start)
            self._metaindex = None
            self._max = None
        elif isinstance(start, array.array):
            self._a = start[:]
            self._length = len(start)
            self._metaindex = None
            self._max = None
        elif isinstance(start, Index):
            self._a = start._a[:]
            self._length = start._length
            self._max = start._max
            self._metaindex = start._metaindex
        else:
            raise Exception('Invalid Index start: %s' % type(start))

    def __getitem__(self, item):

        if isinstance(item, slice):
            return Index(self._a[item])
        if isinstance(item, (tuple, list)):
            i = Index(0)
            for row in item:
                i.append(self._a[row])
            return i
        return self._a[item]

    def __setitem__(self, index, item):

        self._a[index] = item

    def __add__(self, other):

        self._a.extend(other)
        self._length = len(self._a)
        self._metaindex = None
        self._max = None
        return self

    def __len__(self):

        return self._length

    def __contains__(self, other):

        return other in self._a

    def __iter__(self):

        for i in self._a:
            yield i

    def __unicode__(self):

        return u'Index(%s)' % self._a

    def __str__(self):

        return safe_str(self.__unicode__())

    def __repr__(self):

        return u'%s[0x%x]\n%s' % (self.__class__.__name__, id(self), str(self))

    def __getstate__(self):

        # Is used by pickle.dump. To make sure that Index objects with only a
        # different _metaindex are considered identical
        return OrderedState.__getstate__(self, ignore=u'_metaindex')

    def __setstate__(self, state):

        OrderedState.__setstate__(self, state)
        # Start with a _metaindex=None after unpickling
        self._metaindex = None

    def index(self, i):

        if self._metaindex is None:
            self._metaindex = {
                rowid: index
                for index, rowid
                in enumerate(self._a)
            }
        return self._metaindex[i]

    def append(self, i):

        self._a.append(i)
        self._length += 1
        self._metaindex = None
        if i > self._max:
            self._max = i

    def copy(self):

        return Index(self)

    @property
    def max(self):

        if self._max is not None:
            return self._max
        self._max = max(self._a)
        return self._max

    @property
    def asarray(self):

        if np is None:
            raise Exception('numpy is not available')
        return np.array(self._a)

    def sorted(self):

        i = Index(sorted(self._a))
        i._max = self._max
        i._length = self._length
        return i
