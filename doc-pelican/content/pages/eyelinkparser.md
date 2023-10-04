title: Analyzing eye-movement data

[TOC]

## About this tutorial

We're going to analyze pupil-size data from an auditory-working-memory experiment. This data is taken from [Mathôt (2018)](#references), and you can find the data and experimental materials [here](https://github.com/smathot/pupillometry_review).

In this experiment, the participant first hears a series of digits; we will refer to this period as the `sounds` trace. The number of digits (set size) varies: 3, 5, or 7. Next, there is a retention interval during which the participant keeps the digits in memory; we will refer to this period as the `retention` trace. Finally, the participant enters the response.

We will analyze pupil size during the `sounds` and `retention` traces as a function of set size. As reported by [Kahneman and Beatty (1966)](#references), and as we will also see during this tutorial, the size of the pupil increases with set size.

This tutorial makes use of the [`eyelinkparser` module](https://github.com/smathot/python-eyelinkparser), which can be installed with pip:

~~~bash
pip install eyelinkparser
~~~

The data has been collected with an EyeLink 1000 eye tracker.


## Designing an experiment for easy analysis

EyeLink data files (and data files for most other eye trackers) correspond to an event log; that is, each line corresponds to some event. These events can be gaze samples, saccade onsets, user messages, etc.

For example, a `start_trial` user message followed by four gaze samples might look like this:

~~~text
MSG	451224 start_trial
451224	  517.6	  388.9	 1691.0	...
451225	  517.5	  389.1	 1690.0	...
451226	  517.3	  388.9	 1692.0	...
451227	  517.1	  388.7	 1693.0	...
~~~

When designing your experiment, it's important to send user messages in such a way that your analysis software, in this case `eyelinkparser`, knows how to interpret them. If you do, then data analysis will be easy, because you will not have to write a custom script to parse the data file from the ground up.

If you use [OpenSesame/ PyGaze](http://osdoc.cogsci.nl), most of these messages, with the exception of phase messages, will by default be sent in the below format automatically.


### Trials

The following messages indicate the start and end of a trial. The `trialid` argument is optional.

	start_trial [trialid]
	end_trial

### Variables

The following message indicates a variable and a value. For example, `var response_time 645` would tell `eyelinkparser` that the variable `response_time` has the value 645 on that particular trial.

	var [name] [value]

### Phases

Phases are named periods of continuous data. Defining phases during the experiment is the easiest way to segment your data into different epochs for analysis.

The following messages indicate the start and end of a phase. A phase is automatically ended when a new phase is started.

	start_phase [name]
	end_phase [name]

For each phase, four columns of type `SeriesColumn` will be created with information about fixations:

- `fixxlist_[phase name]` is a series of X coordinates
- `fixylist_[phase name]` is a series of Y coordinates
- `fixstlist_[phase name]` is a series of fixation start times
- `fixetlist_[phase name]` is a series of fixation end times
- `blinkstlist_[phase name]` is a series of blink start times
- `blinketlist_[phase name]` is a series of blink end times


Additionally, four columns will be created with information about individual gaze samples:

- `xtrace_[phase name]` is a series of X coordinates
- `ytrace_[phase name]` is a series of Y coordinates
- `ttrace_[phase name]` is a series of time stamps
- `ptrace_[phase name]` is a series of pupil sizes


## Analyzing data

### Parsing

We first define a function to parse the EyeLink data; that is, we read the data files, which are in `.asc` text format, into a `DataMatrix` object.

We define a `get_data()` function that is decorated with `@fnc.memoize()` such that parsing is not redone unnecessarily (see [memoization](%link:memoization%)).

```python
from datamatrix import (
  operations as ops,
  functional as fnc,
  series as srs
)
from eyelinkparser import parse, defaulttraceprocessor


@fnc.memoize(persistent=True)
def get_data():

    # The heavy lifting is done by eyelinkparser.parse()
    dm = parse(
        folder='data',           # Folder with .asc files
        traceprocessor=defaulttraceprocessor(
          blinkreconstruct=True, # Interpolate pupil size during blinks
          downsample=10,         # Reduce sampling rate to 100 Hz,
          mode='advanced'        # Use the new 'advanced' algorithm
        )
    )
    # To save memory, we keep only a subset of relevant columns.
    dm = dm[dm.set_size, dm.correct, dm.ptrace_sounds, dm.ptrace_retention, 
            dm.fixxlist_retention, dm.fixylist_retention]
    return dm
```

We now call this function to get the data as a a `DataMatrix`. If you want to clear the cache, you can call `get_data.clear()` first.

Let's also print out the `DataMatrix` to get some idea of what our data structure looks like. As you can see, traces are stored as [series](https://pythontutorials.eu/numerical/time-series/), which is convenient for further analysis.

```python
dm = get_data()
print(dm)
```


### Preprocessing

Next, we do some preprocessing of the pupil-size data.

We are interested in two traces, `sounds` and `retention`. The length of `sounds` varies, depending on how many digits were played back. The shorter traces are padded with `nan` values at the end. We therefore apply `srs.endlock()` to move the `nan` padding to the beginning of the trace.

To get some idea of what this means, let's plot pupil size during the `sounds` trace for the first 5 trials, both with and without applying `srs.endlock()`.

```python
from matplotlib import pyplot as plt
from datamatrix import series as srs

plt.figure()
plt.subplot(211)
plt.title('NANs at the end')
for pupil in dm.ptrace_sounds[:5]:
    plt.plot(pupil)
plt.subplot(212)
plt.title('NANs at the start')
for pupil in srs.endlock(dm.ptrace_sounds[:5]):
    plt.plot(pupil)
plt.show()
```

Next, we concatenate the (end-locked) `sounds` and `retention` traces, and save the result as a series called `pupil`.

```python
dm.pupil = srs.concatenate(
    srs.endlock(dm.ptrace_sounds),
    dm.ptrace_retention
)
```

We then perform baseline correction. As a baseline, we use the first two samples of the `sounds` trace. (This trace still has the `nan` padding at the end.)

```python
dm.pupil = srs.baseline(
    series=dm.pupil,
    baseline=dm.ptrace_sounds,
    bl_start=0,
    bl_end=2
)
```

And we explicitly set the depth of the `pupil` trace to 1200, which given our original 1000 Hz signal, downsampled 10 ×, corresponds to 12 s.

```python
dm.pupil.depth = 1200
```


### Analyzing pupil size

And now we plot the pupil traces for each of the three set sizes!

```python
import numpy as np


def plot_series(x, s, color, label):

    se = s.std / np.sqrt(len(s))
    plt.fill_between(x, s.mean-se, s.mean+se, color=color, alpha=.25)
    plt.plot(x, s.mean, color=color, label=label)


x = np.linspace(-7, 5, 1200)
dm3, dm5, dm7 = ops.split(dm.set_size, 3, 5, 7)

plt.figure()
plt.xlim(-7, 5)
plt.ylim(-150, 150)
plt.axvline(0, linestyle=':', color='black')
plt.axhline(1, linestyle=':', color='black')
plot_series(x, dm3.pupil, color='green', label='3 (N=%d)' % len(dm3))
plot_series(x, dm5.pupil, color='blue', label='5 (N=%d)' % len(dm5))
plot_series(x, dm7.pupil, color='red', label='7 (N=%d)' % len(dm7))
plt.ylabel('Pupil size (norm)')
plt.xlabel('Time relative to onset retention interval (s)')
plt.legend(frameon=False, title='Memory load')
plt.show()
```

And a beautiful replication of [Kahneman & Beatty (1966)](#references)!


### Analyzing fixations

Now let's look at fixations during the `retention` phase. To get an idea of how the data is structured, we print out the x, y coordinates of all fixations of the first two trials.

```python
for i, row in zip(range(2), dm):
    print('Trial %d' % i)
    for x, y in zip(
        row.fixxlist_retention,
        row.fixylist_retention
    ):
        print('\t', x, y)
```

A common way to plot fixation distributions is as a heatmap. To do this, we need to create numpy arrays from the `fixxlist_retention` and `fixylist_retention` columns. This will result in two 2D arrays, whereas `plt.hexbin()` expects two 1D arrays. So we additionally flatten the arrays.

The resulting heatmap clearly shows that fixations are clustered around the display center (512, 384), just as you would expect from an experiment in which the participant needs to maintain central fixation.

```python
import numpy as np

x = np.array(dm.fixxlist_retention)
y = np.array(dm.fixylist_retention)
x = x.flatten()
y = y.flatten()
plt.hexbin(x, y, gridsize=25)
plt.show()
```

## References

- Kahneman, D., & Beatty, J. (1966). Pupil diameter and load on memory. *Science*, 154(3756), 1583–1585. <https://doi.org/10.1126/science.154.3756.1583>
- Mathôt, S., (2018). Pupillometry: Psychology, Physiology, and Function. *Journal of Cognition*. 1(1), p.16. <https://doi.org/10.5334/joc.18>
