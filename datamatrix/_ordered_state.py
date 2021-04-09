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


class OrderedState(object):
    
    """
    desc:
        A base object that preserves the order of the object's __dict__ for
        serialization (pickling). This is necessary to identify identical
        objects. Based on trial and error it seems that two lists (one for
        values and one for keys) can be consistenly pickled, whereas an
        OrderedDict cannot.
    """
    
    def __getstate__(self, ignore=[]):
                
        keys = []
        values = []
        for k in sorted(self.__dict__):
            if k in ignore:
                continue
            keys.append(k)
            values.append(self.__dict__[k])
        return keys, values

    def __setstate__(self, state):

        if isinstance(state, dict):
            warn(u'Unpickling an old datamatrix')
            self.__dict__.update(state)
            return
        keys, values = state
        self.__dict__.update({key: val for key, val in zip(keys, values)})
