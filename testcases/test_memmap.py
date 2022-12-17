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
from datamatrix import cfg, io
from datamatrix import DataMatrix, MultiDimensionalColumn, INF, \
    functional as fnc
from testcases.test_tools import check_dm
import itertools as it


def _memmap_dm(x=1):
    dm = DataMatrix(length=2000)
    for i in it.count():
        print(f'creating column {i}')
        dm[f'm{i}'] = MultiDimensionalColumn(shape=(100, 100))
        # At least one column should be loaded, otherwise the test doens't
        # make sense.
        if i == 0 and not dm[f'm{i}'].loaded:
            return None
        dm[f'm{i}'] = i * x
        for j in range(i):
            if not dm[f'm{j}'].loaded:
                print(f'column {j} is not loaded')
                break
        else:
            continue
        break
    return dm


def test_dynamic_loading():
    """We create column until one of them cannot be loaded into memory anymore.
    This should the first column. Next, we operate on other columns to check
    if this loads them into memory. The exact result is difficult to predict,
    because it depends on how much memory happens to be free on the system,
    so we only check general patterns.
    """
    cfg.always_load_max_size = 0
    cfg.min_mem_free_rel = .6
    cfg.min_mem_free_abs = INF
    dm = _memmap_dm()
    if dm is None:
        print('insufficient memory to run test')
    else:
        print('without touching')
        for name, col in dm.columns:
            print(name, col.loaded)
        assert not dm.m0.loaded
        print('setting m0')
        dm.m0 = -1
        assert dm.m0[..., ..., ...] == -1
        for name, col in dm.columns:
            print(name, col.loaded)
        assert dm.m0.loaded
        print('getting m1')
        dm.m1 = -1
        assert dm.m1[..., ..., ...] == -1
        for name, col in dm.columns:
            print(name, col.loaded)
        assert dm.m1.loaded
        print('operating m2')
        assert (dm.m2 * 2)[..., ..., ...] == 4
        for name, col in dm.columns:
            print(name, col.loaded)
        assert dm.m2.loaded
    cfg.min_mem_free_rel = .5
    cfg.min_mem_free_abs = 4294967296
    cfg.always_load_max_size = 134217728


def test_memmap_writebin():
    """Create datamatrix objects with at least one unloaded column, and see if
    it can be transparently written to and read from disk in binary format.
    """
    cfg.always_load_max_size = 0
    cfg.min_mem_free_rel = .6
    cfg.min_mem_free_abs = INF
    test_dm = _memmap_dm()
    if test_dm is None:
        print('insufficient memory to run test')
    else:
        print('writing binary file')
        io.writebin(test_dm, 'tmp.dm')
        print('reading binary file')
        ref_dm = io.readbin('tmp.dm')
        print('checking datamatrix objects')
        check_dm(test_dm, ref_dm)
    cfg.min_mem_free_rel = .5
    cfg.min_mem_free_abs = 4294967296
    cfg.always_load_max_size = 134217728


def test_memmap_multiprocess_stack():
    """Check whether we can transparently stack DataMatrix objects with 
    unloaded columns.
    """
    cfg.always_load_max_size = 0
    cfg.min_mem_free_rel = .6
    cfg.min_mem_free_abs = INF
    if _memmap_dm() is None:
        print('insufficient memory to run test')
    else:
        dm = fnc.stack_multiprocess(_memmap_dm, [1, 2])
    cfg.min_mem_free_rel = .5
    cfg.min_mem_free_abs = 4294967296
    cfg.always_load_max_size = 134217728
