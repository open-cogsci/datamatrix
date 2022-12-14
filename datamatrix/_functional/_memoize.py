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
from datamatrix import DataMatrix, convert as cnv, io
from functools import partial
import tarfile
import sys
import os
import logging
import warnings
try:
    from collections.abc import Sequence  # Python 3.3 and later
except ImportError:
    from collections import Sequence
from collections import OrderedDict
import hashlib
import pickle
try:
    import numpy as np
except ImportError:
    np = None
logger = logging.getLogger('datamatrix')


ONE_GIGABYTE = 1024**3


class memoize(object):

    """
    desc: |
        *Requires json_tricks*

        A memoization decorator that stores the result of a function call, and
        returns the stored value when the function is called again with the
        same arguments. That is, memoization is a specific kind of caching that
        improves performance for expensive function calls.

        This decorator only works for return values that can be pickled, and
        arguments that can be serialized to `json`.

        The memoized function becomes a callable object. To clear the
        memoization cache, call the `.clear()` function on the memoized
        function. The total size of all cached return values is available as 
        the `.cache_size` property.


        For a more detailed description, see:

        - %link:memoization%

        *Changed in v0.8.0*: You can no longer pass the `memoclear` keyword to
        the memoized function. Use the `.clear()` function instead.

        __Example:__

        %--
        python: |
         from datamatrix import functional as fnc

         @fnc.memoize
         def add(a, b):

            print('add(%d, %d)' % (a, b))
            return a + b

         three = add(1, 2)  # Storing result in memory
         three = add(1, 2)  # Re-using previous result
         add.clear()  # Clear cache, but only for the next call
         three = add(1, 2)  # Calculate again

         @fnc.memoize(persistent=True, key='persistent-add')
         def persistent_add(a, b):

            print('persistent_add(%d, %d)' % (a, b))
            return a + b

         three = persistent_add(1, 2)  # Writing result to disk
         three = persistent_add(1, 2)  # Re-using previous result
        --%

    keywords:
        fnc:
            desc:   A function to memoize.
            type:   callable
        persistent:
            desc:   Indicates whether the result should be written to disk so
                    that the result can be re-used when the script is run 
                    again. If set to `True`, the result is stored as a pickle 
                    in a `.memoize` subfolder of the working directory.
            type:   bool
        key:
            desc:   Indicates a key that identifies the results. If no key is
                    provided, a key is generated based on the function name,
                    and the arguments passed to the function. However, this
                    requires the arguments to be serialized, which can take 
                    some time.
            type:   [str, None]
        lazy:
            desc:   If `True`, any callable that is passed onto the memoized
                    function is automatically called, and the memoized function
                    receives the return value instead of the function object.
                    This allows for lazy evaluation.
            type:   bool
        debug:
            desc:   If `True`, the memoized function returns a
                    `(retval, memkey, source)` tuple, where `retval` is the
                    function's return value, `memkey` is the key used for
                    caching, and `source` is one of 'memory', 'disk', or
                    'function', indicating whether and how the return value was
                    cached. This is mostly for debugging and testing.
            type:   bool
        max_size:
            desc:   The maximum total size (in bytes) of all cached return
                    values. If the cache exceeds this size, the oldest cached
                    return value is dropped.
            type:   int

    returns:
        desc:   A memoized version of fnc.
        type:   callable
    """

    folder = u'.memoize'

    def __init__(
        self, fnc=None, key=None, persistent=False, lazy=False, debug=False,
        folder=None, max_size=ONE_GIGABYTE
    ):

        self._fnc = fnc
        self._key = key
        self._persistent = persistent
        self._lazy = lazy
        self._debug = debug
        self._max_size = max_size
        self._ignore_cache_once = False
        self._folder = self.folder if folder is None else folder
        self._init_cache()
        self.__name__ = (
            'memoize(nofnc)' if fnc is None
            else 'memoize(%s)' % fnc.__name__
        )

    def clear(self):

        self._ignore_cache_once = True

    @property
    def cache_size(self):

        return sum(sys.getsizeof(obj) for obj in self._cache.values())

    @property
    def __call__(self):

        return (
            self._call_with_arguments
            if self._fnc is None
            else self._call_without_arguments
        )

    def __rshift__(self, other):

        if not self._lazy:
            raise ValueError(
                'You can only use the >> operator with lazy memoization'
            )
        return partial(other, self)

    def __rrshift__(self, other):

        if not self._lazy:
            raise ValueError(
                'You can only use the >> operator with lazy memoization'
            )
        return partial(self, other)

    def _call_with_arguments(self, fnc):

        return self.__class__(
            fnc=fnc,
            key=self._key,
            persistent=self._persistent,
            lazy=self._lazy,
            debug=self._debug,
            folder=self._folder,
            max_size=self._max_size
        )

    def _call_without_arguments(self, *args, **kwargs):

        memkey = (
            self._memkey(*args, **kwargs)
            if self._key is None else self._key
        )
        is_cached, retval = self._read_cache(memkey)
        if is_cached:
            if self._debug:
                print(
                    '%s: returning cached result for memkey %s'
                    % (self.__name__, memkey)
                )
            return (
                (retval, memkey, self._latest_source)
                if self._debug
                else retval
            )
        if self._lazy:
            args = self._lazy_evaluation_args(args)
            kwargs = self._lazy_evaluation_kwargs(kwargs)
        if self._debug:
            print(
                '%s: executing for memkey %s'
                % (self.__name__, memkey)
            )
        return self._write_cache(
            memkey,
            self._fnc(*args, **kwargs)
        )

    def _lazy_evaluation_obj(self, obj):

        if callable(obj):
            return obj()
        if isinstance(obj, dict):
            return self._lazy_evaluation_kwargs(obj)
        if (
            isinstance(obj, Sequence)
            and not isinstance(obj, basestring)
        ):
            return self._lazy_evaluation_args(obj)
        return obj

    def _lazy_evaluation_args(self, args):

        return [self._lazy_evaluation_obj(arg) for arg in args]

    def _lazy_evaluation_kwargs(self, kwargs):

        return {
            key: self._lazy_evaluation_obj(val)
            for key, val in kwargs.items()
        }

    def _init_cache(self):

        self._cache = OrderedDict()
        if self._persistent and not os.path.exists(self._folder):
            os.mkdir(self._folder)

    def _uncompress_cache(self, cachepath):

        tarxzpath = cachepath + u'.tar.xz'
        if os.path.exists(cachepath) or not os.path.exists(tarxzpath):
            return
        with tarfile.open(tarxzpath) as fd:
            fd.extractall(os.path.dirname(tarxzpath))

    def _read_cache(self, memkey):

        cache_path = os.path.join(self._folder, memkey)
        if self._ignore_cache_once:
            self._latest_source = 'function'
            self._ignore_cache_once = False
            if memkey in self._cache:
                del self._cache[memkey]
            if os.path.exists(cache_path):
                os.remove(cache_path)
            return False, None
        if self._persistent:
            self._uncompress_cache(cache_path)
            if os.path.exists(cache_path):
                self._latest_source = 'disk'
                try:
                    with open(cache_path, u'rb') as fd:
                        obj = pickle.load(fd)
                    logger.debug('read pickle from memoization cache: {}'
                                 .format(cache_path))
                except pickle.UnpicklingError as e:
                    # DataMatrix objects are stored as binary files, because
                    # this allows memmaped columns to be included
                    obj = io.readbin(cache_path)
                    logger.debug(
                        'read binary datamatrix from memoization cache {}'
                        .format(cache_path))
                # Old-style datamatrix objects need to be upgraded so that
                # memoization keeps working for previously executed functions.
                if obj.__class__.__name__ == u'DataMatrix':
                    from datamatrix.io._pickle import _upgrade_datamatrix
                    obj = _upgrade_datamatrix(obj)
                return True, obj
        elif memkey in self._cache:
            self._latest_source = 'memory'
            return True, pickle.loads(self._cache[memkey])
        self._latest_source = 'function'
        return False, None

    def _write_cache(self, memkey, retval):

        if self._persistent:
            cache_path = os.path.join(self._folder, memkey)
            if not os.path.exists(cache_path):
                # DataMatrix objects are stored as binary files, because
                # this allows memmaped columns to be included.
                if isinstance(retval, DataMatrix):
                    io.writebin(retval, cache_path)
                    logger.debug(
                        'wrote binary datamatrix to memoization cache: {}'
                        .format(cache_path))
                else:
                    with open(cache_path, u'wb') as fd:
                        pickle.dump(retval, fd)
                    logger.debug('wrote pickle to memoization cache: {}'
                                 .format(cache_path))
        else:
            self._cache[memkey] = pickle.dumps(retval)
            while self.cache_size > self._max_size:
                if self._debug:
                    print('%s: dropping oldest cached value' % self.__name__)
                self._cache.popitem(last=False)
            if not self._cache:
                warnings.warn('Return value exceeds max_size')
        return (
            (retval, memkey, self._latest_source)
            if self._debug
            else retval
        )

    def _serialize_obj(self, obj):

        import json_tricks

        if callable(obj):
            return obj.__name__ if hasattr(obj, '__name__') else '__nameless__'
        if isinstance(obj, dict):
            return self._serialize_kwargs(obj)
        if (
            isinstance(obj, Sequence)
            and not isinstance(obj, basestring)
        ):
            return self._serialize_args(obj)
        if isinstance(obj, DataMatrix):
            return cnv.to_json(obj)
        if np is not None and isinstance(obj, np.ndarray):
            return str(obj.data.tobytes())
        try:
            return json_tricks.dumps(obj)
        except BaseException as e:
            pass
        try:
            return str(obj)
        except BaseException as e:
            pass
        if hasattr(obj, '__hash__') and callable(obj.__hash__):
            return obj.__hash__()
        raise ValueError('Cannot serialize arguments')

    def _serialize_args(self, args):

        return [self._serialize_obj(arg) for arg in args]

    def _serialize_kwargs(self, kwargs):

        return {key: self._serialize_obj(val) for key, val in kwargs.items()}

    def _memkey(self, *args, **kwargs):

        return hashlib.md5(
            pickle.dumps(
                [
                    self._fnc.__name__,
                    self._serialize_args(args),
                    self._serialize_kwargs(kwargs),
                ]
            )
        ).hexdigest()
