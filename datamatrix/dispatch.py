#-*- coding:utf-8 -*-

"""
This file is part of exparser.

exparser is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

exparser is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with exparser.  If not, see <http://www.gnu.org/licenses/>.
"""

import sys
from datamatrix.py3compat import *
from datamatrix import DataMatrix, _cache
import time


def dispatch(dm, modules=[], full=[], cache_prefix='auto_cache.'):

	"""
	desc:
		Executes an analysis loop, in which all functions that specified on the
		command are executed. A function is executed if its name is prefixed by
		`@` and if it is present in one of the helpers modules. Cachable
		functions are cached automatically. If a function returns a DataMatrix,
		this is used to replace the current DataMatrix for the following functions.

	arguments:
		dm:		The DataMatrix to analyze.

	keywords:
		modules:	A module or list of modules that contain the analysis
					functions.
		full:		A list of functions or function names that make up the full
					analysis pathway.
		cache_prefix:
					A prefix for the cacheid for cachable functions. The
					function name will be appended.
	"""

	if not isinstance(modules, list):
		modules = [modules]
	if not modules:
		raise Exception('No modules specified')
	print('Dispatching ...')
	t0 = time.time()
	if '@full' in sys.argv:
		print('Running full analysis pathway')
		if not full:
			raise Exception('No full analysis pathway specified')
		for func in full:
			dm = _callfunc(dm, modules, func, cache_prefix=cache_prefix)
	else:
		for func in sys.argv:
			if not func[0] == '@':
				continue
			if ':redo' in func:
				func = func.replace(':redo', '')
				redo = True
			else:
				redo = False
			dm = _callfunc(dm, modules, func, cache_prefix=cache_prefix, redo=redo)
	print('Dispatch finished (%.2f s)' % (time.time() - t0))

def waterfall(*pipeline):

	"""
	desc:
		Implements a "cached waterfall", which is a series of cachable
		operations which is executed from the last point onward that is not
		cached.

	argument-list:
		pipeline:	A list of (func, cacheid, kwdict) tuples. Here, func is a
					cachable function, cacheid specifies the cacheid, and
					kwdict is dictionary of keyword arguments to passed to func.
					Each function except the first should take a DataMatrix as
					the first argument. All functions should return a
					DataMatrix.

	returns:
		type:	DataMatrix
	"""

	print('Starting waterfall ...')
	t0 = time.time()
	todo = []
	dm = None
	for i, (func, cacheid, kwdict) in enumerate(pipeline[::-1]):
		hascachefile, cachepath = _cache.cachefile(cacheid)
		if not hascachefile:
			todo.append( (func, cacheid, kwdict))
			continue
		print(u'-> Latest cache is %s' % func.__name__)
		dm = _cache.readcache(cachepath)
		break
	for func, cacheid, kwdict in todo[::-1]:
		if dm is None:
			print(u'-> Running (entry point) %s' % func.__name__)
			dm = func(cacheid=cacheid, **kwdict)
		else:
			print(u'-> Running %s' % func.__name__)
			dm = func(dm, cacheid=cacheid, **kwdict)
	print('Waterfall finished (%.2f s)' % (time.time() - t0))
	return dm


# Private functions


def _callfunc(dm, modules, func, cache_prefix='auto_cache.', redo=False):

	"""
	desc:
		Calls a single function from a module.

	arguments:
		dm:		The DataMatrix to analyze.
		modules:	list of modules that may contain the function.
		func:	The function name.

	keywords:
		cache_prefix:	A prefix for the cacheid for cachable functions. The
						function name will be appended.
		redo:			Indicates whether functions should be redone, even if a
						cache is available.

	returns:
		DataMatrix
	"""

	if func[0] == '@':
		func = func[1:]
	found = False
	for mod in modules:
		if hasattr(mod, func):
			t1 = time.time()
			if isinstance(func, basestring):
				_func = getattr(mod, func)
			else:
				_func = func
			if not redo and _cache.iscached(_func):
				cacheid = cache_prefix + func
				print('-> Calling %s.%s() [cacheid=%s]' \
					% (mod.__name__, func, cacheid))
				retval = _func(dm, cacheid=cacheid)
			else:
				print('-> Calling %s.%s() [uncached]' % (mod.__name__,
					func))
				retval = _func(dm)
			if isinstance(retval, DataMatrix):
				print('-> DataMatrix was modified')
				dm = retval
			print('-> Finished %s.%s() in %.2f s' % (mod.__name__, func,
				time.time()-t1))
			found = True
			break # Break in case the same function occurs in multiple modules
	if not found:
		warn(u'Helper function %s does not exist' % func)
	return dm
