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


class UninstantiatedColumn:
    """Represents a column that is a selection of another column, but hasn't
    been created yet. This allows selections to be made without immediately
    copying large amounts of data.
    
    Parameters
    ----------
    parent_col: BaseColumn
    rowid: Index
    """
    def __init__(self, parent_col, rowid):
        logger.debug(
            f'creating uninstantiatedselection from {parent_col.name}')
        self._parent_col = parent_col
        self._rowid = rowid
        
    def instantiate(self):
        logger.debug(f'instantiating selection from {self._parent_col.name}')
        return self._parent_col._getrowidkey(self._rowid)
