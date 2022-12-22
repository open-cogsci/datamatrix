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
    A set of operations to apply to `MultiDimensionalColumn` and `SeriesColumn`
    objects.
---
"""
from datamatrix.py3compat import *
from datamatrix import DataMatrix, IntColumn, FloatColumn, NAN, INF
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
import numpy as np
from numpy import nanmean


def nancount(col):
    """
    desc: |
        Counts the number of `NAN` values for each cell in a multidimensional
        column, and returns this as an int column.
        
        *Version note:* Moved to `datamatrix.multidimensional` in 1.0.0
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, MultiDimensionalColumn, \
             multidimensional as mdim, NAN

         dm = DataMatrix(length=3)
         dm.m = MultiDimensionalColumn(shape=(3,))
         dm.m[0] = 1, 2, 3
         dm.m[1] = 1, 2, NAN
         dm.m[2] = NAN, NAN, NAN
         dm.nr_of_nan = mdim.nancount(dm.m)
         print(dm)
        --%
        
    arguments:
        col:
            desc: A column to count the `NAN` values in.
            type: MultiDimensionalColumn
            
    returns:
        desc: An int column with the number of `NAN` values in each cell.
        type: IntColumn
    """
    if isinstance(col, _MultiDimensionalColumn):
        return reduce(col, operation=nancount)
    if isinstance(col, BaseColumn):
        return len(col == NAN)
    return np.sum(np.isnan(np.array(col)))


def infcount(col):
    """
    desc: |
        Counts the number of `INF` values for each cell in a multidimensional
        column, and returns this as an int column.
        
        *Version note:* Moved to `datamatrix.multidimensional` in 1.0.0
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, MultiDimensionalColumn, \
             multidimensional as mdim, INF

         dm = DataMatrix(length=3)
         dm.m = MultiDimensionalColumn(shape=(3,))
         dm.m[0] = 1, 2, 3
         dm.m[1] = 1, 2, INF
         dm.m[2] = INF, INF, INF
         dm.nr_of_inf = mdim.infcount(dm.m)
         print(dm)
        --%
        
    arguments:
        col:
            desc: A multidimensional column to count the `INF` values in.
            type: MultiDimensionalColumn
            
    returns:
        desc: An int column with the number of `INF` values in each cell.
        type: IntColumn
    """
    if isinstance(col, _MultiDimensionalColumn):
        return reduce(col, operation=infcount)
    if isinstance(col, BaseColumn):
        return len(col == INF)
    return np.sum(np.isinf(col))


def flatten(dm):
    """
    desc: |
        Flattens all multidimensional columns of a datamatrix to float columns.
        The result is a new datamatrix where each row of the original
        datamatrix is repeated for each value of the multidimensional column.
        The new datamatrix does not contain any multidimensional columns.
        
        This function requires that all multidimensional columns in `dm` have
        the same shape, or that `dm` doesn't contain any multidimensional
        columns, in which case a copy of `dm` is returned.
        
        *Version note:* Moved to `datamatrix.multidimensional` in 1.0.0
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, MultiDimensionalColumn, \
             multidimensional as mdim

         dm = DataMatrix(length=2)
         dm.col = 'a', 'b'
         dm.m1 = MultiDimensionalColumn(shape=(3,))
         dm.m1[:] = 1,2,3
         dm.m2 = MultiDimensionalColumn(shape=(3,))
         dm.m2[:] = 3,2,1
         flat_dm = mdim.flatten(dm)
         print('Original:')
         print(dm)
         print('Flattened:')
         print(flat_dm)
        --%
    
    arguments:
        dm:
            desc: A DataMatrix
            type: DataMatrix

    returns:
        desc: A 'flattened' DataMatrix without multidimensional columns
        type: DataMatrix
    """
    # Check the shape of the multidimensional columns in the datamatrix, and
    # ensure that they are all the same
    shape = None
    for colname, col in dm.columns:
        if not isinstance(col, _MultiDimensionalColumn):
            continue
        if shape is None:
            shape = col.shape
        elif shape != col.shape:
            raise ValueError(
                'All MultiDimensionalColumns should have the same shape')
    # If there are no multidimensional columns in the datamatrix, simply return
    # a copy of the datamatrix
    if shape is None:
        return dm[:]
    depth = 1
    for dim in shape[1:]:
        depth *= dim
    long_dm = DataMatrix(length=len(dm) * depth)
    for colname, col in dm.columns:
        # multidimensional columns are flattened and then inserted into the
        # datamatrix as a float column
        if isinstance(col, _MultiDimensionalColumn):
            long_dm[colname] = float
            long_dm[colname] = col._seq.flatten()
            continue
        # Other columns are repeated and then inserted
        long_dm[colname] = type(col)
        for i, val in enumerate(col):
            long_dm[colname][i * depth:(i + 1) * depth] = val
    return long_dm


def reduce(col, operation=nanmean):

    """
    desc: |
        Transforms multidimensional values to single values by applying an
        operation (typically a mean) to each multidimensional value.
        
        *Version note:* Moved to `datamatrix.multidimensional` in 1.0.0
        
        *Version note:* As of 0.11.0, the function has been renamed to
        `reduce()`. The original `reduce_()` is deprecated.
        

        __Example:__

        %--
        python: |
         import numpy as np
         from datamatrix import DataMatrix, MultiDimensionalColumn, \
             multidimensional as mdim

         dm = DataMatrix(length=5)
         dm.m = MultiDimensionalColumn(shape=(3, 3))
         dm.m = np.random.random((5, 3, 3))
         dm.mean_y = mdim.reduce(dm.m)
         print(dm)
        --%

    arguments:
        col:
            desc: The column to reduce.
            type: MultiDimensionalColumn

    keywords:
        operation:
            desc:   The operation function to use for the reduction. This
                    function should accept `col` as first argument, and
                    `axis=1` as keyword argument.

    returns:
        desc: A reduction of the signal.
        type: FloatColumn
    """

    if not isinstance(col, _MultiDimensionalColumn):
        raise TypeError(u'Expecting a MultiDimensionalColumn object')
    reduced_col = FloatColumn(col._datamatrix)
    try:
        a = operation(col, axis=np.arange(1, len(col.shape)))
    except TypeError:
        for i, val in enumerate(col):
            reduced_col[i] = operation(val)
    else:
        reduced_col[:] = a
    return reduced_col
