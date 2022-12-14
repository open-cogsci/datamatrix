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
from datamatrix import Row
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._mixedcolumn import MixedColumn
from datamatrix._datamatrix._index import Index
from datamatrix._ordered_state import OrderedState
try:
    from collections.abc import Sequence  # Python 3.3 and later
except ImportError:
    from collections import Sequence
try:
    import numpy as np
except ImportError:
    np = None
from collections import OrderedDict
_id = 0

PRINT_MAX_ROWS = 20
PRINT_MAX_COLUMNS = 6
PRINT_MAX_NUMBER = 999999


def mimic_DataFrame(function_name):
    
    def inner(fnc):
    
        def innermost(self, *args, **kwargs):
            
            from datamatrix import convert as cnv
            df_in = cnv.to_pandas(self)
            fnc = getattr(df_in, function_name)
            df_out = fnc(*args, **kwargs)
            return df_out
            
        return innermost
        
    return inner


class DataMatrix(OrderedState):

    """
    desc:
        A DataMatrix is a tabular data structure.
    """

    def __init__(self, length=0, default_col_type=MixedColumn, metadata=None,
                 **columns):

        """
        desc:
            Constructor.

        keywords:
            length:
                desc: The starting length of the DataMatrix.
                type: int
            default_col_type:
                desc: The default type for newly created columns.
                type: [int, float, BaseColumn]
            metadata:
                desc: Any Python object that should be associated with this
                      column as metadata

        keyword-dict:
            columns:
                Columns can be initialized by passing them as keywords, where
                the keyword is the column name, and the value is the initial
                value for the column.
        """

        global _id
        try:
            length = int(length)
        except ValueError:
            raise TypeError('length should be an integer')
        object.__setattr__(self, u'_cols', OrderedDict())
        object.__setattr__(self, u'_rowid', Index(length))
        if default_col_type == float:
            from datamatrix import FloatColumn
            default_col_type = FloatColumn
        elif default_col_type == int:
            from datamatrix import IntColumn
            default_col_type = IntColumn
        object.__setattr__(self, u'_default_col_type', default_col_type)
        object.__setattr__(self, u'_id', _id)
        object.__setattr__(self, u'_sorted', True)
        object.__setattr__(self, u'metadata', metadata)
        _id += 1
        for column_name, val in columns.items():
            self[column_name] = val

    @property
    def shape(self):

        return len(self), len(self._cols)

    @property
    def empty(self):
        
        return not len(self) or not len(self._cols)

    @property
    def columns(self):

        return self._to_list(self._cols.items(), key=lambda col: col[0])

    @property
    def column_names(self):

        return self._to_list(self._cols.keys())

    @property
    def rows(self):

        return list(range(len(self)))

    @property
    def length(self):

        return len(self._rowid)

    @property
    def sorted(self):

        return self._sorted

    @property
    def default_col_type(self):

        return self._default_col_type

    @property
    def is_2d(self):

        for name, col in self.columns:
            if hasattr(col, u'depth'):
                return False
        return True

    def equals(self, other):
        
        """
        visible: False

        desc:
            Mimics pandas.DataFrame API
        """
        
        if (
            not isinstance(other, DataMatrix) or
            len(self.columns) != len(other.columns)
        ):
            return False
        for colname in self.column_names:
            if (
                colname not in other or
                not other[colname].equals(self[colname])
            ):
                return False
        return True

    @mimic_DataFrame('drop_duplicates')
    def drop_duplicates(self, *args, **kwargs): pass
    @mimic_DataFrame('groupby')
    def groupby(self, *args, **kwargs): pass
        
    def rename(self, old, new):

        """
        desc:
            Renames a column. Modifies the DataMatrix in place.

        raises:
            ValueError: When an error occurs.

        arguments:
            old:	The old name.
            new:	The new name.
        """

        if old == new:
            return
        if old not in self._cols:
            raise ValueError(u'Column name does not exist')
        if new in self._cols:
            raise ValueError(u'Column name already exists')
        try:
            exec(u'%s = None' % new)
        except SyntaxError:
            raise ValueError(u'Invalid column name')
        # A rename recipe that preservers order.
        _cols = OrderedDict([
            (new, v) if k == old else (k, v)
            for k, v in self._cols.items()
        ])
        object.__setattr__(self, u'_cols', _cols)
        self._mutate()

    def get(self, key, default=None):

        """
        visible: False

        desc:
            Improves compatibility with pandas.DataFrame
        """

        from datamatrix.convert._pandas import to_pandas
        if key in self:
            return to_pandas(self[key])
        return default

    # Private functions. These can also be called by the BaseColumn (and
    # derived) classes.

    def _fromdict(self, d={}):

        """
        visible: False

        desc:
            Merges a dict into the DataMatrix. Modifies the DataMatrix in 
            place.

        keywords:
            d:	The dict to merge.

        returns:
            The modified DataMatrix.
        """

        for name, col in d.items():
            if len(col) > len(self):
                self.length = len(col)
            self[name] = self._default_col_type
            self[name][:len(col)] = col
        return self

    def _selectrowid(self, _rowid):

        """
        visible: False

        desc:
            Selects rows from the current DataMatrix by row id (i.e. not by
            index).

        arguments:
            _rowid:		An iterable list of row ids.

        returns:
            type:	DataMatrix.
        """

        dm = DataMatrix(len(_rowid))
        object.__setattr__(dm, u'_rowid', _rowid)
        object.__setattr__(dm, u'_id', self._id)
        for name, col in self._cols.items():
            dm._cols[name] = self._cols[name]._getrowidkey(_rowid)
            dm._cols[name]._datamatrix = dm
        return dm

    def _slice(self, key):

        """
        visible: False

        desc:
            Selects rows from the current DataMatrix by indices (i.e. not by
            row id).

        arguments:
            key:		A slice object, or a list of indices.

        returns:
            type:	DataMatrix.
        """

        # A tuple of length two is interpreted by a SeriesColumn as a sample
        # and row. Therefore, we turn tuples into lists.
        if isinstance(key, tuple):
            key = list(key)
        _rowid = self._rowid[key]
        dm = DataMatrix(len(_rowid))
        object.__setattr__(dm, u'_rowid', _rowid)
        object.__setattr__(dm, u'_id', self._id)
        for name, col in self._cols.items():
            dm._cols[name] = self._cols[name][key]
            dm._cols[name]._datamatrix = dm
        return dm

    def _setlength(self, value):

        """
        visible: False

        desc: |
            Changes the length of the current DataMatrix, adding or removing
            rows as necessary.

            *This modifies the current DataMatrix.*

            __Note__: The preferred way to change the length is by setting the
            length property:

            ~~~
            dm.length = 10
            ~~~

        arguments:
            value:
                desc:	The new length.
                type:	int
        """

        if value < len(self):
            object.__setattr__(self, u'_rowid', self._rowid[:value])
            for name, col in self._cols.items():
                self._cols[name] = self._cols[name][:value]
        else:
            startid = 0 if not len(self) else self._rowid.max+1
            rowid = Index([i+startid for i in range(value-len(self))])
            object.__setattr__(self, u'_rowid', self._rowid.copy()+rowid)
            for name in self._cols:
                self._cols[name]._addrowid(rowid)
        self._mutate()

    def _set_default_col_type(self, col_type):

        """
        visible: False

        desc:
            Sets the default column type.

        arguments:
            col_type:	A column type (BaseColumn)
        """

        if (
            not isinstance(col_type, type) or
            not issubclass(col_type, BaseColumn)
        ):
            raise Exception(u'Not a valid column type')
        object.__setattr__(self, u'_default_col_type', col_type)

    def _merge(self, other, _rowid):

        """
        visible: False

        desc:
            Merges the current DataMatrix with another DataMatrix, preserving
            only the rows indicated by _rowid.

        arguments:
            other:	Another DataMatrix.
            _rowid:	A list of row ids.

        returns:
            type:	DataMatrix.
        """

        if self != other:
            raise Exception('Can only merge related datamatrices')
        dm = DataMatrix(len(_rowid))
        object.__setattr__(dm, u'_rowid', _rowid)
        object.__setattr__(dm, u'_id', self._id)
        for name, col in self._cols.items():
            dm._cols[name] = self._cols[name]._merge(other._cols[name], _rowid)
            dm._cols[name]._datamatrix = dm
        return dm

    def _mergedict(self, d={}):

        """
        visible: False

        desc: |
            Merges a dict into the DataMatrix.

            *This modifies the current DataMatrix.*

        keywords:
            d:
                desc:	A dictionary, where each each key is a column name, and
                        each value is a sequence of column values, or a single
                        column value.
                type:	dict

        returns:
            desc:	The current DataMatrix.
        """

        for name, col in d.items():
            if isinstance(col, basestring):
                self.length = 1
            elif len(col) > len(self):
                self.length = len(col)
            self[name] = self._default_col_type
            self[name][:len(col)] = col
        return self

    def _mutate(self):

        """
        visible: False

        desc:
            Changes the id of the current DataMatrix. This is done whenever the
            DataMatrix has been modified.
        """

        global _id
        object.__setattr__(self, u'_id', self._id)
        _id += 1

    def _getcolbyobject(self, key):

        """
        visible: False

        desc:
            Retrieves a column by object; that is, just return the object
            itself.

        arguments:
            key:
                type:	BaseColumn

        returns:
            type:	BaseColumn
        """

        for col in self._cols.values():
            if col is key:
                return col
        raise Exception('Column not found')

    def _getcolbyname(self, key):

        """
        visible: False

        desc:
            Retrieves a column by name.

        arguments:
            key:
                type:	str

        returns:
            type:	BaseColumn
        """

        if isinstance(key, bytes):
            key = safe_decode(key)
        col = self._cols.get(key, None)
        if col is None:
            raise AttributeError(u'No column named "%s"' % key)
        return col

    def _getrow(self, key):

        """
        visible: False

        desc:
            Retrieves a row by key.

        arguments:
            key:
                type:	A key that a Row object understands.

        returns:
            type:	Row
        """

        if key >= len(self) or key < -len(self):
            raise IndexError('row index out of range')
        return Row(self, key)

    def _check_name(self, name):

        """
        visible: False

        desc:
            Checks whether a name is a valid column name.

        raises:
            ValueError:	If name is not valid.

        arguments:
            name:		The name to check.
        """

        try:
            exec('%s = None' % name)
        except SyntaxError:
            raise ValueError(u'Invalid column name: %s' % name)

    def _set_col(self, name, value):

        """
        visible: False

        desc:
            Sets columns in various formats. Is used by __setitem__ and
            __setattr__.
        """
        
        # Check if this is a valid column name
        if isinstance(name, bytes):
            name = safe_decode(name)
        if not isinstance(name, str):
            raise TypeError(u'Column names should be str, not %s' % type(name))
        # Create a new column by column type:
        # dm[name] = IntColumn
        # dm[name] = float
        if isinstance(value, type):
            if value == int:
                from datamatrix import IntColumn
                value = IntColumn
            elif value == float:
                from datamatrix import FloatColumn
                value = FloatColumn
            if issubclass(value, BaseColumn):
                self._cols[name] = value(self)
                return
        # Create a new column by type, kwdict tuple
        if (
            isinstance(value, tuple) and
            len(value) == 2 and
            ((isinstance(value[0], type) and issubclass(value[0], BaseColumn))
             or callable(value[0]))
        ):
            cls, kwdict = value
            self._cols[name] = cls(self, **kwdict)
            return
        # Create new column by existing column
        if isinstance(value, BaseColumn):
            # If the column belongs to the same datamatrix we simply insert it
            # under a new name.
            if value._datamatrix is self:
                self._cols[name] = value
                return
            # If the column belongs to another datamatrix, we create a new
            # column of the same type
            if len(value) != len(self):
                raise ValueError(
                    u'Column should have the same length as the DataMatrix'
                )
            self._cols[name] = value._empty_col(datamatrix=self)
        if name not in self:
            # Create a new SeriesColumn by assigning a 2D ndarray, but only if the
            # column doesn't exist yet
            if np is not None and isinstance(value, np.ndarray) and \
                    len(value.shape) == 2:
                if value.shape[0] == len(self):
                    depth = value.shape[1]
                elif value.shape[1] == len(self):
                    depth = value.shape[0]
                    value = np.swapaxes(value, 0, 1)
                else:
                    raise ValueError(
                        'Invalid shape for SeriesColumn: {}'.format(
                            value.shape))
                from datamatrix import SeriesColumn
                self[name] = SeriesColumn(depth=depth)
            else:
                self._cols[name] = self._default_col_type(self)
        self._cols[name][:] = value
        self._mutate()

    def _to_list(self, seq, key=None):

        """
        visible: False

        desc:
            Returns a list that is sorted if the DataMatrix is set to being
            sorted.
        """

        if self._sorted:
            return list(sorted(seq, key=key))
        return list(seq)
        
    def _where(self, other_dm):
        
        """
        visible: False

        desc:
            Returns the indices of other_dm in dm. This assumes that other_dm
            is a subset of the current dm.
        """
        
        if other_dm != self:
            raise ValueError(
                'Can only slice a DataMatrix with a subset of itself')
        try:
            return [self._rowid.index(rowid) for rowid in other_dm._rowid]
        except KeyError:
            raise ValueError(
                'Can only slice a DataMatrix with a subset of itself')
        
    # Implemented syntax

    def __hash__(self):

        from datamatrix import convert as cnv
        return hash(cnv.to_json(self))

    def __getstate__(self):

        # Is used by pickle.dump. To make sure that identical datamatrices with
        # different _ids are considered identical, we strip the _id property.
        return OrderedState.__getstate__(self, ignore=u'_id')

    def __setstate__(self, state):

        if isinstance(state, dict):
            warn(u'Unpickling an old datamatrix')
            self.__dict__.update(state)
            return
        # Is used by pickle.load. Because __getstate__() strips the _id, we
        # need to generate a new id for the DataMatrix upon unpickling.
        global _id
        OrderedState.__setstate__(self, state)
        object.__setattr__(self, u'_id', _id)
        for name, column in self.columns:
            column._datamatrix = self
        _id += 1

    def __dir__(self):

        return self.column_names + object.__dir__(self)

    def __contains__(self, item):

        return item in self._cols.keys()

    def __len__(self):

        return len(self._rowid)

    def __eq__(self, other):

        return isinstance(other, DataMatrix) and other._id == self._id

    def __ne__(self, other):

        return not isinstance(other, DataMatrix) or other._id != self._id

    def __and__(self, other):

        selection = Index(set(self._rowid) & set(other._rowid))
        return self._merge(other, selection.sorted())

    def __or__(self, other):

        selection = Index(set(self._rowid) | set(other._rowid))
        return self._merge(other, selection.sorted())

    def __xor__(self, other):

        selection = Index(set(self._rowid) ^ set(other._rowid))
        return self._merge(other, selection.sorted())

    def __delattr__(self, name):

        if name not in self._cols:
            raise AttributeError(u'No column named %s' % name)
        del self._cols[name]

    def __setattr__(self, name, value):

        if isinstance(name, bytes):
            name = safe_decode(name)
        if name == u'length':
            self._setlength(value)
            return
        if name == u'sorted':
            object.__setattr__(self, u'_sorted', value)
            return
        if name == u'default_col_type':
            self._set_default_col_type(value)
            return
        self._set_col(name, value)

    def __delitem__(self, value):

        # Delete column by object
        if isinstance(value, BaseColumn):
            for name, col in self._cols.items():
                if col is value:
                    del self._cols[name]
                    return
            else:
                raise ValueError('Column not found: %s' % value)
        # Delete column by name
        if isinstance(value, basestring):
            if value in self._cols:
                del self._cols[value]
                return
            raise ValueError('Column not found: %s' % value)
        # Delete row by index. The trick is to first get the slice that we want
        # to delete, and then xor this with the current DataMatrix.
        if isinstance(value, int):
            value = value,
        _slice = self[value] ^ self
        object.__setattr__(self, u'_cols', _slice._cols)
        object.__setattr__(self, u'_rowid', _slice._rowid)

    def __setitem__(self, name, value):

        self._set_col(name, value)

    def __getattr__(self, name):

        if name in ('__getstate__', '_cols'):
            raise AttributeError()
        return self._getcolbyname(name)

    def __getitem__(self, key):

        if isinstance(key, BaseColumn):
            return self._getcolbyobject(key)
        if isinstance(key, basestring):
            return self._getcolbyname(key)
        if isinstance(key, int):
            return self._getrow(key)
        if isinstance(key, slice):
            return self._slice(key)
        if isinstance(key, Sequence):
            if all(isinstance(v, (basestring, BaseColumn)) for v in key):
                from datamatrix import operations as ops
                return ops.keep_only(self, *key)
            return self._slice(key)
        if isinstance(key, DataMatrix):
            return self._where(key)
        raise KeyError('Invalid key, index, or slice: %s' % key)

    def __str__(self):

        if len(self) > PRINT_MAX_ROWS:
            return str(self[:PRINT_MAX_ROWS]) + u'\n(+ %d rows not shown)' \
                % (len(self) - PRINT_MAX_ROWS)
        import prettytable
        t = prettytable.PrettyTable()
        t.add_column('#', self._rowid)
        for name, col in list(self.columns)[:PRINT_MAX_COLUMNS]:
            t.add_column(
                name,
                [
                    '%E' % i
                    if isinstance(i, (int, float)) and i > PRINT_MAX_NUMBER
                    else i
                    for i in col._printable_list()
                ]
            )
        if len(self._cols) > PRINT_MAX_COLUMNS:
            return str(t) + u'\n(+ %d columns not shown)' \
                % (len(self._cols) - PRINT_MAX_COLUMNS)
        return str(t)

    def __repr__(self):

        return u'DataMatrix[%d, 0x%x]\n%s' % (self._id, id(self), str(self))

    def _repr_html_(self):

        """
        visible: False

        desc:
            Used in a Jupyter notebook to give a pretty representation of the
            object.
        """

        from datamatrix.convert._html import to_html
        return to_html(self)

    def __lshift__(self, other):

        from datamatrix import operations as ops
        return ops.stack(self, other)

    def __iter__(self):

        for i in self.rows:
            yield self[i]

    def __array__(self, *args):
        
        """
        visible: False

        desc:
            Use by numpy to convert the DataMatrix to an array where the first
            axis corresponds to the rows and the second axis to the columns.
            The dtype of the array is object, float, or int, depending on which
            dtype fits best.
        """
        
        import numpy as np
        a = np.empty((len(self), len(self.columns)), dtype=object)
        for i, col in enumerate(self._cols.values()):
            if hasattr(col, 'depth'):
                for j, row in enumerate(col):
                    a[j, i] = row
            else:
                a[:, i] = col
        try:
            return np.array(a, dtype=int)
        except (TypeError, ValueError):
            try:
                return np.array(a, dtype=float)
            except (TypeError, ValueError):
                pass
        return a

    def __dataframe__(self):
        
        from datamatrix import convert as cnv
        
        return cnv.to_pandas(self)
