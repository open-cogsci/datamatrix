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
from datamatrix._datamatrix._basecolumn import BaseColumn, NUMBER
from datamatrix._datamatrix._callable_values import CallableFloat
from datamatrix._datamatrix._index import Index
import operator
import warnings
import functools
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
rowid_argsort_cache = None, None 
selected_indices_cache = None, None


class NumericColumn(BaseColumn):

    """
    desc:
        A base class for FloatColumn and IntColumn. Don't use this class
        directly.
    """

    dtype = float
    invalid = nan

    def __init__(self, datamatrix, **kwargs):
        """
        desc:
            Constructor. You generally don't call this constructor correctly,
            but use the FloatColumn or IntColumn helper functions.

        arguments:
            datamatrix:
                desc: The DataMatrix to which this column belongs.
                type: DataMatrix
                
        keyword-dict:
            kwargs:
                keywords that are passed on to the parent constructor.
        """
        if np is None:
            raise Exception(
                u'NumPy and SciPy are required, but not installed.'
            )
        super(NumericColumn, self).__init__(datamatrix,  **kwargs)

    @property
    def unique(self):

        return np.unique(self._seq)

    @property
    def mean(self):

        return CallableFloat(nanmean(self._seq))

    @property
    def median(self):

        return CallableFloat(nanmedian(self._seq))

    @property
    def std(self):

        # By default, ddof=0. The more normal calculation is to use ddof=1, so
        # we change that here. See also:
        # - http://stackoverflow.com/questions/27600207
        return CallableFloat(nanstd(self._seq, ddof=1))

    @property
    def max(self):

        if not len(self._seq):
            return CallableFloat(np.nan)
        return CallableFloat(np.nanmax(self._seq))

    @property
    def min(self):

        if not len(self._seq):
            return CallableFloat(np.nan)
        return CallableFloat(np.nanmin(self._seq))

    @property
    def sum(self):

        if not len(self._seq):
            return CallableFloat(np.nan)
        return CallableFloat(np.nansum(self._seq))

    @property
    def array(self):

        return np.copy(self._seq)

    def _printable_list(self):

        return list(self._seq)

    def _init_rowid(self):

        self._rowid = self._datamatrix._rowid.asarray.copy()

    def _init_seq(self):

        self._seq = np.empty(len(self._datamatrix), dtype=self.dtype)
        self._seq[:] = self.invalid

    def _checktype(self, value):

        value = BaseColumn._checktype(self, value)
        if not isinstance(value, NUMBER):
            warn(u'Invalid type for FloatColumn: %s' % safe_decode(value))
            return self.invalid
        return value

    def _tosequence(self, value, length=None):

        if length is None:
            length = len(self._datamatrix)
        if value is None or isinstance(value, basestring):
            a = np.empty(length, dtype=self.dtype)
            a[:] = self._checktype(value)
            return a
        # Numerical values should be efficiently cast to an array
        if isinstance(value, (int, float)):
            a = np.empty(length, dtype=self.dtype)
            a[:] = value
            return a
        # Other numerical columns should be efficient cast to an array
        if isinstance(value, NumericColumn) and len(value) == length:
            return value.array
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

    def _operate(self, other, number_op, str_op=None, flip=False):

        if flip:
            seq = number_op(self._tosequence(other, len(self)), self._seq)
        else:
            seq = number_op(self._seq, self._tosequence(other, len(self)))
        return self._empty_col(rowid=self._rowid, seq=seq)

    def _map(self, fnc):

        return self._empty_col(rowid=self._rowid.copy(),
                               seq=np.array([fnc(val) for val in self._seq],
                                            dtype=self.dtype))

    def _addrowid(self, _rowid):

        old_length = len(self)
        self._rowid = np.concatenate((self._rowid, _rowid.asarray))
        a = np.empty(len(self._rowid), dtype=self.dtype)
        a[:old_length] = self._seq
        a[old_length:] = self.invalid
        self._seq = a
        
    def _getdatamatrixkey(self, key):

        if key != self._datamatrix:
            raise ValueError('Cannot slice column with a different DataMatrix')
        return self._getrowidkey(key._rowid)

    def _getintkey(self, key):

        return self.dtype(self._seq[key])

    def _getrowidkey(self, key, dm=None):

        if isinstance(key, Index):
            key = key._a
        if isinstance(key, (tuple, list)):
            key = np.array(key)
        # argsort and searchsorted are fairly time-consuming operations which
        # need to be performed very often. Therefore we implement a crude
        # but fast caching mechanism.
        global rowid_argsort_cache, selected_indices_cache
        try:
            rowid_hash = self._rowid.tobytes()  # As of NumPy 1.9.0
            # The key caching is contingent on the rowid
            key_hash = key.tobytes() + rowid_hash
        except AttributeError:
            rowid_hash = self._rowid.tostring()
            key_hash = key.tostring() + rowid_hash
        if rowid_hash != rowid_argsort_cache[0]:
            rowid_argsort_cache = rowid_hash, self._rowid.argsort()
        orig_indices = rowid_argsort_cache[1]
        if key_hash != selected_indices_cache[0]:
            matching_indices = np.searchsorted(self._rowid[orig_indices], key)
            selected_indices = orig_indices[matching_indices]
            selected_indices_cache = key_hash, selected_indices
        else:
            selected_indices = selected_indices_cache[1]
        return self._empty_col(rowid=self._rowid[selected_indices],
                               seq=self._seq[selected_indices],
                               datamatrix=dm)

    def _setdatamatrixkey(self, key, val):

        if key != self._datamatrix:
            raise ValueError('Cannot slice column with a different DataMatrix')
        self._seq[np.searchsorted(self._rowid, key._rowid)] = val

    def _getslicekey(self, key):

        # We need to override the original get slice key so that we get a deep
        # copy of the numpy array.
        return self._empty_col(rowid=self._rowid[key],
                               seq=np.copy(self._seq[key]))

    def _getsequencekey(self, key):

        return self._getslicekey(list(key))

    def _sortedrowid(self):

        return Index(self._rowid[self._seq.argsort()])

    def _merge(self, other, _rowid):

        i_other = ~np.in1d(other._rowid, self._rowid) \
            & np.in1d(other._rowid, _rowid)
        i_self = np.in1d(self._rowid, _rowid)
        rowid = np.concatenate(
            (self._rowid[i_self], other._rowid[i_other]))
        seq = np.concatenate((self._seq[i_self], other._seq[i_other]))
        col = self._empty_col(rowid=rowid, seq=seq)
        return col._getrowidkey(_rowid)

    def __array__(self, *args):

        return self.array


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

    def _setslicekey(self, key, value):

        try:
            super(NumericColumn, self)._setslicekey(key, value)
        except OverflowError:
            # This happens when there are very large numbers. In that case
            # we silently upgrade the dtype to in64 (long)
            self.dtype = np.int64
            seq = self._seq
            self._init_seq()
            self._seq[:] = seq
            warnings.warn(u'Changing dtype to int64')
            super(NumericColumn, self)._setslicekey(key, value)

    def _checktype(self, value):

        if value is not None and fastnumbers is not None:
            value = fastnumbers.fast_forceint(value)
            if isinstance(value, int):
                return value
            raise TypeError(
                u'IntColumn expects integers, not %s' % safe_decode(value)
            )
        if isinstance(value, int):
            return value
        try:
            return int(float(value))
        except:
            raise TypeError(
                u'IntColumn expects integers, not %s' % safe_decode(value)
            )

    def _operate(self, other, number_op, str_op=None, flip=False):

        col = super(IntColumn, self)._operate(
            other,
            number_op,
            str_op=None,
            flip=flip
        )
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
            return self._compare_value(
                0,
                lambda x, y: np.zeros(len(self._datamatrix))
            )

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
            return self._compare_value(
                0,
                lambda x, y: np.ones(len(self._datamatrix))
            )

    def __div__(self, other):

        return self._operate(other, operator.floordiv)

    def __truediv__(self, other):

        return self._operate(other, operator.floordiv)
