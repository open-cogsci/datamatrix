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

import os
import sys
import numpy as np
from matplotlib import pyplot as plt
from datamatrix.colors.tango import *

plotfolder = 'plot'
if '--clear-plot' in sys.argv and os.path.exists(plotfolder):
	print('Removing plot folder (%s)' % plotfolder)
	import shutil
	shutil.rmtree(plotfolder)
plt.style.use('ggplot')
plt.rc('font', family='liberation sans', size=10)

# Some pre-defined sizes
xs = 4, 4
s = 6, 6
ws = 6, 3
r = 8, 8
w = 12, 8
h = 8, 12
l = 12, 12
xl = 16, 16

def new(size=r):

	"""
	desc:
		Creates a new figure.

	keywords:
		size:
			desc:	The figure size.
			type:	tuple

	returns:
		A matplotlib figure.
	"""

	fig = plt.figure(figsize=size)
	plt.subplots_adjust(left=.15, right=.9, bottom=.15, top=.9, wspace=.3,
		hspace=.3)
	return fig


def trace(series, x=None, color=blue[1], err=True, **kwdict):

	"""
	desc:
		Creates an average-trace plot.

	arguments:
		series:
			desc:	The signal.
			type:	SeriesColumn

	keywords:
		x:
			desc:	An array for the X axis with the same length as series, or
					None for a default axis.
			type:	[ndarray, None]
		color:
			desc:	The color.
			type:	str
		label:
			desc:	A label for the line, or None for no label.
			type:	[str, None]
	"""

	y = series.mean
	ymin = y - series.std/np.sqrt(len(series))
	ymax = y + series.std/np.sqrt(len(series))
	if x is None:
		x = np.arange(len(y))
	if err:
		plt.fill_between(x, ymin, ymax, color=color, alpha=.2)
	plt.plot(x, y, color=color, **kwdict)


def threshold(a, y=1, min_length=1, **kwdict):

	inhit = False
	for x, hit in enumerate(a):
		if not inhit and hit:
			onset = x
			inhit = True
		if inhit and not hit:
			if x-onset >= min_length:
				plt.plot([onset, x], [y,y], **kwdict)
			inhit = False
	if inhit:
		if x-onset >= min_length:
			plt.plot([onset, x], [y,y], **kwdict)


def regress(x, y, annotate=True, symbol='.', linestyle='--',
	symbolcolor=blue[1], linecolor=blue[1], label=None):

	"""
	desc:
		Creates a regression plot.

	arguments:
		x:
			desc:	A column for the X data.
			type:	BaseColumn
		y:
			desc:	A column for the Y data.
			type:	BaseColumn

	keywords:
		annotate:
			desc:	Indicates whether the correlation and p-value should be
					marked in the plot.
			type:	bool
		symbol:			TODO
		linestyle:		TODO
		symbolcolor:	TODO
		linecolor:		TODO
		label:			TODO

	returns:
		desc:	The regression parameters as a (slope, intercept, correlation,
				p-value, standard error) tuple
		type:	tuple
	"""

	from scipy.stats import linregress
	s, i, r, p, se = linregress(x, y)
	plt.plot(x, y, symbol, color=symbolcolor)
	xData = np.array([min(x), max(x)])
	yData = i + s*xData
	plt.plot(xData, yData, linestyle, color=linecolor, label=label)
	if annotate:
		plt.text(0.05, 0.95, 'r = %.3f, p = %.3f' % (r, p), ha='left', \
			va='top', transform=plt.gca().transAxes)
	return s, i, r, p, se


def save(name, folder=None, show=False, dpi=200):

	"""
	desc:
		Saves the current figure to the correct folder, depending on the active
		experiment.

	arguments:
		name:
			desc:	The name for the figure.
			type:	bool

	keywords:
		folder:
			desc:	A name for a subfolder to save the plot or None to save
					directly in the plotfolder.
			type:	[str, None]
		show:
			desc:	Indicates whether the figure should be shown as well.
			type:	bool
		dpi:
			desc:	The dots per inch to use for the png export.
			type:	int
	"""

	if folder != None:
		_plotfolder = os.path.join(plotfolder, folder)
	else:
		_plotfolder = plotfolder
	try:
		os.makedirs(os.path.join(_plotfolder, 'svg'))
	except:
		pass
	try:
		os.makedirs(os.path.join(_plotfolder, 'png'))
	except:
		pass
	pathSvg = os.path.join(_plotfolder, 'svg', '%s.svg' % name)
	pathPng = os.path.join(_plotfolder, 'png', '%s.png' % name)
	plt.savefig(pathSvg)
	plt.savefig(pathPng, dpi=dpi)
	if show or '--show' in sys.argv:
		plt.show()
	else:
		plt.clf()
