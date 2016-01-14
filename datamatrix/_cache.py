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

		iscached = True
		if 'cacheid' in kwargs:
			if not cache_initialized:
				init_cache()
			cachepath = os.path.join(cachefolder, kwargs['cacheid']) + '.pkl'
			del kwargs['cacheid']
		else:
			cachepath = None
		if skipcache or cachepath == None or not os.path.exists(cachepath):
			print('@cached: calling %s' % func)
			a = func(*args, **kwargs)
			if cachepath != None:
				print('@cached: saving %s' % cachepath)
				with open(cachepath, u'wb') as fd:
					pickle.dump(a, fd, protocol)
		else:
			ctime = time.ctime(os.path.getctime(cachepath))
			print('@cached: loading %s (created %s)' % (cachepath, ctime))
			with open(cachepath, u'rb') as fd:
				a = pickle.load(fd)
		return a

	return inner

def iscached(func):

	"""
	desc:
		Checks whether a function is cachable.

	returns:
		desc:	True if cachable, False otherwise.
		type:	false
	"""

	return 'iscached' in func.func_code.co_varnames
