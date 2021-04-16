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


class Row(object):

    """
    desc:
        A single row from a DataMatrix.
    """

    def __init__(self, datamatrix, index):

        """
        desc:
            Constructor.

        arguments:
            datamatrix:		A DataMatrix object.
            index:			The row index.
        """

        object.__setattr__(self, u'_datamatrix', datamatrix)
        object.__setattr__(self, u'_index', index)
        
    @property
    def as_slice(self):
        return self._datamatrix[self._index:self._index + 1]
        
    @property
    def column_names(self):
        return self._datamatrix.column_names

    def equals(self, other):
        
        """
        visible: False

        desc:
            Mimics pandas.DataFrame API
        """
        
        if not isinstance(other, Row) or len(self) != len(other):
            return False
        for val1, val2 in zip(self, other):
            if val1 != val2 and (val1 == val1 or val2 == val2):
                return False
        return True
        
    def __dir__(self):
        
        return self.column_names + object.__dir__(self)

    def __len__(self):

        return len(self._datamatrix.columns)

    def __getattr__(self, key):

        return self.__getitem__(key)

    def __getitem__(self, key):

        if isinstance(key, int):
            key = self._datamatrix.column_names[key]
        return self._datamatrix[key][self._index]

    def __setattr__(self, key, value):

        self.__setitem__(key, value)

    def __setitem__(self, key, value):

        if isinstance(key, int):
            key = self._datamatrix.column_names[key]
        elif isinstance(key, basestring):
            # Create a new column with default values if the column does not
            # exist yet
            if key not in self._datamatrix.column_names:
                self._datamatrix[key] = \
                    self._datamatrix._default_col_type.default_value
        self._datamatrix[key][self._index] = value

    def __str__(self):

        import prettytable
        t = prettytable.PrettyTable(["Name", "Value"])
        for name, col in self._datamatrix.columns:
            t.add_row([name, self[name]])
        return str(t)

    def __iter__(self):

        for col in self._datamatrix.column_names:
            yield col, self[col]
