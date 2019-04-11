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
	A set of operations to apply to `SeriesColumn` objects.
---
"""

from datamatrix.py3compat import *
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix import FloatColumn, operations as ops, functional as fnc
import numpy as np
from numpy import nanmean, nanmedian
from scipy.interpolate import interp1d


# Placeholders for imports that will occur in _butter()
butter = None
lfilter = None


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

	if not series or not all(isinstance(s, _SeriesColumn) for s in series):
		raise TypeError(u'Expecting one or more SeriesColumn objects')
	if not all(s.dm is series[0].dm for s in series):
		raise ValueError(
			u'SeriesColumn objects don\'t belong to the same DataMatrix')
	newseries = _SeriesColumn(series[0]._datamatrix,
		depth=sum(s.depth for s in series))
	i = 0
	for s in series:
		newseries[:,i:i+s.depth] = s
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
		 from datamatrix import DataMatrix, SeriesColumn, series

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
		 dm.y2 = series.endlock(dm.y)

		 plt.clf()
		 plt.subplot(121)
		 plt.title('Original (nans at end)')
		 plt.plot(dm.y.plottable)
		 plt.subplot(122)
		 plt.title('Endlocked (nans at start)')
		 plt.plot(dm.y2.plottable)
		 plt.savefig('content/pages/img/series/endlock.png')
		--%

		%--
		figure:
		 source: endlock.png
		 id: FigEndLock
		--%

	arguments:
		series:
			desc:	The signal to end-lock.
			type:	SeriesColumn

	returns:
		desc:	An end-locked signal.
		type:	SeriesColumn
	"""

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
		depth. This is useful to lock, or align, a series based on a sequence of
		values.

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
		 	row.y = np.roll(np.cos(np.linspace(0, np.pi, DEPTH)),
		 		row.x_offset)+row.y_offset
		 # Now use the x offset to lock the traces to the 0 point of the cosine,
		 # i.e. to their peaks.
		 dm.y2, zero_point = srs.lock(dm.y, lock=dm.x_offset)

		 plt.clf()
		 plt.subplot(121)
		 plt.title('Original')
		 plt.plot(dm.y.plottable)
		 plt.subplot(122)
		 plt.title('Locked to peak')
		 plt.plot(dm.y2.plottable)
		 plt.axvline(zero_point, color='black', linestyle=':')
		 plt.savefig('content/pages/img/series/lock.png')
		--%

		%--
		figure:
		 source: lock.png
		 id: FigLock
		--%

	arguments:
		series:
			desc:	The signal to lock.
			type:	SeriesColumn
		lock:
			desc:	A sequence of lock values with the same length as the
					Series. This can be a column, a list, a numpy array, etc.

	returns:
		desc:	A `(series, zero_point)` tuple, in which `series` is a
				`SeriesColumn` and `zero_point` is the zero point to which the
				signal has been locked.
	"""

	if not isinstance(series, _SeriesColumn):
		raise TypeError('series should be a SeriesColumn')
	if len(series) != len(lock):
		raise ValueError('lock and series should be the same length')
	try:
		zero_point = int(max(lock))
	except TypeError:
		raise TypeError('lock should be a sequence of integers')
	lpad = [int(zero_point-l) for l in lock]
	lock_series = _SeriesColumn(series.dm, series.depth+max(lpad))
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

		The resulting series will generally contain a lot of `nan` values, which
		you can interpolate with `interpolate()`.

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
		 plt.savefig('content/pages/img/series/normalize_time.png')
		--%

		%--
		figure:
		 source: normalize_time.png
		 id: FigNormalizeTime
		--%

	arguments:
		dataseries:
			desc:	A column with datapoints.
			type:	SeriesColumn
		timeseries:
			desc:	A column with timestamps. This should be an increasing list
					of the same depth as `dataseries`. NAN values are allowed,
					but only at the end.
			type:	SeriesColumn

	returns:
		desc:	A new series in which the data points are spread according to
				the timestamps.
		type:	SeriesColumn
	"""

	if (
		not isinstance(dataseries, _SeriesColumn)
		or not isinstance(timeseries, _SeriesColumn)
	):
		raise TypeError(
			'dataseries and timeseries should be SeriesColumn objects'
		)
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
		series._seq[row,indices] = values
	return series


