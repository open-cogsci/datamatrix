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
from datamatrix import cfg
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
from datamatrix.io._pickle import readpickle, writepickle
import os
import logging
import tarfile
from pathlib import Path
try:
    import numpy as np
except ImportError:
    np = None
logger = logging.getLogger('datamatrix')


def readbin(path):
    """
    desc: |
        Reads a DataMatrix from a binary file. This format allows you to read
        and write DataMatrix objects with unloaded columns, i.e. columns that
        are too large to fit in memory.

        __Example:__

        ~~~.python
        dm = io.readbin('data.dm')
        ~~~
        
        *Version note:* New in 1.0.0

    arguments:
        path: The path to the binary file.

    returns:
        A DataMatrix.
    """
    if np is None:
        raise Exception(
            'NumPy and SciPy are required, but not installed.')
    if not isinstance(path, Path):
        path = Path(path)
    logger.debug('reading binary file from {}'.format(path))
    tar = tarfile.open(path, 'r:gz')
    # Extracte to a temporary folder that is based on the pid of the current
    # process. This avoids races conditions if multiple processes are reading
    # from the same file
    tmp_dir = Path(cfg.tmp_dir) / f'.{os.getpid()}'
    if not tmp_dir.exists():
        tmp_dir.mkdir()
    for member in tar.getmembers():
        dm_path = tmp_dir / Path(member.name)
        if dm_path.suffix == '.datamatrix':
            logger.debug('reading datamatrix pickle from {}'.format(dm_path))
            tar.extract(member, path=str(tmp_dir))
            dm = readpickle(tmp_dir / dm_path)
            dm_path.unlink()
            break
    else:
        raise TypeError('{} is not a binary datamatrix file'.format(path))
    for col in dm._cols.values():
        if not isinstance(col, _MultiDimensionalColumn) or col.loaded:
            continue
        aux_path = col._seq
        logger.debug('reading auxiliary file: {}'.format(aux_path))
        tar.extract(tar.getmember(str(aux_path)), path=str(tmp_dir))
        col._init_seq()
        chunk_slice = int(cfg.save_chunk_size / col._memory_size() * len(col))
        tmp_path = tmp_dir / aux_path
        with tmp_path.open('rb+') as fd:
            a = np.memmap(fd, mode='r', shape=col.shape, dtype=col.dtype)
            for i in range(0, len(col), chunk_slice):
                col._seq[i:i + chunk_slice] = a[i:i + chunk_slice]
        tmp_path.unlink()
    tmp_dir.rmdir()
    return dm


def writebin(dm, path):
    """
    desc: |
        Reads a DataMatrix to a binary file. This format allows you to read
        and write DataMatrix objects with unloaded columns, i.e. columns that
        are too large to fit in memory.

        __Example:__

        ~~~ .python
        io.writebin(dm, 'data.dm')
        ~~~
        
        *Version note:* New in 1.0.0


    arguments:
        dm:     The DataMatrix to write.
        path:   The path to the binary file.
    """
    if np is None:
        raise Exception(
            'NumPy and SciPy are required, but not installed.')
    if not isinstance(path, Path):
        path = Path(path)
    logger.debug('writing binary file to {}'.format(path))
    tar = tarfile.open(path, 'w:gz')
    # We first write all data from unloaded MultiDimensionalColumns to
    # separate files. The _seq and _fd properties are temporarily removed from
    # the columns so that the datamatrix can be pickled.
    tmp = {}
    for col in dm._cols.values():
        if not isinstance(col, _MultiDimensionalColumn) or col.loaded:
            continue
        aux_path = path.parent / Path(f'.{id(col)}-{os.getpid()}.memmap')
        logger.debug('writing auxiliary file: {}'.format(aux_path))
        chunk_slice = int(cfg.save_chunk_size / col._memory_size() * len(col))
        with aux_path.open('wb+') as fd:
            a = np.memmap(fd, mode='w+', shape=col.shape, dtype=col.dtype)
            for i in range(0, len(col), chunk_slice):
                a[i:i + chunk_slice] = col._seq[i:i + chunk_slice]
        tmp[id(col)] = col._fd, col._seq
        col._fd = None
        object.__setattr__(col, '_seq' , aux_path.name)
        tar.add(aux_path, arcname=aux_path.name)
        aux_path.unlink()
    # The datamatrix can now be safely pickled
    dm_path = path.parent / Path(f'.{id(dm)}-{os.getpid()}.datamatrix')
    logger.debug('writing datamatrix pickle to {}'.format(dm_path))
    writepickle(dm, dm_path)
    tar.add(dm_path, arcname=dm_path.name)
    tar.close()
    dm_path.unlink()
    # The _seq and _fd properties can be restored again
    for col in dm._cols.values():
        if not isinstance(col, _MultiDimensionalColumn) or col.loaded:
            continue
        col._fd, col._seq = tmp[id(col)]
