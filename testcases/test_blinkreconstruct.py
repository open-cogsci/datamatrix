"""This file is part of datamatrix.

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
import numpy as np
from datamatrix import series as srs


def _add_blink(a, t0, t1):
    d = np.linspace(0, -1000, 50)
    u = np.linspace(-1000, 0, 50)
    a[t0:t0 + 50] += d
    if t1 is None:
        a[t0 + 50:] = np.nan
    else:
        a[t1 - 50:t1] += u
        a[t0 + 50:t1 - 50] = np.nan


def test_blinkreconstruct():
    
    noise = np.load('testcases/data/eyetracking-noise.npy')
    # We first test a situation where three blinks should be reconstructed.
    # The first and last blink should be linear because they are close to the
    # edges. The middle blink should be cubic.
    a = np.sin(np.linspace(0, 2 * np.pi, 2000)) * 100 + 1500
    _add_blink(a, 50, 250)
    _add_blink(a, 700, 1100)
    _add_blink(a, 1700, 1900)
    a += np.concatenate(4 * [noise[:500]])
    b = srs._blinkreconstruct(a, mode='advanced')
    assert not np.any(np.isnan(b))
    assert np.nanstd(b) < np.nanstd(a)
    # We now test a complex situatin in which there is first one long period
    # of missing that should not be reconstructed, followed by a 
    # reconstructable blink, followed by missing data at the end that should
    # not be reconstructed.
    a = np.sin(np.linspace(0, 2 * np.pi, 2000)) * 100 + 1500
    _add_blink(a, 500, 1200)
    _add_blink(a, 1300, 1500)
    _add_blink(a, 1900, None)
    a += np.concatenate(4 * [noise[:500]])
    b = srs._blinkreconstruct(a, mode='advanced')
    assert np.nanstd(b) < np.nanstd(a)
