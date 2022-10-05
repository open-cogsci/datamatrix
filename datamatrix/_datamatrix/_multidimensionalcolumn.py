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
from datamatrix._datamatrix._seriescolumn import _SeriesColumn


class _MultiDimensionalColumn(_SeriesColumn):
    
    def __init__(self, datamatrix, shape, defaultnan=True):
        super().__init__(datamatrix, depth=shape, defaultnan=defaultnan)
        
    @property
    def shape(self):
        return self._depth
    
    def _printable_list(self):
        return [self._ellipsize(cell.flatten()) for cell in self]
        
    def _tosequence(self, value, length):
        shape = (length, ) + self._depth
        # For float and integers, we simply create a new (length, depth) array
        # with only this value
        if isinstance(value, (float, int)):
            a = np.empty(shape, dtype=self.dtype)
            a[:] = value
            return a
        try:
            a = np.array(value, dtype=self.dtype)
        except:
            raise Exception('Cannot convert to sequence: %s' % str(value))
        # For a 1D array with the length of the datamatrix, we create an array
        # in which the second dimension (i.e. the depth) is constant.
        if a.shape == (length, ):
            a2 = np.empty(shape, dtype=self.dtype)
            np.swapaxes(a2, 0, -1)[:] = a
            return a2
        # For a 2D array with a matching shape, 
        if a.shape == self._depth:
            a2 = np.empty(shape, dtype=self.dtype)
            a2[:] = a
            return a2
        # Set all rows at once
        if a.shape == shape:
            return a
        raise Exception('Cannot convert to sequence: %s' % str(value))

    def _empty_col(self, datamatrix=None):

        return self.__class__(
            datamatrix if datamatrix else self._datamatrix,
            shape=self._depth,
            defaultnan=self.defaultnan
        )


def MultiDimensionalColumn(shape, defaultnan=True):

    return _MultiDimensionalColumn, {'shape': shape, u'defaultnan': defaultnan}
