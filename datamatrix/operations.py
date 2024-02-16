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
desc:
    Functions that operate on DataMatrix objects and columns.
---
"""

import random
try:
    from collections.abc import Sequence  # Python 3
except ImportError:
    from collections import Sequence  # Python 2
from datamatrix.py3compat import *
from datamatrix import DataMatrix, FloatColumn, IntColumn, SeriesColumn, \
    MixedColumn, MultiDimensionalColumn, NAN, Row
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._index import Index
# For backwards compatibility
from datamatrix.functional import map_, filter_, setcol


def stack(*dms):
    """
    desc: |
        Stacks multiple DataMatrix objects such that the resulting DataMatrix
        has a length that is equal to the sum of all the stacked DataMatrix
        objects. Phrased differently, this function vertically concatenates
        DataMatrix objects.
        
        See also [`stack_multiprocess()`](%url:functional%) for stacking
        DataMatrix objects that are returned by functions running in different
        processes.

        Stacking two DataMatrix objects can also be done with the `<<`
        operator. However, when stacking more than two DataMatrix objects,
        using `stack()` is much faster than iteratively stacking with `<<`.
        
        *Version note:* New in 1.0.0

        __Example:__

        %--
        python: |
         from datamatrix import operations as ops

         dm1 = DataMatrix(length=2)
         dm1.col = 'A'
         dm2 = DataMatrix(length=2)
         dm2.col = 'B'
         dm3 = DataMatrix(length=2)
         dm3.col = 'C'
         dm = ops.stack(dm1, dm2, dm3)
         print(dm)
        --%
        
    argument-list:
        dms:
            desc: A list of DataMatrix objects.
            type: list
    
    returns:
        type: DataMatrix
    """
    from datamatrix._datamatrix._multidimensionalcolumn import \
        _MultiDimensionalColumn
    from datamatrix._datamatrix._seriescolumn import \
        _SeriesColumn

    # Also allow all dms to be passed as a single argument in a list
    if len(dms) == 1 and isinstance(dms[0], list):
        dms = dms[0]
    if isinstance(dms, tuple):
        dms = list(dms)
    # Make sure that all arguments are really datamatrix objects
    new_length = 0
    for i, dm in enumerate(dms):
        if isinstance(dm, dict):
            dms[i] = DataMatrix()._fromdict(dm)
        elif isinstance(dm, Row):
            dms[i] = dm.as_slice
        elif not isinstance(dm, DataMatrix):
            raise TypeError(
                'Expecting DataMatrix, dict, or Row, not {}'.format(type(dm)))
        new_length += len(dms[i])
    start_index = 0
    dm = DataMatrix(length=new_length)
    for stackdm in dms:
        stackdm._instantiate()
        for name, col in stackdm._cols.items():
            if name not in dm._cols:
                if isinstance(col, _MultiDimensionalColumn):
                    dm[name] = col.__class__(dm, shape=col._orig_shape,
                                             defaultnan=col.defaultnan,
                                             metadata=col.metadata)
                else:
                    dm[name] = col.__class__
                dm[name]._typechecking = False
            else:
                # If the column already exists, check if the types match
                if type(dm[name]) != type(stackdm[name]):
                    raise TypeError(
                        'Non-matching types for column {}'.format(name))
            # If the column already exists and is a series, modify the
            # depth to the longest column
            if isinstance(col, _MultiDimensionalColumn) and \
                    len(col.shape) == 2:
                dm[name].depth = max(col.depth, dm[name].depth)
                stackdm[name].depth = max(col.depth, dm[name].depth)
            # The length doesn't need to be the same, but other than that
            # the shape of the columns needs to match
            elif col.shape[1:] != dm[name].shape[1:]:
                raise TypeError(
                    'Non-matching shapes for column {}'.format(name))
            dm[name][start_index:start_index + len(stackdm)] = stackdm[name]
        start_index += len(stackdm)
    for colname, col in dm.columns:
        col._typechecking = True
    return dm


def pivot_table(dm, values, index, columns, *args, **kwargs):
    
    """
    desc: |
        *Requires pandas*
        
        *Version note:* New in 0.14.1
        
        Creates a pivot table where rows correspond to levels of `index`,
        columns correspond to levels of `columns`, and cells contain aggregate
        values of `values`.
        
        A typical use for a pivot table is to create a summary report for a
        data set. For example, in an experiment where reaction times of human
        participants were measured on a large number of trials under different
        conditions, each row might correspond to one participant, each column
        to an experimental condition (or a combination of experimental
        conditions), and cells might contain mean reaction times.
        
        This function is a wrapper around the `pandas.pivot_table()`. For an
        overview of possible `*args` and `**kwargs`, see
        [this page](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html).
        
        __Example:__

        %--
        python: |
         from datamatrix import operations as ops, io

         dm = io.readtxt('data/fratescu-replication-data-exp1.csv')
         pm = ops.pivot_table(dm, values=dm.RT_search, index=dm.subject_nr,
                              columns=dm.load)
         print(pm)
        --%
        
    arguments:
        dm:
            desc: The source DataMatrix.
            type: DataMatrix
        values:
            desc: A column or list of columns to aggregate.
            type: [BaseColumn, str, list]
        columns:
            desc: A column or list of columns to separate columns by.
            type: [BaseColumn, str, list]
        index:
            desc: A column or list of columns to separate rows by.
            type: [BaseColumn, str, list]
    
    returns:
        type: DataMatrix
    """
    
    def _to_names(obj):
        if isinstance(obj, basestring):
            return obj
        if isinstance(obj, BaseColumn):
            return obj.name
        if isinstance(obj, Sequence):
            return [_to_names(element) for element in obj]
        raise TypeError('Expecting column name or BaseColumn or a list of '
                        'column names or BaseColumns')
    try:
        pd_pivot_table
    except NameError:
        import pandas as pd
        from datamatrix import convert as cnv
        pd_pivot_table = cnv.wrap_pandas(pd.pivot_table)
    return pd_pivot_table(dm, _to_names(values), _to_names(index),
                          _to_names(columns), *args, **kwargs)


def z(col):

    """
    desc: |
        Transforms a column into z scores such that the mean of all values is
        0 and the standard deviation is 1.
        
        *Version note:* As of 0.13.2, `z()` returns a `FloatColumn` when a
        regular column is give. For non-numeric values, the z score is NAN. If
        the standard deviation is 0, z scores are also NAN.
        
        *Version note:* As of 0.15.3, `z()` also accepts series columns, in
        which case the series is z-transformed such that the grand mean of
        all samples is 0, and the grand standard deviation of all samples is
        1.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=5)
         dm.col = range(5)
         dm.z = ops.z(dm.col)
         print(dm)
        --%

    arguments:
        col:
            desc: The column to transform.
            type: BaseColumn

    returns:
        type: BaseColumn
    """

    if isinstance(col, _MultiDimensionalColumn):
        import numpy as np
        from datamatrix import series as srs
        zcol = col[:]
        zcol._seq = (zcol._seq - np.nanmean(zcol._seq)) / np.nanstd(zcol._seq)
        return zcol
    zcol = FloatColumn(col.dm)
    zcol[:] = col
    try:
        return (zcol - zcol.mean) / zcol.std
    except ZeroDivisionError:
        pass
    warn('z scores are NAN because standard deviation is 0')
    zcol[:] = NAN
    return zcol


def weight(col):

    """
    desc: |
        Weights a DataMatrix by a column. That is, each row from a DataMatrix
        is repeated as many times as the value in the weighting column.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=3)
         dm.A = 1, 2, 0
         dm.B = 'x', 'y', 'z'
         print('Original:')
         print(dm)
         dm = ops.weight(dm.A)
         print('Weighted by A:')
         print(dm)
        --%

    arguments:
        col:
            desc: The column to weight by.
            type: BaseColumn

    returns:
        type: DataMatrix
    """

    dm1 = col._datamatrix
    dm2 = DataMatrix(length=int(col.sum))
    for colname, _col in dm1.columns:
        dm2[colname] = type(_col)
    i2 = 0
    for i1, weight in enumerate(col):
        if not isinstance(weight, int) or weight < 0:
            raise TypeError(
                u'Weights should be non-negative integer values, not %s (%s)'
                % (weight, type(weight))
            )
        for c in range(weight):
            for colname in dm1.column_names:
                dm2[colname][i2] = dm1[colname][i1]
            i2 += 1
    return dm2


def replace(col, mappings={}):

    """
    desc: |
        Replaces values in a column by other values.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=3)
         dm.old = 0, 1, 2
         dm.new = ops.replace(dm.old, {0 : 'a', 2 : 'c'})
         print(dm_new)
        --%

    arguments:
        col:
            desc:	The column to weight by.
            type:	BaseColumn

    keywords:
        mappings:
            desc:	A dict where old values are keys and new values are values.
            type:	dict
    """

    col = col[:]
    # For MixedColumns
    if isinstance(col._seq, list):
        for old, new in mappings.items():
            for i, val in enumerate(col):
                if old == val:
                    col[i] = new
        return col
    # For NumericColumns and SeriesColumns
    import numpy as np
    for old, new in mappings.items():
        b = np.isnan(col._seq) if np.isnan(old) else col._seq == old
        i = np.where(b)
        col._seq[i] = new
    return col


def split(col, *values):

    """
    desc: |
        Splits a DataMatrix by unique values in a column.
        
        *Version note:* As of 0.12.0, `split()` accepts multiple columns as
        shown below.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=4)
         dm.A = 0, 0, 1, 1
         dm.B = 'a', 'b', 'c', 'd'
         # If no values are specified, a (value, DataMatrix) iterator is
         # returned.
         print('Splitting by a single column')
         for A, sdm in ops.split(dm.A):
             print('sdm.A = %s' % A)
             print(sdm)
         # You can also split by multiple columns at the same time.
         print('Splitting by two columns')
         for A, B, sdm in ops.split(dm.A, dm.B):
             print('sdm.A = %s, sdm.B = %s' % (A, B))
         # If values are specific an iterator over DataMatrix objects is
         # returned.
         print('Splitting by values')
         dm_a, dm_c = ops.split(dm.B, 'a', 'c')
         print('dm.B == "a"')
         print(dm_a)
         print('dm.B == "c"')
         print(dm_c)
        --%

    arguments:
        col:
            desc: The column to split by.
            type: BaseColumn

    argument-list:
        values:     Splits the DataMatrix based on these values. If this is
                    provided, an iterator over DataMatrix objects is returned,
                    rather than an iterator over (value, DataMatrix) tuples.

    returns:
        desc:   A iterator over (value, DataMatrix) tuples if no values are
                provided; an iterator over DataMatrix objects if values are
                provided.
        type:   Iterator
    """

    # If values is a list of columns, then we split by multiple columns at the
    # same time
    if values and any(isinstance(value, BaseColumn) for value in values):
        if not all(isinstance(value, BaseColumn) for value in values):
            raise ValueError('Don\'t know how to split by {}'.format(values))
        for val1, dm in split(col):
            for val_sdm in split(*[dm[col.name] for col in values]):
                yield (val1,) + tuple(val_sdm)
        return
    # Otherwise we determine the number of unique values, or use the values
    # that are passed to the function
    _values = values if values else col.unique
    for val in _values:
        # Setting this flag tells the datamatrix to not copy all columns, but
        # rather to create UninstiatedColumn objects which are turned into
        # actual columns only when they are requested. This is much faster and
        # saves memory in cases where a large datamatrix is split but most
        # columns are never actually used in the splitted datamatrix objects.
        object.__setattr__(col._datamatrix, '_instantiate_on_select', False)
        dm = col == val
        object.__setattr__(col._datamatrix, '_instantiate_on_select', True)
        if not dm:
            warn(u'No matching rows for %s' % val)
        if values:
            yield dm
        else:
            yield val, dm


def tuple_split(col, *values):

    """
    visible: False
    """

    warn(
        'tuple_split() is deprecated. Please use split() instead.',
        DeprecationWarning
    )
    return split(col, *values)


def bin_split(col, bins):

    """
    desc: |
        Splits a DataMatrix into bins; that is, the DataMatrix is first sorted
        by a column, and then split into equal-size (or roughly equal-size)
        bins.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=5)
         dm.A = 1, 0, 3, 2, 4
         dm.B = 'a', 'b', 'c', 'd', 'e'
         for bin, dm in enumerate(ops.bin_split(dm.A, bins=3)):
            print('bin %d' % bin)
            print(dm)
        --%

    arguments:
        col:
            desc:	The column to split by.
            type:	BaseColumn
        bins:
            desc:	The number of bins.
            type:	int

    returns:
        desc:	A generator that iterates over the bins.
    """

    if len(col) < bins:
        raise ValueError('More bins than rows')
    dm = sort(col._datamatrix, by=col)
    start = 0
    for i in range(bins):
        end = int(len(dm) * (i+1)/bins)
        yield dm[start:end]
        start = end


def fullfactorial(dm, ignore=u''):

    """
    desc: |
        *Requires numpy*

        Creates a new DataMatrix that uses a specified DataMatrix as the base
        of a full-factorial design. That is, each value of every row is 
        combined with each value from every other row. For example:

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=2)
         dm.A = 'x', 'y'
         dm.B = 3, 4
         dm = ops.fullfactorial(dm)
         print(dm)
        --%

    arguments:
        dm:
            desc:	The source DataMatrix.
            type:	DataMatrix

    keywords:
        ignore:		A value that should be ignored.

    return:
        type:	DataMatrix
    """

    if not dm.columns:
        return DataMatrix()
    if not all(isinstance(col, MixedColumn) for colname, col in dm.columns):
        raise TypeError(u'fullfactorial only works with MixedColumns')
    # Create a new DataMatrix that strips all empty cells, and packs them such
    # that empty cells are moved toward the end.
    dm = dm[:]
    for colname, col in dm.columns:
        col = (col != ignore)[colname]
        dm[colname][:len(col)] = col
        dm[colname][len(col):] = ignore
    # A list where each value is an int X that corresponds to a factor with X
    # levels.
    design = [len(c != ignore) for n, c in dm.columns]
    a = _fullfact(design)
    # Create an DataMatrix with empty columns
    fdm = DataMatrix(a.shape[0])
    for name in dm.column_names:
        fdm[name] = u''
    for i in range(a.shape[0]):
        row = a[i]
        for rownr, name in enumerate(dm.column_names):
            fdm[name][i] = dm[name][int(row[rownr])]
    return fdm


def group(dm, by):

    """
    desc: |
        *Requires numpy*

        Groups the DataMatrix by unique values in a set of grouping columns.
        Grouped columns are stored as SeriesColumns. The columns that are
        grouped should contain numeric values. The order in which groups appear
        in the grouped DataMatrix is unpredictable.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=4)
         dm.A = 'x', 'x', 'y', 'y'
         dm.B = 0, 1, 2, 3
         print('Original:')
         print(dm)
         dm = ops.group(dm, by=dm.A)
         print('Grouped by A:')
         print(dm)
        --%

    arguments:
        dm:
            desc:	The DataMatrix to group.
            type:	DataMatrix
        by:
            desc:	A column or list of columns to group by.
            type:	[BaseColumn, list]

    returns:
        desc:	A grouped DataMatrix.
        type:	DataMatrix
    """

    bycol = MixedColumn(datamatrix=dm)
    bynames = []
    if by is not None:
        if isinstance(by, BaseColumn):
            bynames = [by.name]
            by = [by]
        for col in by:
            if col._datamatrix is not dm:
                raise ValueError(u'By-columns are from a different DataMatrix')
            bycol += col
            bynames += [col.name]
    bycol_hashed = IntColumn(datamatrix=dm)
    bycol_hashed[:] = [hash(key) for key in bycol]
    keys = bycol_hashed.unique
    groupcols = [
        (name, col) for name, col in dm.columns if name not in bynames
    ]
    nogroupcols = [(name, col) for name, col in dm.columns if name in bynames]
    cm = DataMatrix(length=len(keys))
    for name, col in groupcols:
        if isinstance(col, _MultiDimensionalColumn):
            warn(u'Failed to create series for MultiDimensionalColumn s%s' % name)
            continue
        cm[name] = SeriesColumn(depth=0)
    for name, col in nogroupcols:
        cm[name] = col.__class__

    for i, key in enumerate(keys):
        dm_ = bycol_hashed == int(key)
        for name, col in groupcols:
            if isinstance(col, _MultiDimensionalColumn):
                continue
            if cm[name].depth < len(dm_[name]):
                cm[name].defaultnan = True
                cm[name].depth = len(dm_[name])
                cm[name].defaultnan = False
            try:
                cm[name][i, :len(dm_[name])] = dm_[name]
            except ValueError:
                warn(u'Failed to create series for MixedColumn %s' % name)
        for name, col in nogroupcols:
            cm[name][i] = dm_[name][0]
    return cm


def sort(obj, by=None):

    """
    desc: |
        Sorts a column or DataMatrix. In the case of a DataMatrix, a column
        must be specified to determine the sort order. In the case of a column,
        this needs to be specified if the column should be sorted by another
        column.

        The sort order is as follows:

        - `-INF`
        - `int` and `float` values in increasing order
        - `INF`
        - `str` values in alphabetical order, where uppercase letters come
          first
        - `None`
        - `NAN`

        You can also sort columns (but not DataMatrix objects) using the
        built-in `sorted()` function. However, when sorting different mixed
        types, this may lead to Exceptions or (in the case of `NAN` values)
        unpredictable results.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=3)
         dm.A = 2, 0, 1
         dm.B = 'a', 'b', 'c'
         dm = ops.sort(dm, by=dm.A)
         print(dm)
        --%

    arguments:
        obj:
            type:	[DataMatrix, BaseColumn]

    keywords:
        by:
            desc:	The sort key, that is, the column that is used for sorting
                    the DataMatrix, or the other column.
            type:	BaseColumn

    returns:
        desc:	The sorted DataMatrix, or the sorted column.
        type:	[DataMatrix, BaseColumn]
    """

    if isinstance(obj, DataMatrix):
        if by is None:
            raise ValueError(
                'The by keyword is required when sorting a DataMatrix')
        return obj._selectrowid(by._sortedrowid())
    if by is None:
        by = obj
    col = obj._getrowidkey(by._sortedrowid())
    col._rowid = obj._rowid
    return col


def random_sample(obj, k):
    
    """
    desc: |
        *New in v0.11.0*
    
        Takes a random sample of `k` rows from a DataMatrix or column. The
        order of the rows in the returned DataMatrix is random.
        
        __Example:__
        
        ```python
        from datamatrix import DataMatrix, operations as ops

        dm = DataMatrix(length=5)
        dm.A = 'a', 'b', 'c', 'd', 'e'
        dm = ops.random_sample(dm, k=3)
        print(dm)
        ```

    arguments:
        obj:
            type:	[DataMatrix, BaseColumn]
        k:
            type:	int

    returns:
        desc:	A random sample from a DataMatrix or column.
        type:	[DataMatrix, BaseColumn]	
    """
    
    _rowid = Index(obj._rowid)
    _rowid = random.sample(list(_rowid), k)
    if isinstance(obj, DataMatrix):
        return obj._selectrowid(_rowid)
    col = obj._getrowidkey(_rowid)
    col._rowid = obj._rowid
    return col


def shuffle(obj):

    """
    desc: |
        Shuffles a DataMatrix or a column. If a DataMatrix is shuffled, the
        order of the rows is shuffled, but values that were in the same row
        will stay in the same row.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=5)
         dm.A = 'a', 'b', 'c', 'd', 'e'
         dm.B = ops.shuffle(dm.A)
         print(dm)
        --%

    arguments:
        obj:
            type:	[DataMatrix, BaseColumn]

    returns:
        desc:	The shuffled DataMatrix or column.
        type:	[DataMatrix, BaseColumn]
    """

    _rowid = Index(obj._rowid)
    random.shuffle(_rowid)
    if isinstance(obj, DataMatrix):
        return obj._selectrowid(_rowid)
    col = obj._getrowidkey(_rowid)
    col._rowid = obj._rowid
    return col


def shuffle_horiz(*obj):

    """
    desc: |
        Shuffles a DataMatrix, or several columns from a DataMatrix,
        horizontally. That is, the values are shuffled between columns from the
        same row.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=5)
         dm.A = 'a', 'b', 'c', 'd', 'e'
         dm.B = range(5)
         dm = ops.shuffle_horiz(dm.A, dm.B)
         print(dm)
        --%

    argument-list:
        desc: A list of BaseColumns, or a single DataMatrix.

    returns:
        desc: The shuffled DataMatrix.
        type: DataMatrix
    """

    if len(obj) == 1 and isinstance(obj[0], DataMatrix):
        obj = [column for colname, column in obj[0].columns]
    try:
        assert(len(obj) > 0)
        for column in obj:
            assert(isinstance(column, BaseColumn))
        dm = obj[0]._datamatrix
        for column in obj:
            assert(dm == column._datamatrix)
    except AssertionError:
        raise ValueError(
            u'Expecting a DataMatrix or multiple BaseColumns from the same DataMatrix'
        )
    dm = dm[:]
    dm_shuffle = keep_only(dm, *obj)
    for row in dm_shuffle:
        random.shuffle(row)
    for colname, column in dm_shuffle.columns:
        dm._cols[colname] = column
    dm._mutate()
    return dm


def keep_only(dm, *cols):

    """
    desc: |
        Removes all columns from the DataMatrix, except those listed in `cols`.
        
        *Version note:* As of 0.11.0, the preferred way to select a subset of
        columns is using the `dm = dm[('col1', 'col2')]` notation.
        
        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=5)
         dm.A = 'a', 'b', 'c', 'd', 'e'
         dm.B = range(5)
         dm.C = range(5, 10)
         dm_new = ops.keep_only(dm, dm.A, dm.C)
         print(dm_new)
        --%

    arguments:
        dm:
            type: DataMatrix

    argument-list:
        cols: A list of column names, or column objects.
    """

    # For backwards compatibility, accept also a list as a single argument
    if len(cols) == 1 and isinstance(cols[0], list):
        cols = cols[0]
    dm = dm[:]
    colnames = [_colname(col) for col in cols]
    for colname in colnames:
        if isinstance(colname, list):
            raise TypeError(
                (
                    u'Column object has multiple names: %s. '
                    u'Specify name as str instead.'
                ) % colname
            )
    for colname in colnames:
        if colname not in dm.column_names:
            warn('no column named {}'.format(colname))
    for colname in dm.column_names:
        if colname not in colnames:
            del dm[colname]
    return dm


def auto_type(dm):

    """
    desc: |
        *Requires fastnumbers*

        Converts all columns of type MixedColumn to IntColumn if all values are
        integer numbers, or FloatColumn if all values are non-integer numbers.

        %--
        python: |
         from datamatrix import DataMatrix, operations as ops

         dm = DataMatrix(length=5)
         dm.A = 'a'
         dm.B = 1
         dm.C = 1.1
         dm_new = ops.auto_type(dm)
         print('dm_new.A: %s' % type(dm_new.A))
         print('dm_new.B: %s' % type(dm_new.B))
         print('dm_new.C: %s' % type(dm_new.C))
        --%

    arguments:
        dm:
            type:	DataMatrix

    returns:
        type:	DataMatrix
    """

    new_dm = DataMatrix(length=len(dm))
    for name, col in dm.columns:
        new_dm[name] = _best_fitting_col_type(col)
        new_dm[name][:] = col
    return new_dm

# Private function


def _colname(col):

    """
    visible: False

    desc:
        Gets the name of column. Column can be specified as a name or as a
        BaseColumn.
    """

    if isinstance(col, basestring):
        return col
    if isinstance(col, BaseColumn):
        return col.name
    raise ValueError(u'Expecting column names or BaseColumn objects')


def _best_fitting_col_type(col):

    """
    visible: False

    desc:
        Determines the best fitting type for a column.
    """

    from fastnumbers import isreal, isintlike

    if isinstance(col, _SeriesColumn):
        return SeriesColumn(depth=col.depth)
    if isinstance(col, _MultiDimensionalColumn):
        return MultiDimensionalColumn(shape=col._orig_shape)
    if isinstance(col, (FloatColumn, IntColumn)):
        return type(col)
    if not all(isreal(val, allow_inf=True, allow_nan=True) for val in col):
        return MixedColumn
    if not all(isintlike(val) for val in col):
        return FloatColumn
    return IntColumn


def _fullfact(levels):

    """
    visible: False

    desc: |
        Taken from pydoe. See:
        <https://github.com/tisimst/pyDOE/blob/master/pyDOE/doe_factorial.py>
    """

    import numpy as np
    n = len(levels)  # number of factors
    nb_lines = np.prod(levels)  # number of trial conditions
    try:
        H = np.zeros((nb_lines, n))
    except (ValueError, MemoryError):
        raise MemoryError(u'DataMatrix too large for fullfact')
    level_repeat = 1
    range_repeat = np.prod(levels)
    for i in range(n):
        range_repeat //= levels[i]
        lvl = []
        try:
            for j in range(levels[i]):
                lvl += [j] * level_repeat
            rng = lvl * range_repeat
        except MemoryError:
            raise MemoryError(u'DataMatrix too large for fullfact')
        level_repeat *= levels[i]
        H[:, i] = rng
    return H
