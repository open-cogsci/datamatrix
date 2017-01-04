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
import os
import sys
import time
import pickle
import shutil

cache_initialized = False
skipcache = '--no-cache' in sys.argv
cachefolder = '.cache'
protocol = pickle.HIGHEST_PROTOCOL

def init_cache():

	"""
	desc:
		Initializes the cache system.
	"""

	global cache_initialized
	if cache_initialized:
		return
	cache_initialized = True
	print(u'Initializing cache ...')
	if '--clear-cache' in sys.argv and os.path.exists(cachefolder):
		print(u'Removing cache folder (%s)' % cachefolder)
		shutil.rmtree(cachefolder)
	if not os.path.exists(cachefolder):
		print(u'Creating cache folder (%s)' % cachefolder)
		os.mkdir(cachefolder)


def cached(func):

	"""
	desc:
		A decorator function that provides a cache for functions that return
		a pickable value.
	"""

	def inner(*args, **kwargs):

		if 'cacheid' in kwargs:
			hascachefile, cachepath = cachefile(kwargs['cacheid'])
			del kwargs['cacheid']
		else:
			cachepath = None
		if skipcache or cachepath is None or not hascachefile:
			print('@cached: calling %s' % func)
			a = func(*args, **kwargs)
			if cachepath is not None:
				print('@cached: saving %s' % cachepath)
				writecache(a, cachepath)
		else:
			ctime = time.ctime(os.path.getctime(cachepath))
			print('@cached: loading %s (created %s)' % (cachepath, ctime))
			a = readcache(cachepath)
		return a

	init_cache()
	inner.__name__ = func.__name__
	return inner

def iscached(func):

	"""
	desc:
		Checks whether a function is cachable.

	returns:
		desc:	True if cachable, False otherwise.
		type:	false
	"""

	init_cache()
	if py3:
		return 'iscached' in func.__code__.co_varnames
	return 'iscached' in func.func_code.co_varnames

def cachefile(cacheid):

	"""
	desc:
		Gets the cachefile for a cacheid, and checks whether this file exists.

	arguments:
		cacheid:	The cacheid.

	returns:
		A (cache_exists, cachepath) tuple, where the first is a boolean that
		indicates if the second exists.
	"""

	init_cache()
	path = os.path.join(cachefolder, cacheid) + '.pkl'
	if os.path.exists(path):
		return True, path
	return False, path

def readcache(cachepath):

	"""
	desc:
		Reads an object from a cachefile.

	arguments:
		cachepath:	The full path to the cachefile.

	returns:
		An object that was cached.
	"""

	init_cache()
	with open(cachepath, u'rb') as fd:
		return pickle.load(fd)

def writecache(a, cachepath):

	"""
	desc:
		Writes a cachefile for an object.

	arguments:
		a:			The object to cache. This object should be pickleable.
		cachepath:	The full path to the cachefile.
	"""

	init_cache()
	with open(cachepath, u'wb') as fd:
		pickle.dump(a, fd, protocol)
