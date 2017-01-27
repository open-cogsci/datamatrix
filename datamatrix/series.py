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
from datamatrix import FloatColumn
import numpy as np
from numpy import nanmean, nanmedian
from scipy.interpolate import interp1d


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
	for i in range(len(series)):
		for j in range(series.depth-1, -1, -1):
			if not np.isnan(series[i,j]):
				break
		endlock_series[i,-j-1:] = series[i,:j+1]
	return endlock_series
	
	
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
	a = series[:,start:end]
	depth = a.shape[1]
	window_series = _SeriesColumn(series._datamatrix, depth)
	window_series[:] = a
	return window_series


def baseline(series, baseline, bl_start=-100, bl_end=None, reduce_fnc=None,
	method='divisive'):

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
		 dm.y2 = series.baseline(dm.y, dm.y, bl_start=0, bl_end=10,
		 	method='subtractive')
		 
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
			desc:	Specifies whether divisive or subtrace correction should be
					used. Divisive is the default for historical purposes, but
					subtractive is generally preferred.
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

	return _apply_fnc(series, _blinkreconstruct, vt=vt, maxdur=maxdur,
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

	return _apply_fnc(series, _smooth, winlen=winlen, wintype=wintype)
		
		
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

	return _apply_fnc(series, _downsample, by=by, fnc=fnc)
	

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


# Private functions


def _apply_fnc(series, _fnc, **kwdict):

	"""
	visible: False

	desc:
		Applies a function to each cell.

	arguments:
		series:
			desc:	A signal to apply the function to.
			type:	SeriesColumn
		_fnc:
			desc:	The function to apply.

	keyword-dict:
		kwdict:		A dict with keyword arguments for fnc.

	returns:
		desc:	A new signal.
		type:	SeriesColumn
	"""
	
	if not series:
		return _SeriesColumn(series._datamatrix, depth=series.depth)
	for i, cell in enumerate(series):
		new_cell = _fnc(cell, **kwdict)
		if not i:
			new_series = _SeriesColumn(series._datamatrix, depth=len(new_cell))
		new_series[i] = new_cell
	return new_series


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
	y = np.convolve(w/w.sum(), s, mode='valid')
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
