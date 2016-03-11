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
try:
	import pandas as pd
except ImportError:
	pd = None


def wrap_pandas(fnc):

	"""
	visible: False

	desc:
		A decorator for pandas functions. It converts a DataMatrix to a
		DataFrame, passes it to a function, and then converts the returned
		DataFrame back to a DataMatrix.
	"""

	def inner(dm, *arglist, **kwdict):

		df_in = to_pandas(dm)
		df_out = fnc(df_in, *arglist, **kwdict)
		return from_pandas(df_out)

	inner.__doc__ = u'desc: A simple wrapper around the corresponding pandas function'
	return inner


def to_pandas(dm):

	"""
	desc:
		Converts a DataMatrix to a pandas DataFrame.

	arguments:
		dm:
			type:	DataMatrix

	returns:
		type:	DataFrame
	"""

	d = {}
	for colname, col in dm.columns:
		d[colname] = list(col)
	return pd.DataFrame(d)


def from_pandas(df):

	"""
	desc:
		Converts a pandas DataFrame to a DataMatrix.

	arguments:
		dm:
			type:	DataFrame

	returns:
		type:	DataMatrix
	"""

	from datamatrix import operations as ops

	dm = DataMatrix(length=len(df))
	for colname in df.columns:
		if isinstance(colname, tuple):
			_colname = u'_'.join([str(i) for i in colname])
		else:
			_colname = colname
		try:
			exec('%s = None' % _colname)
		except SyntaxError:
			dm[u'_%s' % _colname] = df[colname]
		else:
			dm[_colname] = df[colname]
	ops.auto_type(dm)
	return dm
