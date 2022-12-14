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
import logging
from datamatrix.py3compat import *
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
logger = logging.getLogger('datamatrix')


class _SeriesColumn(_MultiDimensionalColumn):
    
    def __init__(self, datamatrix, depth=None, shape=None, defaultnan=True,
                 **kwargs):
        if depth is not None:
            if shape is not None:
                logger.warning(
                    'both depth and shape provided (ignoring shape)')
            shape = (depth, )
        elif shape is None:
            raise ValueError('neither depth nor shape provided')
        super().__init__(datamatrix, shape=shape, **kwargs)


def SeriesColumn(depth=None, shape=None, defaultnan=True, **kwargs):

    return _SeriesColumn, dict(depth=depth, shape=shape, defaultnan=defaultnan,
                               **kwargs)
