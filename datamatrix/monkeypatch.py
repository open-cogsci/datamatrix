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


def _monkey_patch_matplotlib():

    """
    visible: False

    desc:
        This patch decorates the is_string_like function of matplotlib, because
        this consider BaseColumn objects to be strings, with causes trouble
        when plotting.
    """

    try:
        from matplotlib.axes import _base
    except ImportError:
        return
    # matplotlib 3 doesn't need to be monkeypatched, apparently.
    if not hasattr(_base, u'is_string_like'):
        return

    from datamatrix._datamatrix._basecolumn import BaseColumn

    def decorate(fnc):
        def inner(obj):
            if isinstance(obj, BaseColumn):
                return False
            return fnc(obj)
        return inner


_monkey_patch_matplotlib()
