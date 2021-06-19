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
from datamatrix._datamatrix._basecolumn import BaseColumn
import os


def _set_globals():

    global nib, IMAGES, image, np
    import nibabel as nib
    import numpy as np
    from nilearn import image

    IMAGES = nib.nifti1.Nifti1Image, nib.nifti2.Nifti2Image
    _set_globals = lambda: None  # suicide


class NiftiColumn(BaseColumn):

    """
    desc:
        A column that contains either Nifti images or None values.
    """

    default_value = None

    def __init__(self, datamatrix):

        _set_globals()
        super(NiftiColumn, self).__init__(datamatrix)

    @property
    def mean(self):

        _set_globals()
        s = self.shape
        if s is None:
            raise ValueError(u'Nifti images must have the same shape')
        f = self.format
        if s is None:
            raise ValueError(u'Nifti images must have the same format')
        data = np.empty((len(self),) + s)
        for i, img in enumerate(self._images):
            data[i] = img.get_fdata()
        return f(np.nanmean(data, axis=0), self.affine)

    @property
    def shape(self):

        shape = None
        for img in self._images:
            if shape is not None and shape != img.shape:
                return None
            shape = img.shape
        return shape

    @property
    def format(self):

        format = None
        for img in self._images:
            if format is not None and not isinstance(img, format):
                return None
            format = type(img)
        return format

    @property
    def affine(self):

        _set_globals()
        affine = None
        for img in self._images:
            if affine is not None and np.any(affine != img.affine):
                return None
            affine = img.affine
        return affine

    @property
    def _images(self):

        return [img for img in self._seq if img is not None]

    def _checktype(self, value):

        _set_globals()
        if value is None or isinstance(value, IMAGES):
            return value
        if isinstance(value, basestring) and os.path.isfile(value):
            return image.load_img(value)
        raise TypeError('Invalid type: {}'.format(value))

    def _tosequence(self, value, length=None):

        if isinstance(value, (basestring, IMAGES)):
            return [self._checktype(value)] * (
                len(self._datamatrix)
                if length is None
                else length
            )
        return super(NiftiColumn, self)._tosequence(value, length=length)

    def _printable_list(self):

        return [u'' if img is None else u'[nifti]' for img in self._seq]

    # To implement

    @property
    def median(self):

        raise NotImplementedError(u'Not implemented for NiftiColumns')

    @property
    def std(self):

        raise NotImplementedError(u'Not implemented for NiftiColumns')

    @property
    def max(self):

        raise NotImplementedError(u'Not implemented for NiftiColumns')

    @property
    def min(self):

        raise NotImplementedError(u'Not implemented for NiftiColumns')

    @property
    def sum(self):

        raise NotImplementedError(u'Not implemented for NiftiColumns')

    @property
    def unique(self):

        raise NotImplementedError(u'Not implemented for NiftiColumns')
