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
try:
    import fastnumbers
except ImportError:
    warn('Install fastnumbers for better performance')
    fastnumbers = None
import math


class SortableNAN(object):

    """
    visible: False

    desc:
        An object that is guaranteed to be larger than everything else,
        including inf. This allows nan values to be last in any sorted
        sequence.
    """

    def __lt__(self, other):

        return False

    def __gt__(self, other):

        return True


class SortableNone(object):

    """
    visible: False

    desc:
        An object that is guaranteed to be larger than everything else except
        NAN values. This allows nan values to be last in any sorted sequence.
    """

    def __lt__(self, other):

        return isinstance(other, SortableNAN)

    def __gt__(self, other):

        return not isinstance(other, SortableNAN)


class SortableSTR(object):

    """
    visible: False

    desc:
        An object that is guaranteed to be larger than everything else except
        NAN values. This allows nan values to be last in any sorted sequence.
    """

    def __init__(self, val):

        self._val = val

    def __lt__(self, other):

        return not isinstance(other, (int, float)) and (
            isinstance(other, SortableNAN)
            or isinstance(other, SortableNone)
            or isinstance(other, SortableSTR) and other._val > self._val
        )

    def __gt__(self, other):

        return (
            isinstance(other, (int, float))
            or isinstance(other, SortableSTR) and other._val <= self._val
        )


def _sortable_regular(val):

    if val is None:
        return sortable_none
    if isinstance(val, float) and math.isnan(val):
        return sortable_nan
    try:
        return float(val)
    except (ValueError, TypeError):
        pass
    return SortableSTR(val)


def _sortable_fastnumbers(val):

    if val is None:
        return sortable_none
    return fastnumbers.fast_float(
        val,
        default=SortableSTR(val),
        nan=sortable_nan
    )


sortable = _sortable_fastnumbers if fastnumbers else _sortable_regular
sortable_nan = SortableNAN()
sortable_none = SortableNone()
