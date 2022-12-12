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
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
try:
    import numpy as np
except ImportError:
    np = None


class _SeriesColumn(_MultiDimensionalColumn):
    
    def __init__(self, datamatrix, depth=None, shape=None, **kwargs):
        if depth is not None:
            if shape is not None:
                warn('both depth and shape provided (ignoring shape)')
            shape = (depth, )
        elif shape is None:
            raise ValueError('neither depth nor shape provided')
        super().__init__(datamatrix, shape=shape, **kwargs)
        
    @property
    def depth(self):
        try:
            return self._shape[0]
        # This can happen for pickled SeriesColumns from older versions.
        except AttributeError:
            self._shape = (self._depth, )
        return self._shape[0]

    @depth.setter
    def depth(self, depth):
        if depth == self.depth:
            return
        if depth > self.depth:
            seq = np.zeros((len(self), depth), dtype=self.dtype)
            if self.defaultnan:
                seq[:] = np.nan
            seq[:, :self.depth] = self._seq
            self._seq = seq
            self._shape = (depth, )
            return
        self._shape = (depth, )
        self._seq = self._seq[:, :depth]


def SeriesColumn(depth, defaultnan=True):

    return _SeriesColumn, {'depth': depth, u'defaultnan': defaultnan}
