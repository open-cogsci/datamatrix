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
from datamatrix import DataMatrix
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
try:
    import numpy as np
except ImportError:
    np = None


MAX_ROWS = 100
MAX_COLS = 20


def to_html(obj):

    """
    desc:
        Generates an HTML representation of a DataMatrix or column.

    arguments:
        obj:
            type:   [DataMatrix, BaseColumn]

    returns:
        type:   str
    """

    if isinstance(obj, DataMatrix):
        return _datamatrix_to_html(obj)
    if isinstance(obj, _SeriesColumn):
        return _seriescolumn_to_html(obj)
    if isinstance(obj, BaseColumn):
        return _basecolumn_to_html(obj)
    raise TypeError('Cannot represent object as HTML')


def _basecolumn_to_html(col):

    html = [
        u'<table><tr><th colspan=%d>%s</th></tr>' % (
            min(MAX_COLS, len(col)),
            col.name
        )
    ]
    for i in range(0, len(col), MAX_COLS):
        html.append(
            u'<tr>'
            + u''.join([
                u'<td>' + safe_decode(cell) + u'</td>'
                for cell in col[i:i + MAX_COLS]
            ])
            + u'</tr>'
        )
    html.append(u'</table>')
    return u''.join(html)


def _seriescolumn_to_html(series):

    html = [
        u'<table><tr><th colspan=%d>%s(%d)</th></tr>' % (
            min(MAX_COLS, series.depth),
            series.name,
            series.depth
        )
    ]
    for i, cell in zip(range(MAX_ROWS), series):
        html.append(
            u'<tr>'
            + u''.join([
                (
                    u'<td>…</td>'
                    if i == MAX_COLS - 1 and series.depth > MAX_COLS
                    else u'<td>' + safe_decode(val) + u'</td>'
                )
                for i, val in zip(range(MAX_COLS), cell)
            ])
            + u'</tr>'
        )
    html.append(u'</table>')
    if len(series) > MAX_ROWS:
        html.insert(
            0,
            u'Showing %d of %d rows <br />' % (MAX_ROWS, len(series))
        )
    return u''.join(html)


def _datamatrix_to_html(dm):

    html = [(
        u'<table><tr>'
        + u''.join([
            u'<th>'
            + (
                u'%s(%d)' % (name, col.depth)
                if isinstance(col, _SeriesColumn)
                else name
            )
            + '</th>'
            for name, col in dm.columns[:MAX_COLS]
        ])
        + u'</tr>'
    )]
    for row in dm[:MAX_ROWS]:
        html.append(
            u'<tr>'
            + u''.join([
                u'<td>'
                + (
                    u'%s ... %s' % (str(cell[:2])[:-1], str(cell[-2:])[1:])
                    if np is not None and isinstance(cell, np.ndarray)
                    else safe_decode(cell)
                )
                + u'</td>'
                for i, (name, cell) in zip(range(MAX_COLS), row)
            ])
            + u'</tr>'
        )
    html.append(u'</table>')
    if len(dm) > MAX_ROWS:
        html.insert(0, u'Showing %d of %d rows <br />' % (MAX_ROWS, len(dm)))
    if len(dm.columns) > MAX_COLS:
        html.insert(
            0,
            u'Showing %d of %d columns <br />' % (MAX_COLS, len(dm.columns))
        )
    return u''.join(html)
