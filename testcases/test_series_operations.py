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
from datamatrix import DataMatrix, SeriesColumn
from datamatrix import series
from testcases.test_tools import check_col, check_series, check_integrity
from nose.tools import eq_, ok_
import numpy as np


def test_endlock():

	dm = DataMatrix(length=4)
	dm.series = SeriesColumn(depth=3)
	dm.series[0] = 1, 2, 3
	dm.series[1] = 1, np.nan, 3
	dm.series[2] = 1, 2, np.nan
	dm.series[3] = np.nan, 2, np.nan
	dm.series = series.endlock(dm.series)
	check_series(dm.series, [
		[1,2,3],
		[1,np.nan,3],
		[np.nan,1,2],
		[np.nan,np.nan,2],
		])


def test_reduce_():

	dm = DataMatrix(length=2)
	dm.series = SeriesColumn(depth=3)
	dm.series[0] = 1, 2, 3
	dm.series[1] = 2, 3, 4
	dm.col = series.reduce_(dm.series)
	check_col(dm.col, [2,3])
	check_integrity(dm)


def test_window():

	dm = DataMatrix(length=2)
	dm.series = SeriesColumn(depth=4)
	dm.series[0] = 0,1,1,0
	dm.series[1] = 0,2,2,0
	dm.window = series.window(dm.series, 1, 3)
	check_series(dm.window, [[1,1], [2,2]])
	check_integrity(dm)


def test_baseline():

	dm = DataMatrix(length=2)
	dm.series = SeriesColumn(depth=3)
	dm.series[0] = range(3)
	dm.series[1] = range(1,4)
	dm.baseline = SeriesColumn(depth=3)
	dm.baseline[0] = range(1,4)
	dm.baseline[1] = range(3)
	dm.norm = series.baseline(dm.series, dm.baseline)
	check_series(dm.norm, [[0,.5,1], [1,2,3]])
	check_integrity(dm)
