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

---
desc: |
	A set of functions and decorators for functional programming.
---
"""

import inspect
import functools
import sys
import os
import pickle
import hashlib
from datamatrix.py3compat import *
from datamatrix import DataMatrix
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._index import Index


MEMOIZE_FOLDER = u'.memoize'


def memoize(fnc=None, key=None, persistent=False, lazy=False, debug=False):
	
	"""
	desc: |
		A memoization decorator that stores the result of a function call, and
		returns the stored value when the function is called again with the same
		arguments. That is, memoization is a specific kind of caching that
		improves performance for expensive function calls.
		
		This decorator only works for arguments and return values
		that can be serialized (i.e. arguments that you can pickle).
		
		To clear memoization, either pass `~[function name]` as a command line
		argument to a script, or pass `memoclear=True` as a keyword to the
		memoized function (not to the decorator).
		
		For a more detailed description, see:
		
		- %link:memoization%
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import functional as fnc

		 @fnc.memoize
		 def add(a, b):
		 	
		 	print('add(%d, %d)' % (a, b))
		 	return a + b
		 	
		 three = add(1, 2) # Storing result in memory
		 three = add(1, 2) # Re-using previous result
		 three = add(1, 2, memoclear=True) # Clear cache!
		 
		 @fnc.memoize(persistent=True, key='persistent-add')
		 def persistent_add(a, b):
		 	
		 	print('persistent_add(%d, %d)' % (a, b))
		 	return a + b
		 	
		 three = persistent_add(1, 2) # Writing result to disk
		 three = persistent_add(1, 2) # Re-using previous result	
		--%
		
	keywords:
		fnc:
			desc:	A function to memoize.
			type:	callable	
		persistent:
			desc:	Indicates whether the result should be written to disk so
					that the result can be re-used when the script is run again.
					If set to `True`, the result is stored as a pickle in a
					`.memoize` subfolder of the working directory.
			type:	bool
		key:
			desc:	Indicates a key that identifies the results. If no key is
					provided, a key is generated based on the function name,
					and the arguments passed to the function. However, this
					requires the arguments to be serialized, which can take some
					time.
			type:	[str, None]
		lazy:
			desc:	If `True`, any callable that is passed onto the memoized
					function is automatically called, and the memoized function
					receives the return value instead of the function object.
					This allows for lazy evaluation.
			type:	bool
		debug:
			desc:	If `True`, the memoized function returns a
					`(retval, memkey, source)` tuple, where `retval` is the
					function's return value, `memkey` is the key used for
					caching, and `source` is one of 'memory', 'disk', or
					'function', indicating whether and how the return value was
					cached. This is mostly for debugging and testing.
			type:	bool

	returns:
		desc:	A memoized version of fnc.
		type:	callable
	"""
	
	def inner(fnc):
			
		@functools.wraps(fnc)
		def innermost(*args, **kwdict):

			clear = kwdict.pop('memoclear') if 'memoclear' in kwdict \
				else '~%s' % fnc.__name__ in sys.argv
			memkey = _memkey(fnc, *args, **kwdict) if key is None else key
			# If persistent, determine the path for the memoization file and
			# create a folder if necessary
			if persistent:
				path = os.path.join(MEMOIZE_FOLDER, memkey)
				if not os.path.exists(MEMOIZE_FOLDER):
					os.mkdir(MEMOIZE_FOLDER)
			# Clear the cache both in memory and, if persistent, on disk.
			if clear:
				if memkey in cache:
					del cache[memkey]
				if persistent and os.path.exists(path):
					os.remove(path)
			if memkey in cache:
				return ret_fnc(cache[memkey], memkey, u'memory')
			# If ther result hasn't been cached yet, check if it's on disk,
			# otherwise determine it.
			if persistent:
				found, obj = _read_persistent_cache(path)
				if found:
					cache[memkey] = obj
					return ret_fnc(obj, memkey, u'disk')
			if lazy:
				args = [arg() if callable(arg) else arg for arg in args]
				kwdict = {key : val() if callable(val) else val for key, val in kwdict.items()}
			cache[memkey] = fnc(*args, **kwdict)
			if persistent:
				_write_persistent_cache(path, cache[memkey])
			return ret_fnc(cache[memkey], memkey, u'function')

		return innermost

	cache = {}
	ret_fnc = (lambda *args: args) if debug else (lambda *args: args[0])
	return inner if fnc is None else inner(fnc)


def curry(fnc):
	
	"""
	desc: |
		A [currying](https://en.wikipedia.org/wiki/Currying) decorator that
		turns a function with multiple arguments into a chain of partial
		functions, each of which takes at least a single argument. The input
		function may accept keywords, but the output function no longer does
		(i.e. currying turns all keywords into positional arguments).			
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import functional as fnc

		 @fnc.curry
		 def add(a, b, c):
		 	
		 	return a + b + c
		 	
		 print(add(1)(2)(3)) # Curried approach with single arguments
		 print(add(1, 2)(3)) # Partly curried approach
		 print(add(1)(2, 3)) # Partly curried approach
		 print(add(1, 2, 3)) # Original approach multiple arguments
		--%
		
	arguments:
		fnc:
			desc:	A function to curry.
			type:	callable

	returns:
		desc:	A curried function that accepts at least the first argument, and
				returns a function that accepts the second argument, etc.
		type:	callable
	"""
	
	def inner(*args):
		
		if _count_unbound_arguments(fnc) == len(args):
			return fnc(*args)
		return curry(functools.partial(fnc, *args))
		
	if py3:
		return functools.wraps(fnc)(inner)
	return inner


def map_(fnc, obj):
	
	"""
	desc: |
		Maps a function (`fnc`) onto rows of datamatrix or cells of a column.
	
		If `obj` is a column, the function `fnc` is mapped is mapped onto each
		cell of the column, and a new column is returned. In this case,
		`fnc` should be a function that accepts and returns a single value.
		
		If `obj` is a datamatrix, the function `fnc` is mapped onto each row,
		and a new datamatrix is returned. In this case, `fnc` should be a
		function that accepts a keyword `dict`, where column names are keys and
		cells are values. The return value should be another `dict`, again with
		column names as keys, and cells as values. Columns that are not part of
		the returned `dict` are left unchanged.
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import DataMatrix, functional as fnc
		 
		 dm = DataMatrix(length=3)
		 dm.old = 0, 1, 2
		 # Map a 2x function onto dm.old to create dm.new
		 dm.new = fnc.map_(lambda i: i*2, dm.old)
		 print(dm)
		 # Map a 2x function onto the entire dm to create dm_new, using a fancy
		 # dict comprehension wrapped inside a lambda function.
		 dm_new = fnc.map_(
		 	lambda **d: {col : 2*val for col, val in d.items()},
			dm)
		 print(dm_new)
		--%
		
	arguments:
		fnc:
			desc:	A function to map onto each row or each cell.
			type:	callable
		obj:
			desc:	A datamatrix or column to map `fnc` onto.
			type:	[BaseColumn, DataMatrix]

	returns:
		desc:	A new column or datamatrix.
		type:	[BaseColumn, DataMatrix]
	"""
	
	if not callable(fnc):
		raise TypeError('fnc should be callable')
	if isinstance(obj, _SeriesColumn):
		# For a SeriesColumn, we need to make a special case, because the depth
		# of the new SeriesColumn may be different from the depth of the
		# original column.
		for i, cell in enumerate(obj):	
			a = fnc(cell)
			if not i:
				newcol = _SeriesColumn(obj.dm, depth=len(a))
			newcol[i] = a
		return newcol		
	if isinstance(obj, BaseColumn):
		newcol = obj._empty_col()
		newcol[:] = [fnc(cell) for cell in obj]
		return newcol
	if isinstance(obj, DataMatrix):
		dm = obj[:]
		for row in dm:
			d = {col : val for col, val in row}
			d.update(fnc(**d))
			for col, val in d.items():
				row[col] = val
		return dm
	raise TypeError(u'obj should be DataMatrix or BaseColumn')
	
	
def filter_(fnc, obj):
	
	"""
	desc: |
		Filters rows from a datamatrix or column based on filter function
		(`fnc`).
		
		If `obj` is a column, `fnc` should be a function that accepts a single
		value. If `obj` is a datamatrix, `fnc` should be a function that accepts
		a keyword `dict`, where column names are keys and cells are values. In
		both cases, `fnc` should return a `bool` indicating whether the row or
		value should be included.
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import DataMatrix, functional as fnc
		 
		 dm = DataMatrix(length=5)
		 dm.col = range(5)
		 # Create a column with only odd values
		 col_new = fnc.filter_(lambda x: x % 2, dm.col)
		 print(col_new)
		 # Create a new datamatrix with only odd values in col
		 dm_new = fnc.filter_(lambda **d: d['col'] % 2, dm)
		 print(dm_new)
		--%
		
	arguments:
		fnc:
			desc:	A filter function.
			type:	callable
		obj:
			desc:	A datamatrix or column to filter.
			type:	[BaseColumn, DataMatrix]

	returns:
		desc:	A new column or datamatrix.
		type:	[BaseColumn, DataMatrix]		
	"""
	
	if not callable(fnc):
		raise TypeError('fnc should be callable')	
	if isinstance(obj, DataMatrix):
		dm = obj
		keep = lambda fnc, row: fnc(**{col : val for col, val in row})
	elif isinstance(obj, BaseColumn):
		dm = obj.dm
		keep = lambda fnc, row: fnc(row)
	else:
		raise TypeError(u'obj should be DataMatrix or BaseColumn')
	dm = dm._selectrowid(Index(
		[rowid for rowid, row in zip(dm._rowid, obj) if keep(fnc, row)]))
	if isinstance(obj, DataMatrix):
		return dm
	return dm[obj.name]


def setcol(dm, name, value):
	
	"""
	desc: |
		Returns a new DataMatrix to which a column has been added or in which
		a column has been modified.
		
		The main difference with regular assignment (`dm.col = 'x'`) is that
		`setcol()` does not modify the original DataMatrix, and can be used in
		`lambda` expressions.
		
		__Example:__
		
		%--
		python: |
		 from datamatrix import DataMatrix, functional as fnc

		 dm1 = DataMatrix(length=5)
		 dm2 = fnc.setcol(dm1, 'y', range(5))
		 print(dm2)
		--%
		
	arguments:
		dm:
			desc:	A DataMatrix.
			type:	DataMatrix
		name:
			desc:	A column name.
			type:	str
		value:
			desc:	The value to be assigned to the column. This can be any
					value this is valid for a regular column assignment.

	returns:
		desc:	A new DataMatrix.
		type:	DataMatrix
	"""	
	
	if not isinstance(name, basestring):
		raise TypeError('name should be a string')
	newdm = dm[:]
	if isinstance(value, BaseColumn):
		if value._datamatrix is not dm:
			raise Exception('This column does not belong to this DataMatrix')
		value._datamatrix = newdm
	newdm[name] = value
	return newdm


# Private functions


def _count_unbound_arguments(fnc):
	
	"""
	visible: False
	
	desc:
		Counts how many unbound arguments fnc takes. This is a wrapper function
		that works around the quirk that partialed functions are not real
		functions in Python 2.
	"""

	nbound = 0
	# In Python 2, functools.partial doesn't return a real function object, so
	# we need to dig to arrive at the actual funcion while remembering how many
	# arguments were bound.
	while isinstance(fnc, functools.partial):
		nbound += len(fnc.args)
		fnc = fnc.func
	return len(inspect.getargspec(fnc).args) - nbound


def _memkey(fnc, *args, **kwdict):
	
	"""
	visible: False
	
	desc:
		Generates a unique hash to serve as key for memoization.
	"""
	
	args = [ (arg.__name__ if hasattr(arg, '__name') else '__nameless__') \
		if callable(arg) else arg for arg in args]
	return hashlib.md5(pickle.dumps([fnc.__name__, args, kwdict])).hexdigest()


def _read_persistent_cache(path):
	
	if not os.path.exists(path):
		return False, None
	with open(path, u'rb') as fd:
		return True, pickle.load(fd)

		
def _write_persistent_cache(path, obj):
	
	with open(path, u'wb') as fd:
		pickle.dump(obj, fd)
