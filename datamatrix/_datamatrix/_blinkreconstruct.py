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
desc: pass
---
"""
from datamatrix.py3compat import *
from datamatrix import series as srs
import numpy as np
from scipy.interpolate import interp1d


def _blink_points(vtrace, vt_start, vt_end, maxdur, margin):
    """Detects the starting and ending index of the first blink in the trace,
    based on a velocity threshold. Returns None if no blink was detected.
    """
    # Detect a blink
    # The onset of the blink is the moment at which the pupil velocity
    # exceeds the threshold
    astart = np.where(vtrace < -vt_start)[0]
    if len(astart) == 0:
        return None
    istart = astart[0]
    # The reversal period is the moment at which the pupil starts to dilate
    # again with a velocity above threshold.
    amid = np.where(vtrace[istart:] > vt_end)[0]
    if len(amid) == 0:
        return None
    imid = amid[0] + istart
    # The end blink period is the moment at which the pupil velocity drops
    # back to zero again.
    aend = np.where(vtrace[imid:] < 0)[0]
    if len(aend) == 0:
        return None
    iend = aend[0] + imid
    # We generally underestimate the blink period, so compensate for this
    if istart - margin >= 0:
        istart -= margin
    if iend + margin < len(vtrace):
        iend += margin
    # We don't accept blinks that are too long, because blinks are not
    # generally very long (although they can be).
    if iend - istart > maxdur:
        logger.debug('blink too long ({})'.format(iend - istart))
        return None
    return np.array([istart, iend])


def _cubic_spline_points(a, istart, iend):
    """Takes two points that indicate the start and end of a blink, and tries
    to find two more equidistance points around them, which can be used for
    cubic-spline interpolation. All points need to fall within the trace and
    cannot be None. If successfull, an array of four indices is returned; if
    unsuccessfull, None is returned.
    """
    dur = iend - istart
    points = np.array([istart - dur, istart, iend, iend + dur])
    for point in points:
        if point < 0 or point >= len(a) or np.isnan(a[point]):
            return None
    return points


def _group(a):
    """Yields starting and ending indices of groups of contiguous indices."""
    if len(a) == 0:
        return
    if len(a) == 1:
        yield a[0], a[0] + 1
        return
    d = np.diff(a)
    i = np.where(d > 1)[0] + 1
    if len(i) == 0:
        yield a[0], a[-1] + 1
        return
    if len(i) == 1:
        yield a[0], a[i[0] - 1] + 1
        yield a[i[0]], a[-1] + 1
        return
    for j, (i1, i2) in enumerate(zip(i[:-1], i[1:])):
        if j == 0:
            yield a[0], a[i1 - 1] + 1
        yield a[i1], a[i2 - 1] + 1
    yield a[i2], a[-1] + 1


def _trim(a, vtrace, std_thr, gap_margin, gap_vt):
    """Sets missing data, or values that diverge too much from the mean, or
    values that exceed a velocity threshold to zero, taking a margin around the
    trimmed data. The only gaps that are not trimmed are at the end.
    """
    indices = np.where(
        (a < (a.mean() - std_thr * a.std())) |
        (a.mean() > (a + std_thr * a.std())) |
        np.isnan(a)
    )[0]
    for istart, iend in _group(indices):
        if iend == len(a):
            continue
        a[istart - gap_margin:iend + gap_margin] = np.nan
    indices = np.where(np.abs(vtrace) > gap_vt)[0]
    for istart, iend in _group(indices):
        if iend == len(a):
            continue
        a[istart - gap_margin:iend + gap_margin] = np.nan
    return a


def _blinkreconstruct_recursive(a, vt_start=10, vt_end=5, maxdur=500,
                                margin=10, gap_margin=20, gap_vt=10,
                                smooth_winlen=21, std_thr=3):
    """Implements a recursive blink-reconstruction algorithm that is a big
    improvement over the original algorithm.
    """
    def fnc_recursive(a):
        """Shortcut for recursive function call that retains all keywords."""
        return _blinkreconstruct_recursive(a, vt_start=vt_start, vt_end=vt_end,
                                           maxdur=maxdur, margin=margin,
                                           gap_margin=gap_margin,
                                           gap_vt=gap_vt,
                                           smooth_winlen=smooth_winlen,
                                           std_thr=std_thr)
    # Create a copy of the signal, smooth it, and calculate the velocity
    a = np.copy(a)
    try:
        strace = srs._smooth(a, winlen=smooth_winlen)
    except Exception as e:
        warn(e)
        strace = a
    vtrace = np.diff(strace)
    # Get the first occuring blink
    blink_points = _blink_points(vtrace, vt_start=vt_start, vt_end=vt_end,
                                 maxdur=maxdur, margin=margin)
    # If no blink exists, we trim the signal as a final operation and then
    # leave it.
    if blink_points is None:
        logger.debug('no more blinks')
        return _trim(a, vtrace, std_thr=std_thr, gap_margin=gap_margin,
                     gap_vt=gap_vt)
    # If a blink exists, see if we can get four valid points around it for
    # cubic spline interpolation. If not, then we do linear interpolation.
    istart, iend = blink_points
    cubic_spline_points = _cubic_spline_points(vtrace, istart, iend)
    if cubic_spline_points is None:
        logger.debug('linear interpolation: {}'.format(str(blink_points)))
        interp_fnc = interp1d(blink_points, a[blink_points])
    else:
        logger.debug('cubic-spline interpolation: {}'.format(
            str(cubic_spline_points)))
        interp_fnc = interp1d(
            cubic_spline_points,
            a[cubic_spline_points],
            kind='cubic')
    interp_x = np.arange(istart, iend)
    a[interp_x] = interp_fnc(interp_x)
    # Recursive call to self to continue cleaning up other blinks (if any)
    return fnc_recursive(a)
