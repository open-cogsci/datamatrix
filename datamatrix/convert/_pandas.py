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
    Convert between `DataMatrix` objects and types of data structures (notably
    `pandas.DataFrame`).
---
"""

from datamatrix.py3compat import *
from datamatrix import DataMatrix
from datamatrix._datamatrix._basecolumn import BaseColumn

try:
    import pandas as pd
except (ImportError, AttributeError, RuntimeError):
    # AttributeError and RuntimeError can occur due to a PyQt4/5 conflict
    pd = None


def wrap_pandas(fnc):

    """
    desc:
        A decorator for pandas functions. It converts a DataMatrix to a
        DataFrame, passes it to a function, and then converts the returned
        DataFrame back to a DataMatrix.

    arguments:
        fnc:
            desc:   A function that takes a DataFrame as first argument and
                    returns a DataFrame as sole return argument.
            type:   callable

    returns:
        desc:   A function takes a DataMatrix as first argument and returns
                a DataMatrix as sole return argument.

    example: |
        import pandas as pd
        from datamatrix import convert as cnv

        pivot_table = cnv.wrap_pandas(pd.pivot_table)
    """

    def inner(dm, *arglist, **kwdict):

        df_in = to_pandas(dm) if isinstance(dm, DataMatrix) else dm
        df_out = fnc(df_in, *arglist, **kwdict)
        return (
            from_pandas(df_out)
            if isinstance(df_out, pd.DataFrame)
            else df_out
        )

    inner.__doc__ = u'desc: A simple wrapper around the corresponding pandas function'
    return inner


def to_pandas(obj):

    """
    desc: |
        Converts a DataMatrix to a pandas DataFrame, or a column to a Series.

        __Example:__

        %--
        python: |
         from datamatrix import DataMatrix, convert

         dm = DataMatrix(length=3)
         dm.col = 1, 2, 3
         df = convert.to_pandas(dm)
         print(df)
        --%

    arguments:
        obj:
            type: [DataMatrix, BaseColumn]

    returns:
        type: [DataFrame, Series]
    """

    if isinstance(obj, BaseColumn):
        return pd.Series(list(obj), dtype=None)
    if not isinstance(obj, DataMatrix):
        raise TypeError('Expecting a column or DataMatrix')
    d = {}
    for colname, col in obj.columns:
        d[colname] = list(col)
    return pd.DataFrame(d)


def from_pandas(df):

    """
    desc: |
        Converts a pandas DataFrame to a DataMatrix.

        __Example:__

        %--
        python: |
         import pandas as pd
         from datamatrix import convert

         df = pd.DataFrame( {'col' : [1,2,3] } )
         dm = convert.from_pandas(df)
         print(dm)
        --%

    arguments:
        df:
            type: DataFrame

    returns:
        type: DataMatrix
    """

    from datamatrix import operations as ops

    dm = DataMatrix(length=len(df))
    if isinstance(df, pd.Series):
        dm.series = df
        return dm
    for colname in df.columns:
        if isinstance(colname, tuple):
            _colname = u'_'.join([safe_decode(i) for i in colname])
        else:
            _colname = safe_decode(colname)
        dm[_colname] = df[colname]
    ops.auto_type(dm)
    return dm
