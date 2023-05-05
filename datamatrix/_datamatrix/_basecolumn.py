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
---
desc: pass
---
"""

from datamatrix.py3compat import *
from datamatrix._datamatrix._index import Index
from datamatrix._ordered_state import OrderedState
from datamatrix._datamatrix._callable_values import CallableFloat
from datamatrix._datamatrix._sort import sortable, fastnumbers
import collections
import numbers
import operator
import math
import types
import itertools
try:
    from inspect import getfullargspec as getargspec  # Python 3.0 and later
except ImportError:
    from inspect import getargspec
try:
    Ellipsis
except NameError:
    Ellipsis = None  # was introduced in Python 3.10


INF = float('inf')
NAN = float('nan')
NUMBER = numbers.Number
BASESTRING_OR_NUMBER = NUMBER, basestring
try:
    from collections.abc import Sequence  # As of Python 3.3
except ImportError:
    from collections import Sequence
try:
    import numpy as np
    SEQUENCE = Sequence, np.ndarray
except ImportError:
    SEQUENCE = Sequence
try:
    Ellipsis
except NameError:
    Ellipsis = None  # was introduced in Python 3.10


class BaseColumn(OrderedState):

    """
    desc:
        The base class for all columns. You should not use this class directly,
        but rather use MixedColumn or NumericColumn.
    """

    default_value = u''
    ndim = 1

    def __init__(self, datamatrix, rowid=None, seq=None, metadata=None):

        """
        desc:
            Constructor.

        arguments:
            datamatrix: A DataMatrix object.
            
        keywords:
            rowid:
                type: [Index, None]
                desc: A rowid index to initialize the column with. If None,
                      a new index is created.
            seq:
                type: [Sequence, None]
                desc: Data to initialize the column with. If None, a new
                      sequence is created.
            metadata:
                desc: Any Python object that should be associated with this
                      column as metadata.
        """

        # Global import like this avoid cyclical imports
        global DataMatrix
        from datamatrix import DataMatrix

        if not isinstance(datamatrix, DataMatrix):
            raise TypeError('expecting DataMatrix, not {}'.format(datamatrix))
        self._datamatrix = datamatrix
        self._typechecking = True
        self.metadata = metadata
        if rowid is None:
            self._init_rowid()
        else:
            self._rowid = rowid
        if seq is None:
            self._init_seq()
        else:
            self._seq = seq
    
    @property
    def loaded(self):
        """
        name: loaded

        desc:
            A property to unloaded the column to disk (by assigning `False`)
            and load the column from disk (by assigning `True`). You don't
            usually change this property manually, but rather let the built-in
            memory management decide when and columns need to be (un)loaded.
        """
        return True
    
    @loaded.setter
    def loaded(self, value):
        if not value:
            raise NotImplementedError('this column cannot be unloaded')

    def equals(self, other):
        
        """
        visible: False

        desc:
            Mimics pandas.DataFrame API
        """
        
        if not isinstance(other, BaseColumn) or len(self) != len(other):
            return False
        for val1, val2 in zip(self, other):
            if val1 != val2 and (val1 == val1 or val2 == val2):
                return False
        return True

    @property
    def unique(self):

        """
        name:	unique

        desc:
            An interator for all unique values that occur in the column.
        """

        return list(safe_sorted(set(self._seq)))

    @property
    def count(self):

        """
        name:	count

        desc:
            The number of unique values that occur in the column.
        """

        return len(self.unique)

    @property
    def shape(self):
        
        """
        name:	shape

        desc:
            A tuple containing the length of the column.
        """		

        return (len(self),)

    @property
    def mean(self):

        """
        name:	mean

        desc:
            Arithmetic mean of all values. If there are non-numeric values,
            these are ignored. If there are no numeric values, NAN is
            returned.
        """

        n = self._numbers
        if len(n) == 0:
            return CallableFloat(NAN)
        return CallableFloat(sum(n) / len(n))

    @property
    def median(self):

        """
        name:	median

        desc:
            The median of all values. If there are non-numeric values,
            these are ignored. If there are no numeric values, NAN is
            returned.
        """

        n = sorted(self._numbers)
        if len(n) == 0:
            return CallableFloat(NAN)
        i = int(len(n)/2)
        if len(n) % 2 == 1:
            return CallableFloat(n[i])
        return CallableFloat(.5*n[i]+.5*n[i-1])

    @property
    def std(self):

        """
        name:	std

        desc:
            The standard deviation of all values. If there are non-numeric
            values, these are ignored. If there are 0 or 1 numeric values, NAN
            is returned. The degrees of freedom are N-1.
        """

        m = self.mean
        n = self._numbers
        if len(n) <= 1:
            return CallableFloat(NAN)
        return CallableFloat(math.sqrt(sum((i-m)**2 for i in n)/(len(n)-1)))

    @property
    def max(self):

        """
        name:	max

        desc:
            The highest numeric value in the column, or NAN if there
            are no numeric values.
        """

        n = self._numbers
        if not len(n):
            return CallableFloat(NAN)
        return CallableFloat(max(n))

    @property
    def min(self):

        """
        name:	min

        desc:
            The lowest numeric value in the column, or NAN if there
            are no numeric values.
        """

        n = self._numbers
        if not len(n):
            return CallableFloat(NAN)
        return CallableFloat(min(n))

    @property
    def sum(self):

        """
        name:	sum

        desc:
            The sum of all values in the column, or NAN if there
            are no numeric values.
        """

        n = self._numbers
        if not len(n):
            return CallableFloat(NAN)
        return CallableFloat(sum(n))

    @property
    def name(self):

        """
        name:	name

        desc:
            The name of the column in the associated DataMatrix, or a list of 
            names if the column occurs multiple times in the DataMatrix.
        """

        l = [name for name, col in self._datamatrix.columns if col is self]
        if not l:
            return None
        if len(l) == 1:
            return l[0]
        return l

    @property
    def dm(self):

        """
        name:	dm

        desc:
            The associated DataMatrix.
        """

        return self._datamatrix

    # Private functions

    @property
    def _numbers(self):

        return [
            float(val) for val in self._seq
            if isinstance(val, numbers.Number) and not self._nanorinf(val)
        ]

    def _printable_list(self):

        """
        visible: False

        desc:
            Creates a list object for this column. The preferred syntax is
            list(dm), although this is slightly slower.

        returns:
            type:	list
        """

        return self._seq

    def _init_rowid(self):

        """
        visible: False

        desc:
            Intializes the _rowid property, which is an iterator that contains
            the row ids.
        """

        self._rowid = self._datamatrix._rowid.copy()

    def _init_seq(self):

        """
        visible: False

        desc:
            Initializes the _seq property, which is an iterator that contains
            the data.
        """

        self._seq = [self.default_value]*len(self._datamatrix)

    def _addrowid(self, _rowid):

        """
        visible: False

        desc:
            Adds an empty row with the given row id.

        arguments:
            _rowid:	A row id
        """

        self._rowid += _rowid
        self._seq += [self.default_value]*len(_rowid)

    def _checktype_fastnumber(self, value):

        # There appears to be a bug in some versions of fastnumbers such that
        # the string 'nan' is converted to 0 instead of NAN. This can be
        # fixed by explicitly using the NAN keyword.
        value = fastnumbers.fast_real(value, nan=NAN)
        if isinstance(value, bytes):
            return safe_decode(value)
        return value

    def _checktype_regular(self, value):

        try:
            value = float(value)
        except (ValueError, TypeError):
            if isinstance(value, bytes):
                return safe_decode(value)
            return value
        if (
            not math.isnan(value) and
            not math.isinf(value) and
            int(value) == value
        ):
            return int(value)
        return value

    def _checktype(self, value):

        """
        visible: False

        desc:
            Checks wether a value has a suitable type for this column, converts
            it if possible, and gives an error if necessary.

        arguments:
            value:	A value to check.

        returns:
            A suitably typed value.
        """

        if value is None:
            return value
        if not isinstance(value, BASESTRING_OR_NUMBER):
            raise TypeError('Invalid type: %s' % value)
        if fastnumbers:
            return self._checktype_fastnumber(value)
        return self._checktype_regular(value)

    def _merge(self, other, _rowid):

        """
        visible: False

        desc:
            Merges this column with another column, selecting only the rows
            indicated by _rowid.

        arguments:
            other:	Another column.
            _rowid:	A list of row ids to select.

        returns:
            type: BaseColumn
        """

        col = self._empty_col(rowid=Index(_rowid), seq=[None] * len(_rowid))
        self_row_id = set(self._rowid)
        for i, row in enumerate(_rowid):
            col._seq[i] = (
                self._seq[self._rowid.index(row)]
                if row in self_row_id
                else other._seq[other._rowid.index(row)]
            )
        return col

    def _tosequence(self, value, length=None):

        """
        visible: False

        desc:
            Creates a sequence with a specific length from a given value (which
            may already be a sequence).

        arguments:
            value:	The value to turn into a sequence.

        keywords:
            length:	The length of the sequence, or None to use length of\
                    DataMatrix.

        returns:
            A sequence, that is, some iterable object.
        """

        if length is None:
            length = len(self._datamatrix)
        if value is None or isinstance(value, BASESTRING_OR_NUMBER):
            return [self._checktype(value)] * length
        try:
            iter(value)
        except TypeError:
            raise TypeError('Cannot convert to sequence: %s' % value)
        seq = [
            self._checktype(cell)
            for cell in itertools.islice(value, 0, length + 1)
        ]
        if len(seq) != length:
            raise ValueError(
                'Sequence length does not match DataMatrix'
            )
        return seq

    def _getintkey(self, key):

        """
        visible: False

        desc:
            Gets a value by index.

        arguments:
            key:	An index.

        returns:
            A value.
        """

        return self._seq[key]

    def _getslicekey(self, key):

        """
        visible: False

        desc:
            Gets a slice of this column by a slice object.

        arguments:
            key:	A slice object.

        returns:
            BaseColunn
        """

        return self._empty_col(rowid=self._rowid[key], seq=self._seq[key])

    def _getellipsiskey(self, key):

        """
        visible: False

        desc:
            Gets the average.

        arguments:
            key:	A slice object.

        returns:
            BaseColunn
        """

        return self.mean


    def _getsequencekey(self, key):

        """
        visible: False

        desc:
            Gets a slice of this column by list or some other iterable.

        arguments:
            key:	A list or other iterable object.

        returns:
            BaseColunn
        """

        rowid = Index()
        seq = []
        for i in key:
            rowid.append(self._rowid[i])
            seq.append(self._seq[i])
        return self._empty_col(rowid=rowid, seq=seq)

    def _getdatamatrixkey(self, key):

        """
        visible: False

        desc:
            Gets a slice of this column by a DataMatrix

        arguments:
            key:	A DataMatrix
        """

        if key != self._datamatrix:
            raise ValueError('Cannot slice column with a different DataMatrix')
        return self[[self._rowid.index(_rowid) for _rowid in key._rowid]]

    def _getrowidkey(self, key, dm=None):

        """
        visible: False

        desc:
            Gets a slice of this column by a list of row ids.

        arguments:
            key:	A list of row ids.

        returns:
            BaseColunn
        """
        seq = [self._seq[self._rowid.index(_rowid)] for _rowid in key]
        return self._empty_col(rowid=key, seq=seq, datamatrix=dm)
        
    def _sortedrowid(self):

        """
        visible: False

        desc:
            Gives a list of rowids that are ordered such that they sort the
            column.

        returns:
            An iterator.
        """

        s = sorted(zip(self._seq, self._rowid), key=lambda x: sortable(x[0]))
        return Index([rowid for val, rowid in s])

    def _setintkey(self, key, value):

        """
        visible: False

        desc:
            Sets a value by index.

        arguments:
            key:	An index.
            value:	The value to set.
        """

        self._seq[key] = self._checktype(value)

    def _setslicekey(self, key, value):

        """
        visible: False

        desc:
            Sets a range of values by a slice object.

        arguments:
            key:	A slice object.
            value:	The value to set. This can be an iterable that matches the
                    length of the slice.
        """

        # If type-checking is disabled and we're receiving a BaseColumn, assign
        # right away to speed up performance
        if not self._typechecking and type(value) == type(self):
            self._seq[key] = value._seq
            return
        length = len(self._seq[key])
        self._seq[key] = self._tosequence(value, length)

    def _setsequencekey(self, key, val):

        """
        visible: False

        desc:
            Sets a range of values by a list or other iterable.

        arguments:
            key:	A list or other iterable object.
            val:	The value to set. This can be an iterable that matches the
                    length of the key.
        """

        for _key, _val in zip(key, self._tosequence(val, len(key))):
            if _key < 0 or _key >= len(self):
                raise Exception('Outside of range')
            self._seq[_key] = _val

    def _setdatamatrixkey(self, key, val):

        """
        visible: False

        desc:
            Sets a range of values by based on matching rows from a DataMatrix.

        arguments:
            key:	A DataMatrix
            val:	The value to set. This can be an iterable that matches the
                    length of the key.
        """

        if key != self._datamatrix:
            raise ValueError('Cannot slice column with a different DataMatrix')
        self[[self._rowid.index(_rowid) for _rowid in key._rowid]] = val

    def _issequence(self, val):

        if (
            isinstance(val, set)
            or isinstance(val, basestring)
            or not hasattr(val, u'__len__')
        ):
            return False
        if len(val) != len(self._datamatrix):
            raise TypeError(u'Sequence has invalid length')
        return True

    def _compare(self, other, op):

        """
        visible: False

        desc:
            Selects rows from this column, and returns the entire DataMatrix.

        arguments:
            other:	A value to compare to.
            op:		An operator to perform the comparison.

        returns:
            type:	DataMatrix
        """

        if isinstance(other, float) and math.isnan(other):
            return self._compare_nan(other, op)
        if isinstance(other, type):
            return self._compare_type(other, op)
        if isinstance(other, set):
            return self._compare_set(other, op)
        if isinstance(other, types.FunctionType):
            return self._compare_function(other, op)
        if self._issequence(other):
            return self._compare_sequence(other, op)
        return self._compare_value(other, op)

    def _compare_nan(self, other, op):

        _rowid = Index(0)
        if op is operator.eq:
            for rowid, val in zip(self._rowid, self._seq):
                if isinstance(val, float) and math.isnan(val):
                    _rowid.append(rowid)
        elif op is operator.ne:
            for rowid, val in zip(self._rowid, self._seq):
                if not isinstance(val, float) or not math.isnan(val):
                    _rowid.append(rowid)
        else:
            raise TypeError('nans can only be compared with == or !=')
        return self._datamatrix._selectrowid(_rowid)

    def _compare_type(self, type_, op):

        _rowid = Index(0)
        if op is operator.eq:
            for rowid, val in zip(self._rowid, self._seq):
                if isinstance(val, type_):
                    _rowid.append(rowid)
        elif op is operator.ne:
            for rowid, val in zip(self._rowid, self._seq):
                if not isinstance(val, type_):
                    _rowid.append(rowid)
        else:
            raise TypeError('types can only be compared with == or !=')
        return self._datamatrix._selectrowid(_rowid)

    def _compare_value(self, other, op):

        _rowid = Index(0)
        for rowid, val in zip(self._rowid, self._seq):
            try:
                if op(val, other):
                    _rowid.append(rowid)
            except:
                pass
        return self._datamatrix._selectrowid(_rowid)

    def _compare_set(self, other, op):

        if op == operator.__eq__:
            test = lambda val: any(val == v for v in other)
        elif op == operator.__ne__:
            test = lambda val: all(val != v for v in other)
        else:
            raise TypeError('sets can only be compared with == or !=')
        _rowid = Index(0)
        for rowid, val in zip(self._rowid, self._seq):
            try:
                if test(val):
                    _rowid.append(rowid)
            except:
                pass
        return self._datamatrix._selectrowid(_rowid)

    def _compare_function(self, other, op):

        if op == operator.__eq__:
            test = other
        elif op == operator.__ne__:
            test = lambda val: not other(val)
        else:
            raise TypeError('functions can only be compared with == or !=')
        if not len(getargspec(other).args) == 1:
            raise TypeError('function must take exactly one argument')
        return self._datamatrix._selectrowid(
            Index([
                rowid for rowid, val
                in zip(self._rowid, self._seq)
                if test(val)
            ])
        )

    def _compare_sequence(self, other, op):

        _rowid = Index(0)
        for rowid, val, ref in zip(
            self._rowid, self._seq, self._tosequence(other)
        ):
            try:
                if op(val, ref):
                    _rowid.append(rowid)
            except:
                pass
        return self._datamatrix._selectrowid(_rowid)

    def _operate(self, other, number_op, str_op=None, flip=False):

        """
        visible: False

        desc:
            Performs an operation on the entire column.

        arguments:
            other:		The value to use for the operation, e.g. a number to
                        multiply with.
            number_op:	The operator to use for numeric values.

        keywords:
            str_op:		The operator to use for string values, or None to
                        leave strings untouched.
            flip:		Indicates if self or other should come first.

        returns:
            A modified column.
        """

        col = self._empty_col(rowid=self._rowid.copy())
        for i, (_other, val) in enumerate(
            zip(self._seq, self._tosequence(other, len(self)))
            if flip else
            zip(self._tosequence(other, len(self)), self._seq)
        ):
            if (isinstance(val, NUMBER) and isinstance(_other, NUMBER)):
                col._seq[i] = number_op(val, _other)
                continue
            if str_op is not None:
                col._seq[i] = str_op(safe_decode(val), safe_decode(_other))
                continue
            col._seq[i] = _other if flip else val
        return col

    def _map(self, fnc):

        return self._empty_col(rowid=self._rowid.copy(),
                               seq=[fnc(val) for val in self._seq])


    def _empty_col(self, datamatrix=None, **kwargs):

        """
        visible: False

        desc:
            Create an empty column of the same type as the current column.
            
        keywords:
            datamatrix: The DataMatrix to which the empty column should
                        belong or None. If None, then the DataMatrix of current
                        column is used unless it has a different length, in
                        which case a new DataMatrix object is initialized.

        returns:
            BaseColumn
        """

        if datamatrix is not None:
            return self.__class__(datamatrix, **kwargs)
        # If this column results from slicing from an original column, the
        # rowids do not match with the DataMatrix. In that case, create a new
        # DataMatrix for the empty column.
        if len(self) != len(self._datamatrix):
            return self.__class__(DataMatrix(length=len(self)), **kwargs)
        return self.__class__(self._datamatrix, **kwargs)

    def _nanorinf(self, val):

        """
        visible: False

        desc:
            Checks whether a value is nan or inf.

        returns:
            bool
        """

        return val != val or val == INF

    # Implemented syntax

    def __getstate__(self):

        # Is used by pickle.dump. To make sure that identical datamatrices with
        # different _ids are considered identical, we strip the _id property.
        return OrderedState.__getstate__(self, ignore=u'_datamatrix')

    def __str__(self):

        return u'col%s' % str(self._seq)

    def __repr__(self):

        return u'%s[0x%x]\n%s' % (self.__class__.__name__, id(self), str(self))

    def _repr_html_(self):

        """
        visible: False

        desc:
            Used in a Jupyter notebook to give a pretty representation of the
            object.
        """

        from datamatrix.convert._html import to_html
        return to_html(self)
        
    def _requests_new_axis(self, key):
        """
        visible: False
        
        desc:
            Matplotlib slices columns with [:, np.newaxis], where np.newaxis
            is None and expects a re-orderd axis.
        """
        if np is None:
            return False
        if not isinstance(key, tuple) or len(key) != 2:
            return False
        if isinstance(key[0], slice) and key[1] is None:
            return True
        return False

    def __len__(self):

        return len(self._rowid)

    def __getitem__(self, key):

        if isinstance(key, int):
            return self._getintkey(key)
        if isinstance(key, slice):
            return self._getslicekey(key)
        if Ellipsis is not None and key == Ellipsis:
            return self._getellipsiskey(key)
        if isinstance(key, SEQUENCE):
            # Hack for matplotlib
            if self._requests_new_axis(key):
                return np.array(self)[key]
            return self._getsequencekey(key)
        if isinstance(key, DataMatrix):
            return self._getdatamatrixkey(key)
        raise Exception(u'Invalid key: {}'.format(key))

    def __setitem__(self, key, value):

        if isinstance(key, int):
            self._setintkey(key, value)
        elif isinstance(key, slice):
            self._setslicekey(key, value)
        elif Ellipsis is not None and key == Ellipsis:
            self._setslicekey(slice(None), value)
        elif isinstance(key, SEQUENCE):
            self._setsequencekey(key, value)
        elif isinstance(key, DataMatrix):
            self._setdatamatrixkey(key, value)
        else:
            raise Exception('Invalid assignment: {} to {}'.format(key, value))
        self._datamatrix._mutate()

    def __array__(self, *args):

        import numpy as np
        return np.array(self._seq)

    def __gt__(self, other):
        return self._compare(other, operator.gt)
    def __ge__(self, other):
        return self._compare(other, operator.ge)
    def __lt__(self, other):
        return self._compare(other, operator.lt)
    def __le__(self, other):
        return self._compare(other, operator.le)
    def __eq__(self, other):
        return self._compare(other, operator.eq)
    def __ne__(self, other):
        return self._compare(other, operator.ne)
    def __add__(self, other):
        return self._operate(other, operator.add, operator.concat)
    def __radd__(self, other):
        return self._operate(other, operator.add, operator.concat)
    def __sub__(self, other):
        return self._operate(other, operator.sub)
    def __rsub__(self, other):
        return self._operate(other, operator.sub, flip=True)
    def __mul__(self, other):
        return self._operate(other, operator.mul)
    def __rmul__(self, other):
        return self._operate(other, operator.mul)
    def __div__(self, other):
        return self._operate(other, operator.truediv)
    def __rdiv__(self, other):
        return self._operate(other, operator.truediv, flip=True)
    def __truediv__(self, other):
        return self._operate(other, operator.truediv)
    def __rtruediv__(self, other):
        return self._operate(other, operator.truediv, flip=True)
    def __floordiv__(self, other):
        return self._operate(other, operator.floordiv)
    def __rfloordiv__(self, other):
        return self._operate(other, operator.floordiv, flip=True)
    def __mod__(self, other):
        return self._operate(other, operator.mod)
    def __rmod__(self, other):
        return self._operate(other, operator.mod, flip=True)
    def __pow__(self, other):
        return self._operate(other, operator.pow)
    def __rpow__(self, other):
        return self._operate(other, operator.pow, flip=True)
    def __matmul__(self, other):
        return self._map(other)
