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
from datamatrix import DataMatrix, operations as ops, MultiDimensionalColumn


def test_uninstantiated_column():
    # Minimal testing of operating on uninstantiated columns
    dm = DataMatrix(length=4)
    dm.c = 1, 1, 2, 2
    dm.i = int
    dm.f = float
    dm.s = 's'
    dm.m = MultiDimensionalColumn(shape=(2,))
    for c, cdm in ops.split(dm.c):
        cdm[:]
    for c, cdm in ops.split(dm.c):
        print(cdm)
    for c, cdm in ops.split(dm.c):
        len(cdm.i)
