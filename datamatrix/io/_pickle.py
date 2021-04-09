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
import pickle
import os


def readpickle(path):

    """
    desc: |
        Reads a DataMatrix from a pickle file.

        __Example:__

        ~~~.python
        dm = io.readpickle('data.pkl')
        ~~~

    arguments:
        path: The path to the pickle file.

    returns:
        A DataMatrix.
    """

    with open(path, 'rb') as picklefile:
        dm = pickle.load(picklefile)
    if not hasattr(dm._rowid, '_a'):
        dm = _upgrade_datamatrix_index(dm)
    return dm


def writepickle(dm, path, protocol=-1):

    """
    desc: |
        Writes a DataMatrix to a pickle file.

        __Example:__

        ~~~ .python
        io.writepickle(dm, 'data.pkl')
        ~~~


    arguments:
        dm:     The DataMatrix to write.
        path:   The path to the pickle file.

    keywords:
        protocol:	The pickle protocol.
    """

    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass
    with open(path, 'wb') as picklefile:
        pickle.dump(dm, picklefile, protocol)


def _upgrade_datamatrix_index(dm):

    """Fixes the Index object of deprecated versions of DataMatrix."""

    from datamatrix._datamatrix._index import Index
    object.__setattr__(dm, '_rowid', Index(dm._rowid._l))
    for colname, col in dm.columns:
        if hasattr(col._rowid, '_l'):
            object.__setattr__(col, '_rowid', Index(col._rowid._l))
        else:
            object.__setattr__(col, '_rowid', Index(col._rowid))
    return dm
