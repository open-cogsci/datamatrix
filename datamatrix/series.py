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
desc:
    A set of operations to apply to `SeriesColumn` objects. These operations
    can also be applied to `MultiDimensionalColumn` objects with two
    dimensions, but *not* to `MultiDimensionalColumn` objects with three or more
    dimensions.
---
"""

from datamatrix.py3compat import *
from datamatrix.multidimensional import nancount, infcount, flatten, reduce
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix._datamatrix._basecolumn import BaseColumn
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn
from datamatrix import FloatColumn, operations as ops, functional as fnc, \
    DataMatrix, NAN, INF
import numpy as np
from numpy import nanmean, nanmedian
from scipy.interpolate import interp1d


# Placeholders for imports that will occur in _butter()
butter = None
sosfilt = None


def roll(series, shift):
    """
    desc: |
        Rolls (or shifts) the elements along the depth of the series. Elements
        that run off the last position are re-introduced at the first position
        and vice versa.
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, SeriesColumn, series as srs
        
         dm = DataMatrix(length=3)
         dm.s = SeriesColumn(depth=4)
         dm.s = [[1, 2, 3, 4],
                 [10, 20, 30, 40],
                 [100, 200, 300, 400]]
         dm.t = srs.roll(dm.s, shift=1)
         dm.u = srs.roll(dm.s, shift=[1, 0, -1])
         print(dm)
        --%
        
    arguments:
        series:
            desc: The series column to roll
            type: SeriesColumn
        shift:
            desc: The number of places to roll by. If `shift` is an `int`, each
                  row is shifted by the same amount. If `shift` is a sequence,
                  which has to be of the same length as the series, then each
                  row is shifted by the amounted indicated by the corresponding
                  value in `shift`.
            type: [int, Sequence]
            
    returns:
        desc: The rolled series.
        type: SeriesColumn
    """
    series = series[:]
    if isinstance(shift, int):
        series._seq = np.roll(series._seq, shift, axis=1)
        return series
    if len(shift) != len(series):
        raise ValueError(
            'shift must be int or a sequence of the same length as the series')
    for i, s in enumerate(shift):
        if not isinstance(s, (int, float)):
            raise TypeError('shift values must be numeric')
        series._seq[i] = np.roll(series._seq[i], int(s))
    return series


def trim(series, value=NAN, start=False, end=True):
    """
    desc: |
        Trims trailing and/ or leading values from a series. This is useful,
        for example, to discard the end (or beginning) of a series that
        consists exclusively of invalid data, such as `NAN` or 0 values.
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, SeriesColumn, series as srs
         
         dm = DataMatrix(length=3)
         dm.s = SeriesColumn(depth=5)
         dm.s[0] = 0, 0, 2, 0, 0
         dm.s[1] = 0, 0, 0, 3, 0
         dm.s[2] = 0, 0, 2, 3, 0
         dm.trimmed = srs.trim(dm.s, value=0, start=True, end=True)
         print(dm)
        --%

    arguments:
        series:
            desc: The series column to trim
            type: SeriesColumn

    keywords:
        value:
            desc: The value to trim
            type: [int, float]
        start:
            desc: Indicates whether the start of the series should be trimmed
            type: bool
        end:
            desc: Indicates whether the end of the series should be trimmed
            type: bool
            
    returns:
        desc: A trimmed copy of the series column
        type: SeriesColumn
    """
    if start:
        start_index = int(
            first_occurrence(series, value=value, equal=False).min)
    else:
        start_index = 0
    if end:
        end_index = int(
            last_occurrence(series, value=value, equal=False).max + 1)
    else:
        end_index = series.depth
    return series[:, start_index:end_index]


def first_occurrence(series, value, equal=True):
    """
    desc: |
        Finds the first occurence of a value for each row of a series column
        and returns the result as a float column of sample indices.
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, SeriesColumn, NAN, series as srs
        
         dm = DataMatrix(length=3)
         dm.s = SeriesColumn(depth=3)
         dm.s[0] = 1, 2, 3
         dm.s[1] = 1, 2, NAN
         dm.s[2] = NAN, NAN, NAN
         dm.first_nan = srs.first_occurrence(dm.s, value=NAN)
         dm.first_non_1 = srs.first_occurrence(dm.s, value=1, equal=False)
         print(dm)
        --%
        
    arguments:
        series:
            desc: The series column to search
            type: SeriesColumn
        value:
            desc: |
                The value to find in the series column. If `value` is a
                sequence, which has to be of the same length as the series,
                then each row is searched for the value indicated by the
                corresponding value in `value`.
            type: [float, int, Sequence]
    
    keywords:
        equal:
            desc:
                If `True`, the index of the first matching sample is returned.
                If `False`, the index of the first non-matching sample is
                returned.
            type: bool
            
    returns:
        desc:
            A float column with sample indices or `NAN` for cells in which
            there was no match (or no mismatch if `equal=False`).
        type: FloatColumn
    """
    return _occurrence(series, value, equal=equal, reverse=True)
    
    
def last_occurrence(series, value, equal=True):
    """
    desc: |
        Finds the last occurence of a value for each row of a series column
        and returns the result as a float column of sample indices.
        
        *Version note:* New in 0.15.0
        
        __Example:__
        
        %--
        python: |
         from datamatrix import DataMatrix, SeriesColumn, NAN
        
         dm = DataMatrix(length=3)
         dm.s = SeriesColumn(depth=3)
         dm.s[0] = 1, 2, 3
         dm.s[1] = 1, 2, NAN
         dm.s[2] = NAN, NAN, NAN
         dm.last_nan = srs.last_occurrence(dm.s, value=NAN)
         dm.last_non_1 = srs.last_occurrence(dm.s, value=1, equal=False)
         print(dm)
        --%
        
    arguments:
        series:
            desc: The series column to search
            type: SeriesColumn
        value:
            desc: |
                The value to find in the series column. If `value` is a
                sequence, which has to be of the same length as the series,
                then each row is searched for the value indicated by the
                corresponding value in `value`.
            type: [float, int, Sequence]
    
    keywords:
        equal:
            desc:
                If `True`, the index of the last matching sample is returned.
                If `False`, the index of the last non-matching sample is
                returned.
            type: bool
            
    returns:
        desc:
            A float column with sample indices or `NAN` for cells in which
            there was no match (or no mismatch if `equal=False`).
        type: FloatColumn
    """    
    return _occurrence(series, value, equal=equal)


def concatenate(*series):

    """
    desc: |
        Concatenates multiple series such that a new series is created with a
        depth that is equal to the sum of the depths of all input series.

        __Example:__

        %--
        python: |
         from datamatrix import series as srs

         dm = DataMatrix(length=1)
         dm.s1 = SeriesColumn(depth=3)
         dm.s1[:] = 1,2,3
         dm.s2 = SeriesColumn(depth=3)
         dm.s2[:] = 3,2,1
         dm.s = srs.concatenate(dm.s1, dm.s2)
         print(dm.s)
        --%

    argument-list:
        series: A list of series.

    returns:
        desc:	A new series.
        type:	SeriesColumn
    """

    _validate_multiple_series(series)
    if not all(s.dm is series[0].dm for s in series):
        raise ValueError(
            u'columns don\'t belong to the same DataMatrix')
    newseries = _SeriesColumn(
        series[0]._datamatrix,
        depth=sum(s.depth for s in series)
    )
    i = 0
    for s in series:
        newseries[:, i:i+s.depth] = s
        i += s.depth
    return newseries


def endlock(series):

    """
    desc: |
        Locks a series to the end, so that any nan-values that were at the end
        are moved to the start.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 5 # Number of rows
         DEPTH = 10 # Depth (or length) of SeriesColumns

         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

         dm = DataMatrix(length=LENGTH)
         # First create five identical rows with a sinewave
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y.setallrows(sinewave)
         # Add a random offset to the Y values
         dm.y += np.random.random(LENGTH)
         # Set some observations at the end to nan
         for i, row in enumerate(dm):
            row.y[-i:] = np.nan
         # Lock the degraded traces to the end, so that all nans
         # now come at the start of the trace
         dm.y2 = srs.endlock(dm.y)

         plt.clf()
         plt.subplot(121)
         plt.title('Original (nans at end)')
         plt.plot(dm.y.plottable)
         plt.subplot(122)
         plt.title('Endlocked (nans at start)')
         plt.plot(dm.y2.plottable)
         plt.show()
        --%

    arguments:
        series:
            desc:	The signal to end-lock.
            type:	SeriesColumn

    returns:
        desc:	An end-locked signal.
        type:	SeriesColumn
    """
    _validate_series(series)
    endlock_series = _SeriesColumn(series._datamatrix, series.depth)
    endlock_series[:] = np.nan
    src = series._seq
    dst = endlock_series._seq
    for rownr, row in enumerate(src):
        if np.all(np.isnan(row)):
            continue
        nancols = np.where(np.isnan(row))[0]
        for nancol in nancols:
            if np.any(~np.isnan(row[nancol:])):
                continue
            dst[rownr, -nancol:] = row[:nancol]
            break
        else:
            dst[rownr] = row
    return endlock_series


def lock(series, lock):

    """
    desc: |
        Shifts each row from a series by a certain number of steps along its
        depth. This is useful to lock, or align, a series based on a sequence
        of values.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 5 # Number of rows
         DEPTH = 10 # Depth (or length) of SeriesColumns

         dm = DataMatrix(length=LENGTH)
         # First create five traces with a partial cosinewave. Each row is
         # offset slightly on the x and y axes
         dm.y = SeriesColumn(depth=DEPTH)
         dm.x_offset = -1
         dm.y_offset = -1
         for row in dm:
            row.x_offset = np.random.randint(0, DEPTH)
            row.y_offset = np.random.random()
            row.y = np.roll(
                np.cos(np.linspace(0, np.pi, DEPTH)),
                row.x_offset
            ) + row.y_offset
         # Now use the x offset to lock the traces to the 0 point of the
         # cosine, i.e. to their peaks.
         dm.y2, zero_point = srs.lock(dm.y, lock=dm.x_offset)

         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.y.plottable)
         plt.subplot(122)
         plt.title('Locked to peak')
         plt.plot(dm.y2.plottable)
         plt.axvline(zero_point, color='black', linestyle=':')
         plt.show()
        --%

    arguments:
        series:
            desc: The signal to lock.
            type: SeriesColumn
        lock:
            desc:   A sequence of lock values with the same length as the
                    Series. This can be a column, a list, a numpy array, etc.

    returns:
        desc:   A `(series, zero_point)` tuple, in which `series` is a
                `SeriesColumn` and `zero_point` is the zero point to which the
                signal has been locked.
    """
    _validate_series(series)
    if len(series) != len(lock):
        raise ValueError('lock and series should be the same length')
    try:
        zero_point = int(max(lock))
    except TypeError:
        raise TypeError('lock should be a sequence of integers')
    lpad = [int(zero_point - l) for l in lock]
    lock_series = _SeriesColumn(series.dm, series.depth + max(lpad))
    for lpad, lock_row, orig_row in zip(lpad, lock_series, series):
        lock_row[lpad:lpad+series.depth] = orig_row
    return lock_series, zero_point


def normalize_time(dataseries, timeseries):

    """
    desc: |
        *New in v0.7.0*

        Creates a new series in which a series of timestamps (`timeseries`) is
        used as the indices for a series of data point (`dataseries`). This is
        useful, for example, if you have a series of measurements and a
        separate series of timestamps, and you want to combine the two.

        The resulting series will generally contain a lot of `nan` values,
        which you can interpolate with `interpolate()`.

        __Example:__

        %--
        python: |
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs, NAN

         # Create a DataMatrix with one series column that contains samples
         # and one series column that contains timestamps.
         dm = DataMatrix(length=2)
         dm.samples = SeriesColumn(depth=3)
         dm.time = SeriesColumn(depth=3)
         dm.samples[0] = 3, 1, 2
         dm.time[0]    = 1, 2, 3
         dm.samples[1] = 1, 3, 2
         dm.time[1]    = 0, 5, 10
         # Create a normalized column with samples spread out according to
         # the timestamps, and also create an interpolate version of this
         # column for smooth plotting.
         dm.normalized = srs.normalize_time(
            dataseries=dm.samples,
            timeseries=dm.time
         )
         dm.interpolated = srs.interpolate(dm.normalized)
         # And plot!
         plt.clf()
         plt.plot(dm.normalized.plottable, 'o')
         plt.plot(dm.interpolated.plottable, ':')
         plt.xlabel('Time')
         plt.ylabel('Data')
         plt.show()
        --%

    arguments:
        dataseries:
            desc:   A column with datapoints.
            type:   SeriesColumn
        timeseries:
            desc:   A column with timestamps. This should be an increasing list
                    of the same depth as `dataseries`. NAN values are allowed,
                    but only at the end.
            type:   SeriesColumn

    returns:
        desc:   A new series in which the data points are spread according to
                the timestamps.
        type:   SeriesColumn
    """
    _validate_series(dataseries)
    _validate_series(timeseries)
    if dataseries.dm is not timeseries.dm:
        raise ValueError(
            'dataseries and timeseries should belong to the same DataMatrix'
        )
    if dataseries.depth != timeseries.depth:
        raise ValueError(
            'dataseries and timeseries should have the same depth'
        )
    if max(timeseries.max) < 0 or min(timeseries.min) < 0:
        raise ValueError('timeseries should contain only positive values')
    series = _SeriesColumn(dataseries.dm, depth=int(max(timeseries.max))+1)
    haystack = np.arange(series.depth, dtype=int)
    for row in range(series._seq.shape[0]):
        needle = timeseries._seq[row]
        values = dataseries._seq[row]
        while len(needle) and np.isnan(needle)[-1]:
            needle = needle[:-1]
            values = values[:-1]
        if np.any(np.isnan(needle)):
            raise ValueError(
                'timeseries should not contain NAN values, except at the end'
            )
        if not np.all(np.diff(needle) > 0):
            raise ValueError(
                'timeseries should contain increasing values '
                '(i.e. time should go forward)'
            )
        indices = np.searchsorted(haystack, needle)
        series._seq[row, indices] = values
    return series


def window(series, start=0, end=None):

    """
    desc: |
        Extracts a window from a signal.

        *Version note:* As of 0.9.4, the preferred way to get a window from a
        series is with a slice: `dm.s[:, start:end]`.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 5 # Number of rows
         DEPTH = 10 # Depth (or length) of SeriesColumns

         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

         dm = DataMatrix(length=LENGTH)
         # First create five identical rows with a sinewave
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y.setallrows(sinewave)
         # Add a random offset to the Y values
         dm.y += np.random.random(LENGTH)
         # Look only the middle half of the signal
         dm.y2 = srs.window(dm.y, start=DEPTH//4, end=-DEPTH//4)

         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.y.plottable)
         plt.subplot(122)
         plt.title('Window (middle half)')
         plt.plot(dm.y2.plottable)
         plt.show()
        --%

    arguments:
        series:
            desc: The signal to get a window from.
            type: SeriesColumn

    keywords:
        start:
            desc: The window start.
            type: int
        end:
            desc: The window end, or None to go to the signal end.
            type: [int, None]

    returns:
        desc: A window of the signal.
        type: SeriesColumn
    """

    if end is None:
        end = series.depth
    return series[:, start:end]


def baseline(
    series,
    baseline,
    bl_start=-100,
    bl_end=None,
    reduce_fnc=None,
    method='subtractive'
):

    """
    desc: |
        Applies a baseline to a signal

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 5 # Number of rows
         DEPTH = 10 # Depth (or length) of SeriesColumns

         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

         dm = DataMatrix(length=LENGTH)
         # First create five identical rows with a sinewave
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y.setallrows(sinewave)
         # Add a random offset to the Y values
         dm.y += np.random.random(LENGTH)
         # And also a bit of random jitter
         dm.y += .2*np.random.random( (LENGTH, DEPTH) )
         # Baseline-correct the traces, This will remove the vertical
         # offset
         dm.y2 = srs.baseline(dm.y, dm.y, bl_start=0, bl_end=10)

         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.y.plottable)
         plt.subplot(122)
         plt.title('Baseline corrected')
         plt.plot(dm.y2.plottable)
         plt.show()
        --%

    arguments:
        series:
            desc: The signal to apply a baseline to.
            type: SeriesColumn
        baseline:
            desc: The signal to use as a baseline to.
            type: SeriesColumn

    keywords:
        bl_start:
            desc: The start of the window from `baseline` to use.
            type: int
        bl_end:
            desc:   The end of the window from `baseline` to use, or None to go
                    to the end.
            type:   [int, None]
        reduce_fnc:
            desc:   The function to reduce the baseline epoch to a single
                    value. If None, np.nanmedian() is used.
            type:   [FunctionType, None]
        method:
            desc: |
                    Specifies whether divisive or subtractive baseline
                    correction should be used. (*Changed in v0.7.0: subtractive
                    is now the default*)
            type:   str

    returns:
        desc:	A baseline-correct version of the signal.
        type:	SeriesColumn
    """

    if reduce_fnc is None:
        reduce_fnc = nanmedian
    baseline = reduce(
        window(baseline, start=bl_start, end=bl_end),
        operation=reduce_fnc
    )
    if method == 'divisive':
        return series / baseline
    if method == 'subtractive':
        return series - baseline
    raise Exception('Baseline method should be divisive or subtractive')


def blinkreconstruct(series, vt=5, vt_start=10, vt_end=5, maxdur=500,
                     margin=10, smooth_winlen=21, std_thr=3, gap_margin=20,
                     gap_vt=10, mode='original'):
    """
    desc: |
        Reconstructs pupil size during blinks. This algorithm has been designed
        and tested largely with the EyeLink 1000 eye tracker.
        
        *Version note:* As of 0.13.0, an advanced algorithm has been
        introduced, wich can be specified through the `mode` keyword. The
        advanced algorithm is recommended for new analyses, and will be made
        the default in future releases.

        __Source:__

        - Mathot, S., & Vilotijević, A. (2022). Methods in cognitive 
          pupillometry: Design, preprocessing, and statitical analysis.
          *Behavior Research Methods*.
          <https://doi.org/10.3758/s13428-022-01957-7>

    arguments:
        series:
            desc: A signal to reconstruct.
            type: SeriesColumn

    keywords:
        vt:
            desc:   A pupil-velocity threshold for blink detection. Lower
                    tresholds more easily trigger blinks. This argument only
                    applies to 'original' mode.
            type:   [int, float]
        vt_start:
            desc:   A pupil-velocity threshold for detecting the onset of a
                    blink. Lower tresholds more easily trigger blinks. This
                    argument only applies to 'advanced' mode.
            type:   [int, float]
        vt_end:
            desc:   A pupil-velocity threshold for detecting the offset of a
                    blink. Lower tresholds more easily trigger blinks. This
                    argument only applies to 'advanced' mode.
            type:   [int, float]
        maxdur:
            desc:   The maximum duration (in samples) for a blink. Longer
                    blinks are not reconstructed.
            type:   int
        margin:
            desc:   The margin to take around missing data that is
                    reconstructed.
            type:   int
        smooth_winlen:
            desc:   The window length for a hanning window that is used to
                    smooth the velocity profile.
            type:   int
        std_thr:
            desc:   A standard-deviation threshold for when data should be
                    considered invalid.
            type:   [float, int]
        gap_margin:
            desc:   The margin to take around missing data that is not
                    reconstructed. Only applies to advanced mode.
            type: int
        gap_vt:
            desc:   A pupil-velocity threshold for detection of invalid data.
                    Lower tresholds mean more data marked as invalid. Only
                    applies to advanced mode.
            type:   [int, float]
        mode:
            desc:   The algorithm to be used for blink reconstruction. Should
                    be 'original' or 'advanced'. An advanced algorith was
                    introduced in v0.13., and should be used for new analysis.
                    The original algorithm is still the default for backwards
                    compatibility.
            type:   [str]

    returns:
        desc: A reconstructed singal.
        type: SeriesColumn
    """

    return _map(series, _blinkreconstruct, vt=vt, vt_start=vt_start,
                vt_end=vt_end, maxdur=maxdur, margin=margin,
                smooth_winlen=smooth_winlen, std_thr=std_thr, gap_vt=gap_vt,
                gap_margin=gap_margin, mode=mode)
    

def smooth(series, winlen=11, wintype='hanning'):

    """
    desc: |
        Smooths a signal using a window with requested size.

        This method is based on the convolution of a scaled window with the
        signal. The signal is prepared by introducing reflected copies of the
        signal (with the window size) in both ends so that transient parts are
        minimized in the begining and end part of the output signal.

        __Adapted from:__

        - <http://www.scipy.org/Cookbook/SignalSmooth>

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 5 # Number of rows
         DEPTH = 100 # Depth (or length) of SeriesColumns

         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

         dm = DataMatrix(length=LENGTH)
         # First create five identical rows with a sinewave
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y.setallrows(sinewave)
         # And add a bit of random jitter
         dm.y += np.random.random( (LENGTH, DEPTH) )
         # Smooth the traces to reduce the jitter
         dm.y2 = srs.smooth(dm.y)

         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.y.plottable)
         plt.subplot(122)
         plt.title('Smoothed')
         plt.plot(dm.y2.plottable)
         plt.show()
        --%

    arguments:
        series:
            desc: A signal to smooth.
            type: SeriesColumn

    keywords:
        winlen:
            desc:   The width of the smoothing window. This should be an odd
                    integer.
            type:   int
        wintype:
            desc:   The type of window from 'flat', 'hanning', 'hamming',
                    'bartlett', 'blackman'. A flat window produces a moving
                    average smoothing.
            type:   str

    returns:
        desc: A smoothed signal.
        type: SeriesColumn
    """

    return _map(series, _smooth, winlen=winlen, wintype=wintype)


def downsample(series, by, fnc=nanmean):

    """
    desc: |
        Downsamples a series by a factor, so that it becomes 'by' times
        shorter. The depth of the downsampled series is the highest multiple of
        the depth of the original series divided by 'by'. For example,
        downsampling a series with a depth of 10 by 3 results in a depth of 3.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 1 # Number of rows
         DEPTH = 100 # Depth (or length) of SeriesColumns

         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

         dm = DataMatrix(length=LENGTH)
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y.setallrows(sinewave)
         dm.y2 = srs.downsample(dm.y, by=10)

         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.y.plottable, 'o-')
         plt.subplot(122)
         plt.title('Downsampled')
         plt.plot(dm.y2.plottable, 'o-')
         plt.show()
        --%

    arguments:
        by:
            desc: The downsampling factor.
            type: int

    keywords:
        fnc:
            desc:   The function to average the samples that are combined
                    into 1 value. Typically an average or a median.
            type:   callable

    returns:
        desc: A downsampled series.
        type: SeriesColumn
    """

    return _map(series, _downsample, by=by, fnc=fnc)


def threshold(series, fnc, min_length=1):

    """
    desc: |
        Finds samples that satisfy some threshold criterion for a given period.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 1 # Number of rows
         DEPTH = 100 # Depth (or length) of SeriesColumns

         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

         dm = DataMatrix(length=LENGTH)
         # First create five identical rows with a sinewave
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y.setallrows(sinewave)
         # And also a bit of random jitter
         dm.y += np.random.random( (LENGTH, DEPTH) )
         # Threshold the signal by > 0 for at least 10 samples
         dm.t = srs.threshold(dm.y, fnc=lambda y: y > 0, min_length=10)

         plt.clf()
         # Mark the thresholded signal
         plt.fill_between(np.arange(DEPTH), dm.t[0], color='black', alpha=.25)
         plt.plot(dm.y.plottable)
         print(dm)
         plt.show()
        --%

    arguments:
        series:
            desc: A signal to threshold.
            type: SeriesColumn
        fnc:
            desc:   A function that takes a single value and returns True if
                    this value exceeds a threshold, and False otherwise.
            type:   FunctionType

    keywords:
        min_length:
            desc:   The minimum number of samples for which `fnc` must return
                    True.
            type:   int

    returns:
        desc:   A series where 0 indicates below threshold, and 1 indicates
                above threshold.
        type:   SeriesColumn
    """
    _validate_series(series)
    threshold_series = _SeriesColumn(series._datamatrix, series.depth)
    threshold_series[:] = 0
    # First walk through all rows
    for i, trace in enumerate(series):
        # Then walk through all samples within a row
        nhit = 0
        for j, val in enumerate(trace):
            hit = fnc(val)
            if hit:
                nhit += 1
                continue
            if nhit >= min_length:
                threshold_series[i, j-nhit:j] = 1
            nhit = 0
        if nhit >= min_length:
            threshold_series[i, j-nhit+1:j+1] = 1
    return threshold_series


def interpolate(series):

    """
    desc: |
        Linearly interpolates missing (`nan`) data.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 1 # Number of rows
         DEPTH = 100 # Depth (or length) of SeriesColumns
         MISSING = 50 # Nr of missing samples

         # Create a sine wave with missing data
         sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))
         sinewave[np.random.choice(np.arange(DEPTH), MISSING)] = np.nan
         # And turns this into a DataMatrix
         dm = DataMatrix(length=LENGTH)
         dm.y = SeriesColumn(depth=DEPTH)
         dm.y = sinewave
         # Now interpolate the missing data!
         dm.i = srs.interpolate(dm.y)

         # And plot the original data as circles and the interpolated data as
         # dotted lines
         plt.clf()
         plt.plot(dm.i.plottable, ':')
         plt.plot(dm.y.plottable, 'o')
         plt.show()
        --%

    arguments:
        series:
            desc: A signal to interpolate.
            type: SeriesColumn


    returns:
        desc: The interpolated signal.
        type: SeriesColumn
    """

    return _map(series, _interpolate)


def filter_bandpass(series, freq_range, order=2, sampling_freq=None):

    """
    desc: |
        *New in v0.9.2*
        
        *Changed in v0.11.0: added `sampling_freq` argument* 

        Applies a Butterworth bandpass-pass filter to the signal.

        For more information, see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html).

        __Example:__

        %--
        python: |
            import numpy as np
            from matplotlib import pyplot as plt
            from datamatrix import DataMatrix, SeriesColumn, series as srs
            
            LENGTH = 3
            DEPTH = 100
            SAMPLING_FREQ = 100
            
            # Create one fast oscillation, and two combined fast and slow
            # oscillations
            dm = DataMatrix(length=LENGTH)
            dm.s = SeriesColumn(depth=DEPTH)
            dm.s[0] = np.sin(np.linspace(0, 20 * np.pi, DEPTH))  # 10 Hz
            dm.s[1] = np.sin(np.linspace(0, 10 * np.pi, DEPTH)) + dm.s[0]  # 5 Hz
            dm.s[2] = np.cos(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]  # 1 Hz
            dm.f = srs.filter_bandpass(dm.s, freq_range=(4, 6), sampling_freq=SAMPLING_FREQ)
            
            # Plot the original signal
            plt.clf()
            plt.subplot(121)
            plt.title('Original')
            plt.plot(dm.s[0])
            plt.plot(dm.s[1])
            plt.plot(dm.s[2])
            plt.subplot(122)
            # And the filtered signal!
            plt.title('Bandpass')
            plt.plot(dm.f[0])
            plt.plot(dm.f[1])
            plt.plot(dm.f[2])
            plt.show()
        --%

    arguments:
        series:
            desc: A signal to filter.
            type: SeriesColumn
        freq_range:
            desc: A `(min_freq, max_freq)` tuple.
            type: tuple

    keywords:
        order:
            desc: The order of the filter.
            type: int
        sampling_freq:
            desc:   The sampling frequence of the signal, or `None` to use the
                    scipy default of 2 half-cycles per sample.
            type:   [int, None]

    returns:
        desc: The filtered signal.
        type: SeriesColumn
    """

    return _map(
        series,
        _butter,
        freq_range=freq_range,
        order=order,
        btype='bandpass',
        sampling_freq=sampling_freq
    )


def filter_highpass(series, freq_min, order=2, sampling_freq=None):

    """
    desc: |
        *New in v0.9.2*
        
        *Changed in v0.11.0: added `sampling_freq` argument* 

        Applies a Butterworth highpass-pass filter to the signal.

        For more information, see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html).

        __Example:__

        %--
        python: |
            import numpy as np
            from matplotlib import pyplot as plt
            from datamatrix import DataMatrix, SeriesColumn, series as srs
            
            LENGTH = 3
            DEPTH = 100
            SAMPLING_FREQ = 100
            
            # Create one fast oscillation, and two combined fast and slow
            # oscillations
            dm = DataMatrix(length=LENGTH)
            dm.s = SeriesColumn(depth=DEPTH)
            dm.s[0] = np.sin(np.linspace(0, 20 * np.pi, DEPTH))  # 10 Hz
            dm.s[1] = np.sin(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]  # 1 Hz
            dm.s[2] = np.cos(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]  # 1 Hz
            dm.f = srs.filter_highpass(dm.s, freq_min=3, sampling_freq=SAMPLING_FREQ)
            
            # Plot the original signal
            plt.clf()
            plt.subplot(121)
            plt.title('Original')
            plt.plot(dm.s[0])
            plt.plot(dm.s[1])
            plt.plot(dm.s[2])
            plt.subplot(122)
            # And the filtered signal!
            plt.title('Highpass')
            plt.plot(dm.f[0])
            plt.plot(dm.f[1])
            plt.plot(dm.f[2])
            plt.show()
        --%

    arguments:
        series:
            desc: A signal to filter.
            type: SeriesColumn
        freq_min:
            desc: The minimum filter frequency.
            type: int

    keywords:
        order:
            desc: The order of the filter.
            type: int
        sampling_freq:
            desc:   The sampling frequence of the signal, or `None` to use the
                    scipy default of 2 half-cycles per sample.
            type:   [int, None]

    returns:
        desc: The filtered signal.
        type: SeriesColumn
    """

    return _map(
        series,
        _butter,
        freq_range=freq_min,
        order=order,
        btype='highpass',
        sampling_freq=sampling_freq
    )


def filter_lowpass(series, freq_max, order=2, sampling_freq=None):

    """
    desc: |
        *New in v0.9.2*
        
        *Changed in v0.11.0: added `sampling_freq` argument* 

        Applies a Butterworth low-pass filter to the signal.

        For more information, see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html).

        __Example:__

        %--
        python: |
            import numpy as np
            from matplotlib import pyplot as plt
            from datamatrix import DataMatrix, SeriesColumn, series as srs
            
            LENGTH = 3
            DEPTH = 100
            SAMPLING_FREQ = 100
            
            # Create one fast oscillation, and two combined fast and slow
            # oscillations
            dm = DataMatrix(length=LENGTH)
            dm.s = SeriesColumn(depth=DEPTH)
            dm.s[0] = np.sin(np.linspace(0, 20 * np.pi, DEPTH))  # 10 Hz
            dm.s[1] = np.sin(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]  # 1 Hz
            dm.s[2] = np.cos(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]  # 1 Hz
            dm.f = srs.filter_lowpass(dm.s, freq_max=3, sampling_freq=SAMPLING_FREQ)
            
            # Plot the original signal
            plt.clf()
            plt.subplot(121)
            plt.title('Original')
            plt.plot(dm.s[0])
            plt.plot(dm.s[1])
            plt.plot(dm.s[2])
            plt.subplot(122)
            # And the filtered signal!
            plt.title('Lowpass')
            plt.plot(dm.f[0])
            plt.plot(dm.f[1])
            plt.plot(dm.f[2])
            plt.show()
        --%

    arguments:
        series:
            desc: A signal to filter.
            type: SeriesColumn
        freq_max:
            desc: The maximum filter frequency.
            type: int

    keywords:
        order:
            desc: The order of the filter.
            type: int
        sampling_freq:
            desc:   The sampling frequence of the signal, or `None` to use the
                    scipy default of 2 half-cycles per sample.
            type:   [int, None]

    returns:
        desc: The filtered signal.
        type: SeriesColumn
    """

    return _map(
        series,
        _butter,
        freq_range=freq_max,
        order=order,
        btype='lowpass',
        sampling_freq=sampling_freq
    )


def fft(series, truncate=True):

    """
    desc: |
        *New in v0.9.2*

        Performs a fast-fourrier transform (FFT) for the signal. For more
        information, see [`numpy.fft`](https://docs.scipy.org/doc/numpy/reference/routines.fft.html#module-numpy.fft).

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 3
         DEPTH = 200

         # Create one fast oscillation, and two combined fast and slow
         # oscillations
         dm = DataMatrix(length=LENGTH)
         dm.s = SeriesColumn(depth=DEPTH)
         dm.s[0] = np.sin(np.linspace(0, 150 * np.pi, DEPTH))
         dm.s[1] = np.sin(np.linspace(0, 75 * np.pi, DEPTH))
         dm.s[2] = np.sin(np.linspace(0, 10 * np.pi, DEPTH))
         dm.f = srs.fft(dm.s)

         # Plot the original signal
         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.s[0])
         plt.plot(dm.s[1])
         plt.plot(dm.s[2])
         plt.subplot(122)
         # And the filtered signal!
         plt.title('FFT')
         plt.plot(dm.f[0])
         plt.plot(dm.f[1])
         plt.plot(dm.f[2])
         plt.show()
        --%

    arguments:
        series:
            desc: A signal to determine the FFT for.
            type: SeriesColumn

    keywords:
        truncate:
            desc:   FFT series of real signals are symmetric. The `truncate`
                    keyword indicates whether the last (symmetric) part of the
                    FFT should be removed.
            type:   bool

    returns:
        desc: The FFT of the signal.
        type: SeriesColumn
    """
    _validate_series(series)
    newseries = _SeriesColumn(series._datamatrix, depth=series.depth)
    newseries[:] = np.fft.fft(series, axis=1)
    if truncate:
        newseries.depth = newseries.depth // 2
    return newseries


def z(series):

    """
    desc: |
        Applies a *z*-transform to the signal such that each trace has a mean
        value of 0 and a standard deviation of 1. That is, each trace is
        *z*-transformed individually.
        
        *Note:* If you want to *z*-transform a series column such that the mean
        of the full series is 0 with a standard deviation of 1, then use
        `operations.z()`.

        __Example:__

        %--
        python: |
         import numpy as np
         from matplotlib import pyplot as plt
         from datamatrix import DataMatrix, SeriesColumn, series as srs

         LENGTH = 3
         DEPTH = 200

         # Create one fast oscillation, and two combined fast and slow
         # oscillations
         dm = DataMatrix(length=LENGTH)
         dm.s = SeriesColumn(depth=DEPTH)
         dm.s[0] = 1 * np.sin(np.linspace(0, 4 * np.pi, DEPTH))
         dm.s[1] = 2 * np.sin(np.linspace(.4, 4.4 * np.pi, DEPTH))
         dm.s[2] = 3 * np.sin(np.linspace(.8, 4.8 * np.pi, DEPTH))
         dm.z = srs.z(dm.s)

         # Plot the original signal
         plt.clf()
         plt.subplot(121)
         plt.title('Original')
         plt.plot(dm.s[0])
         plt.plot(dm.s[1])
         plt.plot(dm.s[2])
         plt.subplot(122)
         # And the filtered signal!
         plt.title('Z transform')
         plt.plot(dm.z[0])
         plt.plot(dm.z[1])
         plt.plot(dm.z[2])
         plt.show()
        --%

    arguments:
        series:
            desc: A signal to determine the z-transform for.
            type: SeriesColumn

    returns:
        desc: The z-transform of the signal.
        type: SeriesColumn
    """

    return _map(series, _z)


# Private functions


def _z(a):

    """
    visible: False

    desc:
        Test.
    """

    return (a - np.nanmean(a)) / np.nanstd(a)


def _butter(signal, freq_range, order, btype, sampling_freq):

    """
    visible: False

    desc:
        Test.
    """

    global butter, sosfilt
    if butter is None:
        from scipy.signal import butter, sosfilt
        butter = fnc.memoize(butter)
    sos = butter(
        order,
        freq_range,
        btype=btype,
        fs=sampling_freq,
        output='sos'
    )
    return sosfilt(sos, signal)


def _map(series, fnc_, **kwdict):

    """
    visible: False

    desc:
        Applies a function to each cell. Or, if a numpy array is passed, only
        that array is processed.

    arguments:
        series:
            desc:	A signal to apply the function to, or a numpy array.
            type:	[SeriesColumn, ndarray]
        fnc_:
            desc:	The function to apply.

    keyword-dict:
        kwdict:		A dict with keyword arguments for fnc.

    returns:
        desc:	A new signal.
        type:	[SeriesColumn, ndarray]
    """

    f = lambda a: fnc_(a, **kwdict)
    if isinstance(series, _SeriesColumn):
        return fnc.map_(f, series)
    if isinstance(series, np.ndarray):
        return f(series)
    try:
        len(series)
    except TypeError:
        raise TypeError(u'Expects a SeriesColumn or an iterable object')
    return f(np.array(series))


def _blinkreconstruct(a, vt=5, vt_start=10, vt_end=5, maxdur=500, margin=10,
                      gap_margin=20, gap_vt=10, smooth_winlen=21, std_thr=3,
                      mode='original'):

    """
    visible: False

    desc:
        Reconstructs a single array.
    """
    if mode == 'advanced':
        from datamatrix._datamatrix._blinkreconstruct import \
            _blinkreconstruct_recursive
        return _blinkreconstruct_recursive(a, vt_start=vt_start, vt_end=vt_end,
                                           maxdur=maxdur, margin=margin,
                                           gap_margin=gap_margin,
                                           gap_vt=gap_vt,
                                           smooth_winlen=smooth_winlen,
                                           std_thr=std_thr)
    if mode != 'original':
        raise ValueError(
            'blinkreconstruct() mode should be "orignal" or "advanced"')
    warn('Using "original" blink-reconstruction mode. For new code, '
         '"advanced" mode is recommended.')
    # Create a copy of the signal, a smoothed version, and calculate the
    # velocity profile.
    a = np.copy(a)
    try:
        strace = _smooth(a, winlen=smooth_winlen)
    except Exception as e:
        warn(e)
        strace = a
    vtrace = strace[1:]-strace[:-1]
    # Start blink detection
    ifrom = 0
    lblink = []
    while True:
        # The onset of the blink is the moment at which the pupil velocity
        # exceeds the threshold.
        l = np.where(vtrace[ifrom:] < -vt)[0]
        if len(l) == 0:
            break  # No blink detected
        istart = l[0]+ifrom
        if ifrom == istart:
            break
        # The reversal period is the moment at which the pupil starts to dilate
        # again with a velocity above threshold.
        l = np.where(vtrace[istart:] > vt)[0]
        if len(l) == 0:
            ifrom = istart
            continue
        imid = l[0]+istart
        # The end blink period is the moment at which the pupil velocity drops
        # back to zero again.
        l = np.where(vtrace[imid:] < 0)[0]
        if len(l) == 0:
            ifrom = imid
            continue
        iend = l[0]+imid
        ifrom = iend
        # We generally underestimate the blink period, so compensate for this
        if istart-margin >= 0:
            istart -= margin
        if iend+margin < len(a):
            iend += margin
        # We don't accept blinks that are too long, because blinks are not
        # generally very long (although they can be).
        if iend-istart > maxdur:
            ifrom = istart+maxdur//10
            continue
        lblink.append((istart, iend))
    # Now reconstruct the trace during the blinks
    for istart, iend in lblink:
        # First create a list of (when possible) four data points that we can
        # use for interpolation.
        dur = iend - istart
        l = []
        if istart-dur >= 0:
            l += [istart-dur]
        l += [istart, iend]
        if iend+dur < len(strace):
            l += [iend+dur]
        x = np.array(l)
        # If the list is long enough we use cubic interpolation, otherwise we
        # use linear interpolation
        y = a[x]
        if len(x) >= 4:
            f2 = interp1d(x, y, kind='cubic')
        else:
            f2 = interp1d(x, y)
        xInt = np.arange(istart, iend)
        yInt = f2(xInt)
        a[xInt] = yInt

    # For all remaining gaps, replace them with the previous sample if
    # available
    b = np.where(
        (a < (a.mean()-std_thr*a.std()))
        | (a.mean() > (a+std_thr*a.std()))
        | np.isnan(a)
    )[0]
    for i in b:
        if i == 0:
            continue
        a[i] = a[i - 1]
    return a


def _smooth(a, winlen=11, wintype='hanning'):

    """
    visible: False

    desc:
        Smooths a single array.
    """

    if a.ndim != 1:
        raise ValueError('smooth only accepts 1 dimension arrays')
    if a.size < winlen:
        raise ValueError('input array must be larger than window size')
    if winlen < 3:
        return a
    if wintype not in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
        raise ValueError(
            "wintype should be 'flat', 'hanning', 'hamming', 'bartlett', or 'blackman'"
        )
    if not winlen % 2 or winlen < 0 or int(winlen) != winlen:
        raise ValueError('winlen must be a positive uneven integer')
    d = (winlen-1)//2
    s = np.r_[a[d:0:-1], a, a[-2:-d-2:-1]]
    if wintype == 'flat':  # moving average
        w = np.ones(winlen, 'd')
    else:
        func = getattr(np, wintype)
        w = func(winlen)
    y = np.convolve(w/np.nansum(w), s, mode='valid')
    return y


def _downsample(a, by, fnc=nanmean):

    """
    visible: False

    desc:
        Downsamples a single array.
    """

    # Resize the array so that its length is a multiple of by
    a = a[:by * (a.shape[0] // by)]
    return fnc(a.reshape(-1, by), axis=1)


def _interpolate(y):

    """
    visible: False

    desc:
        Performs linear interpolation of a single array.
    """

    y = np.copy(y)
    xnan = np.isnan(y)
    if np.sum(xnan) == len(y):
        warn(u'Cannot interpolate all-nan array')
        return y
    inan = np.where(xnan)
    x = np.arange(len(y))
    y[inan] = np.interp(x=inan, xp=x[~xnan], fp=y[~xnan])
    return y


def _occurrence(series, value, equal, reverse=False):
    """
    visible: False

    desc:
        The actual implement for the first_occurrence() and last_occurence()
        functions.
    """
    try:
        len(value)
    except (ValueError, TypeError):
        # Value is a single value
        # First rows and columns that match the value to search for. This goes
        # slightly differently for nan values than for other values because nans
        # are not equal to themselves
        if np.isnan(value):
            rows, cols = np.where(np.isnan(series) if equal else ~np.isnan(series))
        else:
            rows, cols = np.where(
                (series._seq == value) if equal else (series._seq != value))
    else:
        # Value is a sequence
        if len(value) != len(series):
            raise ValueError(
                'value must be a single value or a sequence of the same length as the series')
        rows = []
        cols = []
        for i, (haystack, needle) in enumerate(zip(series, value)):
            if np.isnan(needle):
                hits = np.where(np.isnan(haystack) if equal
                                else ~np.isnan(haystack))
            else:
                hits = np.where(haystack == needle if equal
                                else haystack != needle)
            hits = list(hits[0])
            rows += [i] * len(hits)
            cols += hits
        cols = np.array(cols)
        rows = np.array(rows)
    # Then create an empty array with a length equal to that of the series.
    # It's initialized to nan, which indicates that the value does not occur
    # at all in the row
    a = np.empty(len(series), dtype=float)
    a[:] = np.nan
    # The columns are provided in incremental order, and the last pair wins,
    # which means that highest matching col will be assigned to the row. When
    # searching for the first occurence (as opposed to the last occurrence)
    # this is not what we want. Rather, we want to lowest matching col to be
    # assigned to the row. To accomplish this, we simply reverse the matches.
    if reverse:
        a[rows[::-1]] = cols[::-1]
    else:
        a[rows] = cols
    # Turn the result into a float column
    col = FloatColumn(series.dm)
    col[:] = a
    return col


def _validate_series(obj):
    if not isinstance(obj, _MultiDimensionalColumn):
        raise TypeError('expecting a SeriesColumn or MultiDimensionalColumn '
                        'not {}'.format(type(obj)))
    if len(obj.shape) != 2:
        raise ValueError(
            'expecting a two dimensions, not {}'.format(len(obj.shape)))


def _validate_multiple_series(seq):
    if not seq:
        raise TypeError(
            'expecting at least one SeriesColumn or MultiDimensionalColumn')
    for obj in seq:
        if not isinstance(obj, _MultiDimensionalColumn):
            raise TypeError('expecting SeriesColumns or MultiDimensionalColumns '
                            'not {}'.format(type(obj)))
        if len(obj.shape) != 2:
            raise ValueError(
                'expecting two dimensions, not {}'.format(len(obj.shape)))


reduce_ = reduce  # Backwards compatibility
