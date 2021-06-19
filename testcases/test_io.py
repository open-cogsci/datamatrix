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

import pytest
from datamatrix import DataMatrix, io
from testcases.test_tools import check_dm


def test_io():

    refdm = DataMatrix(length=3)
    refdm[u'tést'] = 1, 2, u''
    refdm.B = u'mathôt', u'b', u'x'
    refdm.C = u'a,\\b"\'c', 8, u''

    testdm = io.readtxt('testcases/data/data.csv')
    check_dm(refdm, testdm)
    io.writetxt(testdm, 'tmp.csv')
    testdm = io.readtxt('tmp.csv')
    check_dm(refdm, testdm)

    refdm = io.readtxt('testcases/data/line-ending-cr.csv')
    check_dm(refdm, testdm)
    refdm = io.readtxt('testcases/data/line-ending-crlf.csv')
    check_dm(refdm, testdm)
    refdm = io.readtxt('testcases/data/data-with-bom.csv')
    check_dm(refdm, testdm)

    io.writepickle(testdm, 'tmp.pickle')
    testdm = io.readpickle('tmp.pickle')
    check_dm(refdm, testdm)

    io.writexlsx(testdm, 'tmp.xlsx')
    with pytest.warns(UserWarning):  # Not all rows have column C
        testdm = io.readxlsx('tmp.xlsx')
    check_dm(refdm, testdm)
    io.writexlsx(testdm, 'tmp.xlsx')
    with pytest.warns(UserWarning):  # Not all rows have column C
        testdm = io.readxlsx('tmp.xlsx')
    check_dm(refdm, testdm)
