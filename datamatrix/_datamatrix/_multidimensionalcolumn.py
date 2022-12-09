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
from datamatrix._datamatrix._numericcolumn import NumericColumn, FloatColumn
try:
    from collections.abc import Sequence  # Python 3.3 and later
except ImportError:
    from collections import Sequence
try:
    import numpy as np
    from numpy import nanmean, nanmedian, nanstd
except ImportError:
    np = None


class _MultiDimensionalColumn(NumericColumn):

    """
    desc:
        A column in which each cell is a float array.
    """

    dtype = float

    def __init__(self, datamatrix, shape, defaultnan=True):

        """
        desc:
            Constructor. You generally don't call this constructor correctly,
            but use the MultiDimensional helper function.

        arguments:
            datamatrix:
                desc: The DataMatrix to which this column belongs.
                type: DataMatrix
            shape:
                desc: The shape, ie. the number of values per cell.
                type: int
        """

        if np is None:
            raise Exception(
                'NumPy and SciPy are required, but not installed.')
        self._shape = shape
        self.defaultnan = defaultnan
        NumericColumn.__init__(self, datamatrix)

    def setallrows(self, value):

        """
        desc:
            Sets all rows to a value, or array of values.

        arguments:
            value:	A value, or array of values that has the same length as the
                    shape of the column.
        """

        value = self._checktype(value)
        self._seq[:] = value

    @property
    def unique(self):

        raise NotImplementedError(
            'unique is not implemented for {}'.format(self.__class__.__name__))

    @property
    def shape(self):

        """
        name: shape

        desc:
            A property to access and change the shape of the column.
        """

        return self._shape

    @property
    def plottable(self):

        """
        name: plottable

        desc:
            Gives a view of the traces where the axes have been swapped. This 
            is the format that matplotlib.pyplot.plot() expects.
        """

        return np.swapaxes(self._seq, 0, -1)

    @property
    def mean(self):

        return nanmean(self._seq, axis=0)

    @property
    def median(self):

        return nanmedian(self._seq, axis=0)

    @property
    def std(self):

        return nanstd(self._seq, axis=0, ddof=1)

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

        if isinstance(self._shape, int):
            shape = (len(self._datamatrix), self._shape)
        else:
            shape = (len(self._datamatrix),) + self._shape
        self._seq = np.zeros(shape, dtype=self.dtype)
        if self.defaultnan:
            self._seq[:] = np.nan

    def _ellipsize(self, a):

        """
        visible: False

        desc:
            Creates an ellipsized represenation of an array.

        arguments:
            a: An array.

        returns:
            A string with an ellipsized representation.
        """

        return '{} ... {}'.format(str(a[:2])[:-1], str(a[-1:])[1:])

    def _printable_list(self):

        if sum(self._shape) <= 4:
            return [str(cell.flatten()) for cell in self]
        return [self._ellipsize(cell.flatten()) for cell in self]

    def _operate(self, a, number_op, str_op=None, flip=False):

        # For a 1D array with the length of the datamatrix, we create an array
        # in which the second dimension (i.e. the shape) is constant. This
        # allows us to do by-row operations.
        if isinstance(a, (list, tuple)):
            a = np.array(a, dtype=self.dtype)
        if isinstance(a, NumericColumn):
            a = np.array(a._seq)
        if isinstance(a, np.ndarray) and a.shape == (len(self), ):
            a2 = np.empty((len(self),) + self._shape, dtype=self.dtype)
            np.swapaxes(a2, 0, -1)[:] = a
            a = a2
        col = self._empty_col()
        col._rowid = self._rowid.copy()
        col._seq = number_op(a, self._seq) if flip else number_op(self._seq, a)
        return col

    def _map(self, fnc):

        # For a MultiDimensionalColumn, we need to make a special case, because
        # the shape of the new MultiDimensionalColumn may be different from
        # the shape of the original column.
        for i, cell in enumerate(self):
            a = fnc(cell)
            if not i:
                newcol = self.__class__(self.dm, shape=len(a))
            newcol[i] = a
        return newcol

    def _checktype(self, value):

        try:
            a = np.empty(self._shape, dtype=self.dtype)
            a[:] = value
        except:
            raise Exception('Invalid type: %s' % str(value))
        return a

    def _compare(self, other, op):

        raise NotImplementedError('Cannot compare {}s'.format(
            self.__class__.__name__))

    def _tosequence(self, value, length):
        
        full_shape = (length, ) + self._shape
        # For float and integers, we simply create a new (length, shape) array
        # with only this value
        if isinstance(value, (float, int)):
            a = np.empty(full_shape, dtype=self.dtype)
            a[:] = value
            return a
        try:
            a = np.array(value, dtype=self.dtype)
        except:
            raise Exception('Cannot convert to sequence: %s' % str(value))
        # For a 1D array with the length of the datamatrix, we create an array
        # in which the second dimension (i.e. the shape) is constant.
        if a.shape == (length, ):
            a2 = np.empty(full_shape, dtype=self.dtype)
            np.swapaxes(a2, 0, -1)[:] = a
            return a2
        # For a 2D array that already has the correct dimensions, we return it.
        if a.shape == full_shape:
            return a
        # Set all rows at once
        if a.shape == self._shape:
            return a
        raise Exception('Cannot convert to sequence: %s' % str(value))

    def _empty_col(self, datamatrix=None):

        return self.__class__(datamatrix if datamatrix else self._datamatrix,
                              shape=self._shape,
                              defaultnan=self.defaultnan)

    def _addrowid(self, _rowid):

        old_length = len(self)
        self._rowid = np.concatenate((self._rowid, _rowid.asarray))
        a = np.zeros((len(self._rowid), ) + self._shape, dtype=self.dtype)
        a[:old_length] = self._seq
        self._seq = a

    def _getintkey(self, key):

        return self._seq[key]

    # Implemented syntax

    def __getitem__(self, key):

        if isinstance(key, tuple) and len(key) == 2:
            row, smp = key
            if isinstance(row, Sequence):
                row = np.array(row)
            if isinstance(smp, Sequence):
                smp = np.array(smp)
            if isinstance(row, int):
                # dm.s[0, 0] -> float
                if isinstance(smp, int):
                    return float(self._seq[key])
                # dm.s[0, :] -> array
                # dm.s[0, (0, 1)] -> array
                if isinstance(smp, (slice, np.ndarray)):
                    return self._seq[row, smp].copy()
            if isinstance(row, (slice, np.ndarray)):
                # dm.s[:, 0] -> FloatColumn
                # dm.s[(0, 1), 0] -> FloatColumn
                if isinstance(smp, int):
                    col = FloatColumn(self._datamatrix)
                    col._rowid = self._rowid[row]
                    col._seq = np.copy(self._seq[row, smp])
                    return col
                # dm.s[:, :] -> MultiDimensionalColumn
                # dm.s[:, (0, 1)] -> MultiDimensionalColumn
                # dm.s[(0, 1), :] -> MultiDimensionalColumn
                # dm.s[(0, 1), (0, 1)] -> MultiDimensionalColumn
                if isinstance(smp, (slice, np.ndarray)):
                    if isinstance(smp, np.ndarray):
                        _seq = np.copy(self._seq[row][:, smp])
                    else:
                        _seq = np.copy(self._seq[row, smp])
                    col = self.__class__(self._datamatrix, shape=_seq.shape[1])
                    col._rowid = self._rowid[row]
                    col._seq = _seq
                    return col
            raise KeyError('Invalid key')
        # dm[0] -> array
        # dm[:] -> MultiDimensionalColumn
        return super().__getitem__(key)

    def __setitem__(self, key, value):

        if isinstance(key, tuple) and len(key) == 2:
            self._seq[key] = value
            return
        return super().__setitem__(key, value)


def MultiDimensionalColumn(shape, defaultnan=True):

    return _MultiDimensionalColumn, {'shape': shape, 'defaultnan': defaultnan}
