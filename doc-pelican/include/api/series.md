<div class=" YAMLDoc" id="" markdown="1">

 

<div class="FunctionDoc YAMLDoc" id="baseline" markdown="1">

## function __baseline__\(series, baseline, bl\_start=-100, bl\_end=None, reduce\_fnc=None, method=u'subtractive'\)

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

__Arguments:__

- `series` -- The signal to apply a baseline to.
	- Type: SeriesColumn
- `baseline` -- The signal to use as a baseline to.
	- Type: SeriesColumn

__Keywords:__

- `bl_start` -- The start of the window from `baseline` to use.
	- Type: int
	- Default: -100
- `bl_end` -- The end of the window from `baseline` to use, or None to go to the end.
	- Type: int, None
	- Default: None
- `reduce_fnc` -- The function to reduce the baseline epoch to a single value. If None, np.nanmedian() is used.
	- Type: FunctionType, None
	- Default: None
- `method` -- Specifies whether divisive or subtractive baseline
correction should be used. (*Changed in v0.7.0: subtractive
is now the default*)
	- Type: str
	- Default: 'subtractive'

__Returns:__

A baseline-correct version of the signal.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="blinkreconstruct" markdown="1">

## function __blinkreconstruct__\(series, vt=5, maxdur=500, margin=10, smooth\_winlen=21, std\_thr=3\)

Reconstructs pupil size during blinks. This algorithm has been designed
and tested largely with the EyeLink 1000 eye tracker.

__Source:__

- Mathot, S. (2013). A simple way to reconstruct pupil size during eye
blinks. <http://doi.org/10.6084/m9.figshare.688002>

__Arguments:__

- `series` -- A signal to reconstruct.
	- Type: SeriesColumn

__Keywords:__

- `vt` -- A pupil velocity threshold. Lower tresholds more easily trigger blinks.
	- Type: int, float
	- Default: 5
- `maxdur` -- The maximum duration (in samples) for a blink. Longer blinks are not reconstructed.
	- Type: int
	- Default: 500
- `margin` -- The margin to take around missing data.
	- Type: int
	- Default: 10
- `smooth_winlen` -- No description
	- Default: 21
- `std_thr` -- No description
	- Default: 3

__Returns:__

A reconstructed singal.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="concatenate" markdown="1">

## function __concatenate__\(\*series\)

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

__Argument list:__

- `*series`: A list of series.

__Returns:__

A new series.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="downsample" markdown="1">

## function __downsample__\(series, by, fnc=<function nanmean at 0x7f7b2af61158>\)

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

__Arguments:__

- `series` -- No description
- `by` -- The downsampling factor.
	- Type: int

__Keywords:__

- `fnc` -- The function to average the samples that are combined into 1 value. Typically an average or a median.
	- Type: callable
	- Default: <function nanmean at 0x7f7b2af61158>

__Returns:__

A downsampled series.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="endlock" markdown="1">

## function __endlock__\(series\)

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

__Arguments:__

- `series` -- The signal to end-lock.
	- Type: SeriesColumn

__Returns:__

An end-locked signal.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="interpolate" markdown="1">

## function __interpolate__\(series\)

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

__Arguments:__

- `series` -- A signal to interpolate.
	- Type: SeriesColumn

__Returns:__

The interpolated signal.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="lock" markdown="1">

## function __lock__\(series, lock\)

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

__Arguments:__

- `series` -- The signal to lock.
	- Type: SeriesColumn
- `lock` -- A sequence of lock values with the same length as the Series. This can be a column, a list, a numpy array, etc.

__Returns:__

A `(series, zero_point)` tuple, in which `series` is a `SeriesColumn` and `zero_point` is the zero point to which the signal has been locked.

</div>

<div class="FunctionDoc YAMLDoc" id="normalize_time" markdown="1">

## function __normalize\_time__\(dataseries, timeseries\)

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

__Arguments:__

- `dataseries` -- A column with datapoints.
	- Type: SeriesColumn
- `timeseries` -- A column with timestamps. This should be an increasing list of the same depth as `dataseries`. NAN values are allowed, but only at the end.
	- Type: SeriesColumn

__Returns:__

A new series in which the data points are spread according to the timestamps.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="reduce_" markdown="1">

## function __reduce\___\(series, operation=<function nanmean at 0x7f7b2af61158>\)

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

__Arguments:__

- `series` -- The signal to reduce.
	- Type: SeriesColumn

__Keywords:__

- `operation` -- The operation function to use for the reduction. This function should accept `series` as first argument, and `axis=1` as keyword argument.
	- Default: <function nanmean at 0x7f7b2af61158>

__Returns:__

A reduction of the signal.

- Type: FloatColumn

</div>

<div class="FunctionDoc YAMLDoc" id="smooth" markdown="1">

## function __smooth__\(series, winlen=11, wintype=u'hanning'\)

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

__Arguments:__

- `series` -- A signal to smooth.
	- Type: SeriesColumn

__Keywords:__

- `winlen` -- The width of the smoothing window. This should be an odd integer.
	- Type: int
	- Default: 11
- `wintype` -- The type of window from 'flat', 'hanning', 'hamming', 'bartlett', 'blackman'. A flat window produces a moving average smoothing.
	- Type: str
	- Default: 'hanning'

__Returns:__

A smoothed signal.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="threshold" markdown="1">

## function __threshold__\(series, fnc, min\_length=1\)

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

__Arguments:__

- `series` -- A signal to threshold.
	- Type: SeriesColumn
- `fnc` -- A function that takes a single value and returns True if this value exceeds a threshold, and False otherwise.
	- Type: FunctionType

__Keywords:__

- `min_length` -- The minimum number of samples for which `fnc` must return True.
	- Type: int
	- Default: 1

__Returns:__

A series where 0 indicates below threshold, and 1 indicates above threshold.

- Type: SeriesColumn

</div>

<div class="FunctionDoc YAMLDoc" id="window" markdown="1">

## function __window__\(series, start=0, end=None\)

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

__Arguments:__

- `series` -- The signal to get a window from.
	- Type: SeriesColumn

__Keywords:__

- `start` -- The window start.
	- Type: int
	- Default: 0
- `end` -- The window end, or None to go to the signal end.
	- Type: int, None
	- Default: None

__Returns:__

A window of the signal.

- Type: SeriesColumn

</div>

</div>

