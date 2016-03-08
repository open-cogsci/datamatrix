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
import pickle
import os


def readpickle(path):

	"""
	desc:
		Reads a DataMatrix from a pickle file.

	arguments:
		path:	The path to the pickle file.

	returns:
		A DataMatrix.
	"""

	with open(path, 'rb') as picklefile:
		return pickle.load(picklefile)


def writepickle(dm, path, protocol=-1):

	"""
	desc:
		Writes a DataMatrix to a pickle file.

	arguments:
		dm:		The DataMatrix to write.
		path:	The path to the pickle file.

	keywords:
		protocol:	The pickle protocol.
	"""

	try:
		os.makedirs(os.path.dirname(path))
	except:
		pass
	with open(path, 'wb') as picklefile:
		pickle.dump(dm, picklefile, protocol)
