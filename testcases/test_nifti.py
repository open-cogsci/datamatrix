# coding=utf-8

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
from datamatrix import DataMatrix, NiftiColumn
import nibabel as nib
import numpy as np


def test_nifti():

	dm = DataMatrix(length=2)
	dm.n = NiftiColumn
	dm.n[0] = nib.Nifti2Image(
		np.array([[[0, 0], [1, 1]], [[-1, -1], [1, 1]]]),
		None
	)
	dm.n[1] = nib.Nifti2Image(
		np.array([[[1, 1], [0, 0]], [[np.nan, 1], [0, 0]]]),
		None
	)
	m = dm.n.mean.get_data()
	assert np.all(m == np.array([[[.5, .5], [.5, .5]], [[-1, 0], [.5, .5]]]))


test_nifti()
