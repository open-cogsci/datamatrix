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
import os
from pathlib import Path
logger = logging.getLogger('datamatrix')


class Config:
    """A central config object with sensible defaults. Values can also be
    specified in a tool.datamatrix entry in pyprojec.toml.
    """
    min_mem_free_rel = .5
    min_mem_free_abs = 4294967296
    always_load_max_size = 134217728
    never_load_min_size = float('inf')
    save_chunk_size = 134217728
    tmp_dir = os.getcwd()
    
    def __init__(self):
        logger.debug('initializing config')
        pyproject_toml = Path('pyproject.toml')
        if not pyproject_toml.exists():
            return
        try:
            import tomlkit
        except ImportError:
            logger.warning(
                'tomlkit not available. Cannot read pyproject.toml.')
            return
        logger.debug('reading pyproject.toml')
        toml = tomlkit.parse(pyproject_toml.read_text())
        if 'tool' not in toml or \
                'datamatrix' not in toml['tool']:
            logger.debug('no tool.datamatrix entry in pyproject.toml')
            return
        for key, value in toml['tool']['datamatrix'].items():
            logger.debug('{} = {}'.format(key, value))
            setattr(self, key, value)


# singleton instance
cfg = Config()
