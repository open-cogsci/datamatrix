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

from datamatrix import utils
from datamatrix import DataMatrix, MixedColumn
import os
import csv
import collections


# Byte-order marks should be silently stripped
BOM = u'\ufeff'


def readtxt(path, delimiter=',', quotechar='"', default_col_type=MixedColumn):

    """
    desc: |
        Reads a DataMatrix from a csv file.

        __Example:__

        ~~~ .python
        dm = io.readtxt('data.csv')
        ~~~

        *Version note:* As of 0.10.7, byte-order marks (BOMs) are silently
        stripped from column names.

    arguments:
        path: The path to the pickle file.

    keywords:
        delimiter:          The delimiter characer.
        quotechar:          The quote character.
        default_col_type:   The default column type.

    returns:
        A DataMatrix.
    """

    d = collections.OrderedDict()
    with open(path, 'r', encoding='utf-8') as csvfile:
        reader = csv.reader(
            csvfile,
            delimiter=delimiter,
            quotechar=quotechar
        )
        # Register columns while silently stripping BOMs
        for column in next(reader):
            column = utils.safe_decode(column)
            if column.startswith(BOM):
                column = column[1:]
            d[column] = []
        for row in reader:
            all_columns = list(d.keys())
            for column, val in zip(d.keys(), row):
                all_columns.remove(column)
                d[column].append(val)
            for column in all_columns:
                utils.logger.warning(u'Some rows miss column %s' % column)
                d[column].append(u'')
    dm = DataMatrix(default_col_type=default_col_type)._fromdict(d)
    return dm


def writetxt(dm, path, delimiter=',', quotechar='"'):

    """
    desc: |
        Writes a DataMatrix to a csv file.

        __Example:__

        ~~~ .python
        io.writetxt(dm, 'data.csv')
        ~~~

    arguments:
        dm:     The DataMatrix to write.
        path:   The path to the pickle file.

    keywords:
        delimiter: The delimiter characer.
        quotechar: The quote character.
    """

    if not dm.is_2d:
        raise TypeError('Can only write 2D DataMatrix objects to csv')
    try:
        os.makedirs(os.path.dirname(path))
    except:
        pass
    with open(path, 'w', encoding='utf-8') as csvfile:
        writer = csv.writer(
            csvfile,
            delimiter=delimiter,
            quotechar=quotechar,
            lineterminator='\n'
        )
        writer.writerow([utils.safe_decode(colname) for colname in dm.columns])
        for row in dm:
            writer.writerow([utils.safe_decode(value) for colname, value in row])
