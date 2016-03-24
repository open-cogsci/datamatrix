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
import time
import subprocess
from datamatrix import io, series, SeriesColumn, DataMatrix, cached
from datamatrix._datamatrix._seriescolumn import _SeriesColumn
from datamatrix.py3compat import *


@cached
def lmer(dm, formula):

	cmd = u'''
library(lmerTest)
result <- lmer(%s)
s = summary(result)
s;
write.csv(s$coef, ".r-out.csv")
''' % formula
	rm = _launchr(dm, cmd)
	rm.rename(u'', u'effect')
	rm.rename(u'Estimate', u'est')
	rm.rename(u'Std. Error', u'se')
	rm.rename(u't value', u't')
	if u'Pr(>|t|)' in rm:
		rm.rename(u'Pr(>|t|)', u'p')
	else:
		rm.p = -1
	return rm


@cached
def glmer(dm, formula, family):

	cmd = u'''
library(lme4)
result <- glmer(%s, family="%s")
s = summary(result)
s;
write.csv(s$coef, ".r-out.csv")
''' % (formula, family)
	rm = _launchr(dm, cmd)
	rm.rename(u'', u'effect')
	rm.rename(u'Estimate', u'est')
	rm.rename(u'Std. Error', u'se')
	rm.rename(u'z value', u'z')
	if u'Pr(>|z|)' in rm:
		rm.rename(u'Pr(>|z|)', u'p')
	else:
		rm.p = -1
	return rm


@cached
def lmer_series(dm, formula, winlen=1):

	col = formula.split()[0]
	depth = dm[col].depth
	rm = None
	for i in range(0, depth, winlen):
		wm = dm[:]
		wm[col] = series.reduce_(
			series.window(wm[col], start=i, end=i+winlen))
		lm = lmer(wm, formula)
		print('Sample %d' % i)
		print(lm)
		if rm is None:
			rm = DataMatrix(length=len(lm))
			rm.effect = list(lm.effect)
			rm.p = SeriesColumn(depth=depth)
			rm.t = SeriesColumn(depth=depth)
			rm.est = SeriesColumn(depth=depth)
			rm.se = SeriesColumn(depth=depth)
		for lmrow, rmrow in zip(lm, rm):
			rmrow.p[i:i+winlen] = lmrow.p
			rmrow.t[i:i+winlen] = lmrow.t
			rmrow.est[i:i+winlen] = lmrow.est
			rmrow.se[i:i+winlen] = lmrow.se
	return rm


def _launchr(dm, cmd):

	dm = dm[:]
	# SeriesColumns cannot be saved to a csv file, so we delete those first.
	for name, col in dm.columns:
		if isinstance(col, _SeriesColumn):
			del dm[name]
	# Write the data to an input file
	io.writetxt(dm, u'.r-in.csv')
	# Launch R, read the data, and communicate the commands
	proc = subprocess.Popen( ['R', '--vanilla'], stdin=subprocess.PIPE)
	# proc = subprocess.Popen( ['R', '--vanilla'], stdin=subprocess.PIPE,
	# 	stdout=subprocess.PIPE, stderr=subprocess.PIPE)
	cmd = u'data <- read.csv(".r-in.csv")\nattach(data)\n%s' % cmd
	proc.communicate(safe_encode(cmd, u'ascii'))
	# Wait until the output file has been generated and return it
	while not os.path.exists(u'.r-out.csv'):
		time.sleep(.5)
	dm = io.readtxt(u'.r-out.csv')
	return dm