def reduce_(series, operation=nanmean):

	"""
	desc: |
		Transforms series to single values by applying an operation (typically
		a mean) to each series.

		__Example:__

		%--
		python: |
		 import numpy as np
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 5 # Number of rows
		 DEPTH = 10 # Depth (or length) of SeriesColumns

		 dm = DataMatrix(length=LENGTH)
		 dm.y = SeriesColumn(depth=DEPTH)
		 dm.y = np.random.random( (LENGTH, DEPTH) )
		 dm.mean_y = series.reduce_(dm.y)

		 print(dm)
		--%

	arguments:
		series:
			desc:	The signal to reduce.
			type:	SeriesColumn

	keywords:
		operation:
			desc:	The operation function to use for the reduction. This
					function should accept `series` as first argument, and
					`axis=1` as keyword argument.

	returns:
		desc:	A reduction of the signal.
		type:	FloatColumn
	"""

	col = FloatColumn(series._datamatrix)
	try:
		a = operation(series, axis=1)
	except TypeError:
		for i, val in enumerate(series):
			col[i] = operation(val)
	else:
		col[:] = a
	return col


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
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 5 # Number of rows
		 DEPTH = 10 # Depth (or length) of SeriesColumnsplt.show()

		 sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

		 dm = DataMatrix(length=LENGTH)
		 # First create five identical rows with a sinewave
		 dm.y = SeriesColumn(depth=DEPTH)
		 dm.y.setallrows(sinewave)
		 # Add a random offset to the Y values
		 dm.y += np.random.random(LENGTH)
		 # Look only the middle half of the signal
		 dm.y2 = series.window(dm.y, start=DEPTH//4, end=-DEPTH//4)

		 plt.clf()
		 plt.subplot(121)
		 plt.title('Original')
		 plt.plot(dm.y.plottable)
		 plt.subplot(122)
		 plt.title('Window (middle half)')
		 plt.plot(dm.y2.plottable)
		 plt.savefig('content/pages/img/series/window.png')
		--%

		%--
		figure:
		 source: window.png
		 id: FigWindow
		--%

	arguments:
		series:
			desc:	The signal to get a window from.
			type:	SeriesColumn

	keywords:
		start:
			desc:	The window start.
			type:	int
		end:
			desc:	The window end, or None to go to the signal end.
			type:	[int, None]

	returns:
		desc:	A window of the signal.
		type:	SeriesColumn
	"""

	if end is None:
		end = series.depth
	return series[:, start:end]


def baseline(series, baseline, bl_start=-100, bl_end=None, reduce_fnc=None,
	method='subtractive'):

	"""
	desc: |
		Applies a baseline to a signal

		__Example:__

		%--
		python: |
		 import numpy as np
		 from matplotlib import pyplot as plt
		 from datamatrix import DataMatrix, SeriesColumn, series

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
		 dm.y2 = series.baseline(dm.y, dm.y, bl_start=0, bl_end=10)

		 plt.clf()
		 plt.subplot(121)
		 plt.title('Original')
		 plt.plot(dm.y.plottable)
		 plt.subplot(122)
		 plt.title('Baseline corrected')
		 plt.plot(dm.y2.plottable)
		 plt.savefig('content/pages/img/series/baseline.png')
		--%

		%--
		figure:
		 source: baseline.png
		 id: FigBaseline
		--%

	arguments:
		series:
			desc:	The signal to apply a baseline to.
			type:	SeriesColumn
		baseline:
			desc:	The signal to use as a baseline to.
			type:	SeriesColumn

	keywords:
		bl_start:
			desc:	The start of the window from `baseline` to use.
			type:	int
		bl_end:
			desc:	The end of the window from `baseline` to use, or None to go
					to the end.
			type:	[int, None]
		reduce_fnc:
			desc:	The function to reduce the baseline epoch to a single value.
					If None, np.nanmedian() is used.
			type:	[FunctionType, None]
		method:
			desc: |
					Specifies whether divisive or subtractive baseline
					correction should be used. (*Changed in v0.7.0: subtractive
					is now the default*)
			type:	str

	returns:
		desc:	A baseline-correct version of the signal.
		type:	SeriesColumn
	"""

	if reduce_fnc is None:
		reduce_fnc = nanmedian
	baseline = reduce_(window(baseline, start=bl_start, end=bl_end),
		operation=reduce_fnc)
	if method == 'divisive':
		return series / baseline
	if method == 'subtractive':
		return series - baseline
	raise Exception('Baseline method should be divisive or subtractive')


def blinkreconstruct(series, vt=5, maxdur=500, margin=10, smooth_winlen=21,
	std_thr=3):

	"""
	desc: |
		Reconstructs pupil size during blinks. This algorithm has been designed
		and tested largely with the EyeLink 1000 eye tracker.

		__Source:__

		- Mathot, S. (2013). A simple way to reconstruct pupil size during eye
		blinks. <http://doi.org/10.6084/m9.figshare.688002>

	arguments:
		series:
			desc:	A signal to reconstruct.
			type:	SeriesColumn

	keywords:
		vt:
			desc:	A pupil velocity threshold. Lower tresholds more easily
					trigger blinks.
			type:	[int, float]
		maxdur:
			desc:	The maximum duration (in samples) for a blink. Longer
					blinks are not reconstructed.
			type:	int
		margin:
			desc:	The margin to take around missing data.
			type:	int

	returns:
		desc:	A reconstructed singal.
		type:	SeriesColumn
	"""

	return _map(series, _blinkreconstruct, vt=vt, maxdur=maxdur,
		margin=margin, smooth_winlen=21, std_thr=3)


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
		 from datamatrix import DataMatrix, SeriesColumn, series

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
		 dm.y2 = series.smooth(dm.y)

		 plt.clf()
		 plt.subplot(121)
		 plt.title('Original')
		 plt.plot(dm.y.plottable)
		 plt.subplot(122)
		 plt.title('Smoothed')
		 plt.plot(dm.y2.plottable)
		 plt.savefig('content/pages/img/series/smooth.png')
		--%

		%--
		figure:
		 source: smooth.png
		 id: FigSmooth
		--%

	arguments:
		series:
			desc:	A signal to smooth.
			type:	SeriesColumn

	keywords:
		winlen:
			desc:	The width of the smoothing window. This should be an odd
					integer.
			type:	int
		wintype:
			desc:	The type of window from 'flat', 'hanning', 'hamming',
					'bartlett', 'blackman'. A flat window produces a moving
					average smoothing.
			type:	str

	returns:
		desc:	A smoothed signal.
		type:	SeriesColumn
	"""

	return _map(series, _smooth, winlen=winlen, wintype=wintype)


def downsample(series, by, fnc=nanmean):

	"""
	desc: |
		Downsamples a series by a factor, so that it becomes 'by' times shorter.
		The depth of the downsampled series is the highest multiple of the depth
		of the original series divided by 'by'. For example, downsampling a
		series with a depth of 10 by 3 results in a depth of 3.

		__Example:__

		%--
		python: |
		 import numpy as np
		 from matplotlib import pyplot as plt
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 1 # Number of rows
		 DEPTH = 100 # Depth (or length) of SeriesColumns

		 sinewave = np.sin(np.linspace(0, 2*np.pi, DEPTH))

		 dm = DataMatrix(length=LENGTH)
		 dm.y = SeriesColumn(depth=DEPTH)
		 dm.y.setallrows(sinewave)
		 dm.y2 = series.downsample(dm.y, by=10)

		 plt.clf()
		 plt.subplot(121)
		 plt.title('Original')
		 plt.plot(dm.y.plottable, 'o-')
		 plt.subplot(122)
		 plt.title('Downsampled')
		 plt.plot(dm.y2.plottable, 'o-')
		 plt.savefig('content/pages/img/series/downsample.png')
		--%

		%--
		figure:
		 source: downsample.png
		 id: FigDownsample
		--%

	arguments:
		by:
			desc:	The downsampling factor.
			type:	int

	keywords:
		fnc:
			desc:	The function to average the samples that are combined
					into 1 value. Typically an average or a median.
			type:	callable

	returns:
		desc:	A downsampled series.
		type:	SeriesColumn
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
		 from datamatrix import DataMatrix, SeriesColumn, series

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
		 dm.t = series.threshold(dm.y, fnc=lambda y: y > 0, min_length=10)

		 plt.clf()
		 # Mark the thresholded signal
		 plt.fill_between(np.arange(DEPTH), dm.t[0], color='black', alpha=.25)
		 plt.plot(dm.y.plottable)
		 plt.savefig('content/pages/img/series/threshold.png')

		 print(dm)
		--%

		%--
		figure:
		 source: threshold.png
		 id: FigThreshold
		--%

	arguments:
		series:
			desc:	A signal to threshold.
			type:	SeriesColumn
		fnc:
			desc:	A function that takes a single value and returns True if
					this value exceeds a threshold, and False otherwise.
			type:	FunctionType

	keywords:
		min_length:
			desc:	The minimum number of samples for which `fnc` must return
					True.
			type:	int

	returns:
		desc:	A series where 0 indicates below threshold, and 1 indicates
				above threshold.
		type:	SeriesColumn
	"""

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
				threshold_series[i,j-nhit:j] = 1
			nhit = 0
		if nhit >= min_length:
			threshold_series[i,j-nhit+1:j+1] = 1
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
		 from datamatrix import DataMatrix, SeriesColumn, series

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

		 # And plot the original data as circles and the interpolated data as dotted
		 # lines
		 plt.clf()
		 plt.plot(dm.i.plottable, ':')
		 plt.plot(dm.y.plottable, 'o')
		 plt.savefig('content/pages/img/series/interpolate.png')
		--%

		%--
		figure:
		 source: interpolate.png
		 id: FigInterpolate
		--%

	arguments:
		series:
			desc:	A signal to interpolate.
			type:	SeriesColumn


	returns:
		desc:	The interpolated signal.
		type:	SeriesColumn
	"""

	return ops.map_(_interpolate, series)


def filter_bandpass(series, freq_range, order=2):

	"""
	desc: |
		*New in v0.9.2*

		Applies a Butterworth low-pass filter to the signal. The filter
		frequency is a number between 1 and depth/2 - 1 (i.e. one less than the
		Nyquist frequency).

		For more information, see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html).

		__Example:__

		%--
		python: |
		 import numpy as np
		 from matplotlib import pyplot as plt
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 3
		 DEPTH = 200

		 # Create a fast, a medium, and a slow oscillation
		 dm = DataMatrix(length=LENGTH)
		 dm.s = SeriesColumn(depth=DEPTH)
		 dm.s[0] = np.sin(np.linspace(0, 20 * np.pi, DEPTH))
		 dm.s[1] = np.sin(np.linspace(0, 10 * np.pi, DEPTH))
		 dm.s[2] = np.cos(np.linspace(0, 1 * np.pi, DEPTH))
		 dm.f = series.filter_bandpass(dm.s, freq_range=(4, 6))

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
		 plt.savefig('content/pages/img/series/bandpass.png')
		--%

		%--
		figure:
		 source: bandpass.png
		 id: FigBandpass
		--%

	arguments:
		series:
			desc:	A signal to filter.
			type:	SeriesColumn
		freq_range:
			desc:	A `(min_freq, max_freq)` tuple.
			type:	tuple

	keywords:
		order:
			desc:	The order of the filter.
			type:	int

	returns:
		desc:	The filtered signal.
		type:	SeriesColumn
	"""

	return _map(
		series,
		_butter,
		freq_range=freq_range,
		order=order,
		btype='bandpass'
	)


def filter_highpass(series, freq_min, order=2):

	"""
	desc: |
		*New in v0.9.2*

		Applies a Butterworth low-pass filter to the signal. The filter
		frequency is a number between 1 and depth/2 - 1 (i.e. one less than the
		Nyquist frequency).

		For more information, see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html).

		__Example:__

		%--
		python: |
		 import numpy as np
		 from matplotlib import pyplot as plt
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 3
		 DEPTH = 200

		 # Create one fast oscillation, and two combined fast and slow oscillations
		 dm = DataMatrix(length=LENGTH)
		 dm.s = SeriesColumn(depth=DEPTH)
		 dm.s[0] = np.sin(np.linspace(0, 20 * np.pi, DEPTH))
		 dm.s[1] = np.sin(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]
		 dm.s[2] = np.cos(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]
		 dm.f = series.filter_highpass(dm.s, freq_min=3)

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
		 plt.savefig('content/pages/img/series/highpass.png')
		--%

		%--
		figure:
		 source: highpass.png
		 id: FigHighpass
		--%

	arguments:
		series:
			desc:	A signal to filter.
			type:	SeriesColumn
		freq_min:
			desc:	The minimum filter frequency.
			type:	int

	keywords:
		order:
			desc:	The order of the filter.
			type:	int

	returns:
		desc:	The filtered signal.
		type:	SeriesColumn
	"""

	return _map(
		series,
		_butter,
		freq_range=freq_min,
		order=order,
		btype='highpass'
	)


def filter_lowpass(series, freq_max, order=2):

	"""
	desc: |
		*New in v0.9.2*

		Applies a Butterworth low-pass filter to the signal. The filter
		frequency is a number between 1 and depth/2 - 1 (i.e. one less than the
		Nyquist frequency).

		For more information, see [`scipy.signal`](https://docs.scipy.org/doc/scipy/reference/signal.html).

		__Example:__

		%--
		python: |
		 import numpy as np
		 from matplotlib import pyplot as plt
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 3
		 DEPTH = 200

		 # Create one fast oscillation, and two combined fast and slow oscillations
		 dm = DataMatrix(length=LENGTH)
		 dm.s = SeriesColumn(depth=DEPTH)
		 dm.s[0] = np.sin(np.linspace(0, 20 * np.pi, DEPTH))
		 dm.s[1] = np.sin(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]
		 dm.s[2] = np.cos(np.linspace(0, 2 * np.pi, DEPTH)) + dm.s[0]
		 dm.f = series.filter_lowpass(dm.s, freq_max=3)

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
		 plt.savefig('content/pages/img/series/lowpass.png')
		--%

		%--
		figure:
		 source: lowpass.png
		 id: FigLowpass
		--%

	arguments:
		series:
			desc:	A signal to filter.
			type:	SeriesColumn
		freq_max:
			desc:	The maximum filter frequency.
			type:	int

	keywords:
		order:
			desc:	The order of the filter.
			type:	int

	returns:
		desc:	The filtered signal.
		type:	SeriesColumn
	"""

	return _map(
		series,
		_butter,
		freq_range=freq_max,
		order=order,
		btype='lowpass'
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
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 3
		 DEPTH = 200

		 # Create one fast oscillation, and two combined fast and slow oscillations
		 dm = DataMatrix(length=LENGTH)
		 dm.s = SeriesColumn(depth=DEPTH)
		 dm.s[0] = np.sin(np.linspace(0, 150 * np.pi, DEPTH))
		 dm.s[1] = np.sin(np.linspace(0, 75 * np.pi, DEPTH))
		 dm.s[2] = np.sin(np.linspace(0, 10 * np.pi, DEPTH))
		 dm.f = series.fft(dm.s)

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
		 plt.savefig('content/pages/img/series/fft.png')
		--%

		%--
		figure:
		 source: fft.png
		 id: FigFFT
		--%

	arguments:
		series:
			desc:	A signal to determine the FFT for.
			type:	SeriesColumn

	keywords:
		truncate:
			desc:	FFT series of real signals are symmetric. The `truncate`
					keyword indicates whether the last (symmetric) part of the
					FFT should be removed.
			type:	bool

	returns:
		desc:	The FFT of the signal.
		type:	SeriesColumn
	"""

	newseries = _SeriesColumn(series._datamatrix, depth=series.depth)
	newseries[:] = np.fft.fft(series, axis=1)
	if truncate:
		newseries.depth = newseries.depth // 2
	return newseries


def z(series):

	"""
	desc: |
		Applies a *z*-transform to the signal such that each trace has a mean
		value of 0 and a standard deviation of 1.

		__Example:__

		%--
		python: |
		 import numpy as np
		 from matplotlib import pyplot as plt
		 from datamatrix import DataMatrix, SeriesColumn, series

		 LENGTH = 3
		 DEPTH = 200

		 # Create one fast oscillation, and two combined fast and slow oscillations
		 dm = DataMatrix(length=LENGTH)
		 dm.s = SeriesColumn(depth=DEPTH)
		 dm.s[0] = 1 * np.sin(np.linspace(0, 4 * np.pi, DEPTH))
		 dm.s[1] = 2 * np.sin(np.linspace(.4, 4.4 * np.pi, DEPTH))
		 dm.s[2] = 3 * np.sin(np.linspace(.8, 4.8 * np.pi, DEPTH))
		 dm.z = series.z(dm.s)

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
		 plt.savefig('content/pages/img/series/z.png')
		--%

		%--
		figure:
		 source: z.png
		 id: FigZ
		--%

	arguments:
		series:
			desc:	A signal to determine the z-transform for.
			type:	SeriesColumn

	returns:
		desc:	The z-transform of the signal.
		type:	SeriesColumn
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


def _butter(signal, freq_range, order, btype):

	"""
	visible: False

	desc:
		Test.
	"""

	global butter, lfilter
	if butter is None:
		from scipy.signal import butter, lfilter
		butter = fnc.memoize(butter)
	nyq = .5 * len(signal)
	if btype == 'bandpass':
		freq_range = freq_range[0] / nyq, freq_range[1] / nyq
	else:
		freq_range /= nyq
	b, a = butter(order, freq_range, btype=btype)
	return lfilter(b, a, signal)


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


def _blinkreconstruct(a, vt=5, maxdur=500, margin=10, smooth_winlen=21,
	std_thr=3):

	"""
	visible: False

	desc:
		Reconstructs a single array.
	"""

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
			break # No blink detected
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
		lblink.append( (istart, iend) )
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

	# For all remaining gaps, replace them with the previous sample if available
	b = np.where( (a < (a.mean()-std_thr*a.std())) \
		| (a.mean() > (a+std_thr*a.std())) \
		| np.isnan(a) )[0]
	for i in b:
		if i == 0:
			continue
		a[i] = a[i-1]
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
	if not wintype in ['flat', 'hanning', 'hamming', 'bartlett', 'blackman']:
		raise ValueError(
			"wintype should be 'flat', 'hanning', 'hamming', 'bartlett', or 'blackman'")
	if not winlen % 2 or winlen < 0 or int(winlen) != winlen:
		raise ValueError('winlen must be a positive uneven integer')
	d = (winlen-1)//2
	s = np.r_[a[d:0:-1], a, a[-2:-d-2:-1]]
	if wintype == 'flat': #moving average
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
