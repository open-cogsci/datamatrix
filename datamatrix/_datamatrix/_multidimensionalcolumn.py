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
import logging
import weakref
from datamatrix import cfg
from datamatrix._datamatrix._mixedcolumn import MixedColumn
from datamatrix._datamatrix._numericcolumn import NumericColumn, FloatColumn, \
    IntColumn
from datamatrix._datamatrix._datamatrix import DataMatrix
from collections.abc import Sequence, Collection
from collections import OrderedDict
try:
    import numpy as np
    from numpy import nanmean, nanmedian, nanstd
except ImportError:
    np = None
try:
    Ellipsis
except NameError:
    Ellipsis = None  # was introduced in Python 3.10
try:
    import psutil
except ImportError:
    psutil = None
logger = logging.getLogger('datamatrix')

        
        
class _MultiDimensionalColumn(NumericColumn):

    """
    desc:
        A column in which each cell is a float array.
    """

    dtype = float
    printoptions = dict(precision=4, threshold=4, edgeitems=2)

    def __init__(self, datamatrix, shape, defaultnan=True, **kwargs):

        """
        desc:
            Constructor. You generally don't call this constructor correctly,
            but use the MultiDimensional helper function.

        arguments:
            datamatrix:
                desc: The DataMatrix to which this column belongs.
                type: DataMatrix
            shape:
                desc: A tuple that specifies the number and size of the
                      dimensions of each cell. Values can be integers, or 
                      tuples of non-integer values that specify names of
                      indices, e.g. `shape=(('x', 'y'), 10)). Importantly,
                      the length of the column (the number of rows) is
                      implicitly used as the first dimension. That, if you
                      specify a two-dimensional shape, then the resulting
                      column has three dimensions.
                type: int
                
        keywords:
            defaultnan:
                desc: Indicates whether the column should be initialized with
                      `nan` values (`True`) or 0s (`False`).
                type: bool
                
        keyword-dict:
            kwargs:
                keywords that are passed on to the parent constructor.
        """

        if np is None:
            raise Exception(
                'NumPy and SciPy are required, but not installed.')
        self._orig_shape = shape
        normshape = tuple()
        if isinstance(shape, (int, str)):
            shape = (shape, )
        self.index_names = []
        self.index_values = []
        for dim_size in shape:
            # Dimension without named indices
            if isinstance(dim_size, int):
                normshape += (dim_size, )
                self.index_names.append(list(range(dim_size)))
                self.index_values.append(list(range(dim_size)))
            elif isinstance(dim_size, Collection):
                if isinstance(dim_size, str):
                    raise ValueError('A dimension cannot be a string')
                normshape += (len(dim_size), )
                self.index_names.append(list(dim_size))
                self.index_values.append(list(range(len(dim_size))))
        self._shape = normshape
        self.defaultnan = defaultnan
        self._fd = None
        self._loaded = kwargs.get('loaded', None)
        NumericColumn.__init__(self, datamatrix, **kwargs)
        
    def __del__(self):
        """Clean up weak references on destruction."""
        touch_history.remove(self)

    def setallrows(self, value):

        """
        desc:
            Sets all rows to a value, or array of values.

        arguments:
            value:	A value, or array of values that has the same length as the
                    shape of the column.
        """

        value = self._checktype(value)
        self._seq[:] = value

    @property
    def unique(self):

        raise NotImplementedError(
            'unique is not implemented for {}'.format(self.__class__.__name__))

    @property
    def shape(self):

        """
        name: shape

        desc:
            A property to access and change the shape of the column. The shape
            includes the length of the column (the number of rows) as the first
            dimension.
        """

        return (len(self), ) + self._shape
    
    @property
    def depth(self):
        
        """
        name: depth

        desc:
            A property to access and change the depth of the column. The depth
            is the second dimension of the column, where the length of the
            column (the number of rows) is the first dimension.
        """
        
        return self._shape[0]

    @depth.setter
    def depth(self, depth):
        if depth == self.depth:
            return
        if len(self._shape) > 2:
            raise TypeError('Can only change the depth of two-dimensional '
                            'MultiDimensionalColumns/ SeriesColumns')
        logger.debug('changing depth from {} to {}'.format(self.depth, depth))
        self._orig_shape = (depth, )
        if depth > self.depth:
            seq = np.zeros((len(self), depth), dtype=self.dtype)
            if self.defaultnan:
                seq[:] = np.nan
            seq[:, :self.depth] = self._seq
            # If the depth is changed, we need to take this into account by 
            # setting the current shape based on the target shape
            self._shape = seq.shape[1:]            
            self._seq = seq
            self._shape = (depth, )
            return
        self._shape = (depth, )
        self._seq = self._seq[:, :depth]

    @property
    def plottable(self):

        """
        name: plottable

        desc:
            Gives a view of the traces where the axes have been swapped. This 
            is the format that matplotlib.pyplot.plot() expects.
        """

        return np.swapaxes(self._seq, 0, -1)

    @property
    def mean(self):

        return nanmean(self._seq, axis=0)

    @property
    def median(self):

        return nanmedian(self._seq, axis=0)

    @property
    def std(self):

        return nanstd(self._seq, axis=0, ddof=1)

    @property
    def max(self):

        return np.nanmax(self._seq, axis=0)

    @property
    def min(self):

        return np.nanmin(self._seq, axis=0)

    @property
    def sum(self):

        return np.nansum(self._seq, axis=0)
        
    @property
    def loaded(self):
        if self._loaded is None:
            self._loaded = self._sufficient_free_memory()
        return self._loaded
    
    @loaded.setter
    def loaded(self, val):
        if val == self._loaded:
            return
        logger.debug('{} column {}'.format('loading' if val else 'unloading',
                                           id(self)))
        self._loaded = val
        # Simply assigning self._seq will trigger a conversion to/ from
        # np.memmap based on the self._loaded
        self._seq = self._seq

    # Private functions
    
    def _memory_size(self):
        """Returns the size of the column in bytes if it were loaded into
        memory.
        """
        size = np.empty(1, dtype=self.dtype).nbytes
        for dim_size in self.shape:
            if isinstance(dim_size, Sequence):
                dim_size = len(dim_size)
            size *= dim_size
        return size
    
    def _sufficient_free_memory(self):
        """Returns whether there is sufficient free memory for the current
        column to be loaded into memory based on the MIN_MEM_FREE_ABS and
        MIN_MEM_FREE_REL constants.
        """
        if psutil is None:
            logger.debug('psutil is not installed. Cannot check available memory.')
            return True
        memory_size = self._memory_size()
        if memory_size < cfg.always_load_max_size:
            return True
        if memory_size > cfg.never_load_min_size:
            return False
        vm = psutil.virtual_memory()
        mem_free_abs =  vm.available - memory_size
        mem_free_rel = mem_free_abs / vm.total
        logger.debug('{} MB {:.1f}% will be available after loading column'
                     .format(mem_free_abs // 1024 ** 2, 100 * mem_free_rel))
        return mem_free_abs > cfg.min_mem_free_abs or \
            mem_free_rel > cfg.min_mem_free_rel

    def _init_seq(self):
        touch_history.touch(self)
        if self.loaded:
            # Close previous memmap object
            if self._fd is not None and not self._fd.closed:
                self._fd.close()
                self._fd = None
            logger.debug('initializing loaded column {}'.format(id(self)))
            if self.defaultnan:
                self._seq = np.empty(self.shape, dtype=self.dtype)
                self._seq[:] = np.nan
            else:
                self._seq = np.zeros(self.shape, dtype=self.dtype)
            return
        # Use memory-mapped array
        import tempfile
        logger.debug('initializing unloaded column {}'.format(id(self)))
        memory_size = self._memory_size()
        if memory_size >= psutil.virtual_memory().total:
            logger.warning('the size of this column exceeds system memory. '
                           'The column will be created, but operations that '
                           'require data to be loaded into memory will fail.')
        self._fd = tempfile.TemporaryFile(dir=cfg.tmp_dir, prefix='.',
                                          suffix='.memmap')
        self._seq = np.memmap(self._fd, shape=self.shape, dtype=self.dtype)
        chunk_slice = int(cfg.save_chunk_size / memory_size * len(self))
        self._seq[:] = np.nan if self.defaultnan else 0

    def __setattr__(self, key, val):
        """Catches assignments to the _seq attribute, which may need to be
        converted to memmap or a regular array depending on the loaded status.
        """
        if key != '_seq' or (isinstance(val, np.memmap) and not self.loaded) \
                or (not isinstance(val, np.memmap) and self.loaded):
            super().__setattr__(key, val)
            return
        # Convert to memory-mapped array
        self._init_seq()
        self._seq[:] = val

    def _printable_list(self):
        with np.printoptions(**self.printoptions):
            return [str(cell) for cell in self]

    def _operate(self, other, number_op, str_op=None, flip=False):

        touch_history.touch(self, try_to_load=True)
        # For a 1D array with the length of the datamatrix, we create an array
        # in which the second dimension (i.e. the shape) is constant. This
        # allows us to do by-row operations.
        if isinstance(other, (list, tuple)):
            other = np.array(other, dtype=self.dtype)
        if isinstance(other, NumericColumn):
            other = np.array(other._seq)
        if isinstance(other, np.ndarray) and other.shape == (len(self), ):
            a2 = np.empty(self.shape, dtype=self.dtype)
            np.swapaxes(a2, 0, -1)[:] = other
            other = a2
        rowid = self._rowid.copy()
        seq = number_op(other, self._seq) if flip else number_op(self._seq,
                                                                 other)
        return self._empty_col(rowid=rowid, seq=seq)

    def _map(self, fnc):

        # For a MultiDimensionalColumn, we need to make a special case, because
        # the shape of the new MultiDimensionalColumn may be different from
        # the shape of the original column. The new column may even be a 
        # different kind of column altogether.
        for i, cell in enumerate(self):
            a = fnc(cell)
            if not i:
                if isinstance(a, float):
                    newcol = FloatColumn(self.dm)
                elif isinstance(a, int):
                    newcol = IntColumn(self.dm)
                elif isinstance(a, str):
                    newcol = MixedColumn(self.dm)
                else:
                    newcol = self.__class__(self.dm, shape=len(a))
            newcol[i] = a
        return newcol

    def _checktype(self, value):

        try:
            a = np.empty(self.shape[1:], dtype=self.dtype)
            a[:] = value
        except:
            raise Exception('Invalid type: %s' % str(value))
        return a

    def _compare(self, other, op):

        raise NotImplementedError('Cannot compare {}s'.format(
            self.__class__.__name__))

    def _tosequence(self, value, length=None):
        
        full_shape = (length, ) + self.shape[1:]
        # For float and integers, we simply create a new (length, shape) array
        # with only this value
        if isinstance(value, (float, int)):
            a = np.empty(full_shape, dtype=self.dtype)
            a[:] = value
            return a
        try:
            a = np.array(value, dtype=self.dtype)
        except:
            raise TypeError('Cannot convert to sequence: %s' % str(value))
        # For a 1D array with the length of the datamatrix, we create an array
        # in which the second dimension (i.e. the shape) is constant.
        if a.shape == (length, ):
            a2 = np.empty(full_shape, dtype=self.dtype)
            np.swapaxes(a2, 0, -1)[:] = a
            return a2
        # For a 2D array that already has the correct dimensions, we return it.
        if a.shape == full_shape:
            return a
        # Set all rows at once
        if a.shape == self.shape[1:]:
            return a
        raise TypeError('Cannot convert to sequence: %s' % str(value))

    def _empty_col(self, datamatrix=None, **kwargs):

        return self.__class__(datamatrix if datamatrix else self._datamatrix,
                              shape=self._orig_shape,
                              defaultnan=self.defaultnan, **kwargs)

    def _addrowid(self, _rowid):

        old_length = len(self)
        self._rowid = np.concatenate((self._rowid, _rowid.asarray))
        a = np.zeros((len(self._rowid), ) + self.shape[1:], dtype=self.dtype)
        a[:old_length] = self._seq
        self._seq = a

    def _getintkey(self, key):

        return self._seq[key]

    # Implemented syntax

    def __getitem__(self, key):
        touch_history.touch(self, try_to_load=True)
        if isinstance(key, (tuple, list)) and len(key) <= len(self._seq.shape):
            # Advanced indexing always returns a copy, rather than a view, so
            # there's no need to explicitly copy the result.
            indices = self._numindices(key, accept_ellipsis=True)
            if indices is None:
                return
            value = self._seq[indices]
            # Averaging axes allows the slice to be reduced as part of the
            # slice. dm.s[:, ...] wil average axis 1, wheras dm.s[...] will
            # average axis 0.
            averaging_axes = self._averaging_axes(key)
            if averaging_axes:
                logger.debug('averaging over axes {}'.format(averaging_axes))
                value = np.nanmean(value, axis=averaging_axes)
            # If the index refers to exactly one value, then we return this
            # value as a float.
            if len(key) == len(self._seq.shape) and all(
                    self._single_index(index) for index in key):
                return float(value.squeeze())
            # If the index refers to exactly one row, then we return the cell
            # as an array
            if self._single_index(key[0]):
                return value[0]
            # Otherwise we create a new MultiDimensionalColumn. The shape is
            # squeezed such that all dimensions of size 1 are removed, except
            # the first dimension (in case there is a single row).
            squeeze_dims = tuple(dim + 1
                                 for dim, size in enumerate(value.shape[1:])
                                 if size == 1)
            if squeeze_dims:
                logger.debug('squeezing dimensions {}'.format(squeeze_dims))
                value = value.squeeze(axis=squeeze_dims)
            # If we're averaging across the first dimension, then we cannot
            # create column from the result because it changes the rows. In
            # this case we return an array.
            if 0 in averaging_axes:
                return value
            # If only one dimension remains, we return a FloatColumn, otherwise
            # a MultiDimensionalColumn, SeriesColumn, SurfaceColumn, or
            # VolumeColumn. However, we don't do this if any of the dimensions
            # was specified as a slice or ellipsis, because in that case it's
            # a coincidence.
            row_indices = indices[0].flatten()
            if len(value.shape) == 1 and not any(
                    isinstance(index, slice) for index in key[1:]):
                col = FloatColumn(self._datamatrix,
                                  rowid=self._rowid[row_indices],
                                  seq=value)
            else:
                # This captures the edge case in which a slice happened to
                # result in a one-dimensional column. In this case, we expand
                # it back to two dimensions.
                if len(value.shape) == 1:
                    value = value.reshape(value.shape[0], 1)
                if len(value.shape) == 2:
                    from datamatrix._datamatrix._seriescolumn import \
                        _SeriesColumn
                    cls = _SeriesColumn
                else:
                    cls = _MultiDimensionalColumn
                col = cls(self._datamatrix, shape=value.shape[1:],
                          rowid=self._rowid[row_indices],
                          seq=value)
            return col
        return super().__getitem__(key)

    def __setitem__(self, key, value):
        touch_history.touch(self, try_to_load=True)
        if not isinstance(key, tuple):
            key = (key, )
            key_was_tuple = False
        else:
            key_was_tuple = True
        indices = self._numindices(key)
        if indices is None:
            return
        # When assigning, the shape of the indexed array (target) and the
        # to-be-assigned value either need to match, or the shape of the
        # value needs to match the end of the shape of the target.
        if isinstance(value, (Sequence, np.ndarray)):
            if not isinstance(value, np.ndarray):
                value = np.array(value)
            target_shape = self._seq[indices].shape
            # This is an edge case that is preserved for backwards
            # compatibility: for a 2D column, and only if a single key is
            # provided (not a tuple), then values that match the length of the
            # datamatrix are used to set all values in each row to a constant
            # value, like so:
            #
            # dm = DataMatrix(length=2)
            # dm.col = SeriesColumn(depth=2)
            # dm.col = 1, 2
            # print(dm)
            # +---+---------+
            #| # |   col   |
            #+---+---------+
            #| 0 | [1. 1.] |
            #| 1 | [2. 2.] |
            if len(self.shape) == 2 and value.shape == (target_shape[0], ) \
                    and not key_was_tuple:
                np.rot90(self._seq)[:] = value
                return
            elif target_shape[-len(value.shape):] != value.shape:
                value = value.reshape(target_shape)
        self._seq[indices] = value
        self._datamatrix._mutate()
        
    def __getstate__(self):
        # When pickling the column, we need to load the column into memory.
        # However, when this is done in the context of writebin(), we actually
        # should load to memory, because the contents are written to disk and
        # replaced by a path that points towards this file.
        if self._fd is not None:
            logger.warning('loading column into memory for pickling. Use '
                           'io.writebin() and io.readbin() for reading and '
                           'writing columns that don\'t fit in memory.')
            self.loaded = True
        return super().__getstate__()

    def _single_index(self, index):
        return not isinstance(index, (slice, Sequence, np.ndarray)) and not \
            index == Ellipsis
        
    def _named_index(self, name, dim):
        try:
            return self.index_names[dim - 1].index(name)
        except ValueError as e:
            raise ValueError('{} is not an index name'.format(name))
            
    def _averaging_axes(self, indices):
        """Returns the axes that should be averaged when getting a slice, as
        specified by Ellipsis (...).
        """
        return tuple(dim for dim, index in enumerate(indices)
                     if Ellipsis is not None and index == Ellipsis)
        
    def _numindices(self, indices, accept_ellipsis=False):
        """Takes a tuple of indices, which can be either named or numeric,
        and converts it to a tuple of numeric indices that can be used to
        slice the array.
        """
        # Indices can be specified as slices, integers, names, and sequences of
        # integers and/ or names. These are all normalized to numpy arrays of
        # indices. The result is a tuple of arrays, where each array indexes
        # one dimension.
        numindices = tuple()
        for dim, index in enumerate(indices):
            if isinstance(index, slice):
                index = np.arange(*index.indices(self._seq.shape[dim]))
            elif accept_ellipsis and Ellipsis is not None and \
                    index == Ellipsis:
                index = np.arange(self._seq.shape[dim])
            elif isinstance(index, int):
                index = np.array([index])
            elif isinstance(index, np.ndarray):
                pass
            elif isinstance(index, DataMatrix):
                if index != self._datamatrix:
                    raise ValueError('Cannot slice column with a different DataMatrix')
                index = np.searchsorted(self._rowid, index._rowid)
            elif isinstance(index, Sequence) and not isinstance(index, str):
                index = np.array([
                    name if isinstance(name, int)
                    else self._named_index(name, dim)
                    for name in index])
            else:
                index = np.array([self._named_index(index, dim)])
            if 0 in index.shape:
                return None
            numindices += (index, )
        # By default, NumPy interprets tuples of indexes in a zip-like way, so
        # that a[(0, 2), (1, 3)] indexes two cells a[0, 1] and a[2, 3]. We want
        # tuples to be interpreted such that they refer to rows 0 and 2 and
        # columns 1 and 3. This is done with np.ix_().
        return np.ix_(*numindices)


def MultiDimensionalColumn(shape, defaultnan=True, **kwargs):
    
    return _MultiDimensionalColumn, dict(shape=shape, defaultnan=defaultnan,
                                         **kwargs)


class TouchHistory:
    """Keeps track of which columns have been used least recently and
    dynamically unloads these to free up memory if necessary.
    """
    def __init__(self):
        self._history = OrderedDict()
        self.suspended = False
    
    def touch(self, col, try_to_load=False):
        if self.suspended:
            return
        # Make sure the current column is add the end of the history
        id_ = id(col)
        if id_ in self._history:
            self._history.move_to_end(id_)
        else:
            self._history[id_] = weakref.ref(col)
        # If the current column is loaded, then we return right away, because
        # there is no need to free up additional memory by unloading other
        # columns
        if col._sufficient_free_memory():
            if try_to_load:
                col.loaded = True
            return
        # Otherwise we suspend the touch mechanism and loop through all other
        # columns, starting with the least-recently touched ones.
        self.suspended = True
        to_remove = []
        for other_id, other_col in self._history.items():
            # If the column doesn't exist anymore, then it's likely a pending
            # reference, and we remove it. This shouldn't happen though.
            other_col = other_col()
            if other_col is None:
                to_remove.append(other_id)
                continue
            # If the other column is not loaded or if it's the current column,
            # then we ignore it. We also ignore columns that are below a
            # certain size, because these should always be loaded.
            if other_col is col or not other_col.loaded or \
                    other_col._memory_size() < cfg.always_load_max_size:
                continue
            # Otherwise we unload the other column to free up memoty
            logger.debug('insufficient free memory')
            other_col.loaded = False
            # If there is now sufficient free memory to load the current column
            # then we do that if try_to_load is specified.
            if col._sufficient_free_memory():
                if try_to_load:
                    logger.debug(
                        'loading previously unloaded column {}'.format(id_))
                    col.loaded = True
                break
        for other_id in to_remove:
            self._history.pop(other_id)
        self.suspended = False

    def remove(self, col):
        id_ = id(self)
        if id_ in self._history:
            self._history.pop(id_)


# Singleton instance
touch_history = TouchHistory()
