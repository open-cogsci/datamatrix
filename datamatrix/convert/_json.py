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
from datamatrix import (
    MixedColumn, IntColumn, FloatColumn, SeriesColumn, DataMatrix
)
import collections


def to_json(dm):

    """
    desc: |
        *Requires json_tricks*

        Creates (serializes) a `json` string from a DataMatrix.

    arguments:
        dm:
            desc: A DataMatrix to serialize.
            type: DataMatrix

    returns:
        desc: A json string.
        type: str
    """

    import json_tricks

    return json_tricks.dumps(
        collections.OrderedDict([
            ('rowid', list(dm._rowid._a)),
            (
                'columns',
                collections.OrderedDict([
                    (
                        name,
                        (
                            type(column).__name__,
                            column._seq
                        )
                    )
                    for name, column in dm.columns
                ])
            )
        ]),
        allow_nan=True
    )


def from_json(s):

    """
    desc: |
        *Requires json_tricks*

        Creates a DataMatrix from a `json` string.

    arguments:
        s:
            desc: A json string.
            type: str

    returns:
        desc: A DataMatrix.
        type: DataMatrix.
    """

    import json_tricks

    d = json_tricks.loads(s)
    dm = DataMatrix(length=len(d['rowid']))
    for name, (coltype, seq) in d['columns'].items():
        if coltype == '_SeriesColumn':
            dm[name] = SeriesColumn(depth=seq.shape[1])
            dm[name]._seq = seq
        else:
            dm[name] = globals()[coltype]
            dm[name]._seq = seq
    return dm
