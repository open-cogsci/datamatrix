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
    Convert between `DataMatrix` objects and types of data structures (notably
    `pandas.DataFrame`).
---
"""

from datamatrix.py3compat import *
from datamatrix._datamatrix._multidimensionalcolumn import \
    _MultiDimensionalColumn


def from_mne_epochs(epochs, ch_avg=False):
    """
    desc: |
        [Python MNE](https://mne.tools/) is a library for analysis of
        neurophysiological data.
        
        This function converts an `mne.Epochs()` object to a multidimensional
        column. The column's metadata is set to the `epochs.info` property. The
        length of the datamatrix should match the length of the metadata that
        was passed to `mne.Epochs()`. Rejected epochs result in `nan` values
        in the corresponding rows of the column.
        
        If channels are averaged, the shape of the resulting column is
        two-dimensional, where the first dimension is the number of rows and
        the second dimension is sample time.
        
        If channels not are averaged, the shape of the resulting column is
        three-dimensional, where the first dimension is the number of rows,
        the second dimension is the channel (which can be referenced by name),
        and the third dimension is sample time.
        
        *Version note:* New in 1.0.0
        
        %--
        python: |
            import numpy as np
            import pickle
            import mne
            from matplotlib import pyplot as plt
            from datamatrix import operations as ops, convert as cnv
            
            # First read a simple dataset that contains data from three occipital EEG
            # channels (O1, O2, Oz). `events` is an mne style array with event codes
            # and timestamps. `dm` is a datamatrix with trial information.
            with open('data/eeg-data.pkl', 'rb') as fd:
                raw, events, dm = pickle.loads(fd.read())
            # Create an Epochs object and convert it to a multidimensional column (dm.erp)
            epochs = mne.Epochs(raw, events, tmin=-.05, tmax=1.5,
                                metadata=cnv.to_pandas(dm))
            dm.erp = cnv.from_mne_epochs(epochs)
            # The last dimension corresponds to time, and the `index_names` property
            # contains the timestamps in seconds.
            channels = dm.erp.index_names[0]
            timestamps = dm.erp.index_names[1]
            # Split the data by stimulus intensity, and plot the mean signal over time
            plt.title(f'channels = {channels}')
            for intensity, idm in ops.split(dm.intensity):
                # Average over trials and channels, but not time
                plt.plot(timestamps, idm.erp[..., ...], label=str(intensity))
            plt.legend(title='Stimulus intensity')
            plt.xlabel('Time (s)')
            plt.ylabel('Voltage')
            plt.show()
        --%
    
    arguments:
        epochs:
            type: mne.Epochs
    
    keywords:
        ch_avg:
            desc: Determines whether the epochs should be averaged across
                  channels or not.
            type: bool
    
    returns:
        type: MultiDimensionalColumn
    """
    def inner(dm):
        data = epochs.get_data()
        if ch_avg:
            data = data.mean(axis=1)
            shape = (epochs.times, )
        else:
            shape = epochs.info['ch_names'], epochs.times
        col = _MultiDimensionalColumn(dm, shape=shape, metadata=epochs.info)
        col._seq[epochs.metadata.index] = data
        return col
    return inner, {}


def from_mne_tfr(tfr, ch_avg=False, freq_avg=False):
    """
    desc: |
        [Python MNE](https://mne.tools/) is a library for analysis of
        neurophysiological data.
        
        This function converts an `mne.EpochsTFR()` object to a 
        multidimensional column. The column's metadata is set to the
        `tfr.info` property. The length of the datamatrix should match the 
        length of the metadata that was passed to `mne.Epochs()`. Rejected 
        epochs result in `nan` values in the corresponding rows of the column.
        
        If both channels and frequencies are averaged, the shape of the
        resulting column is two-dimensional, where the first dimension is the 
        number of rows and the second dimension is sample time.
        
        If only channels are averaged, the shape of the resulting column is
        three-dimensional, where the first dimension is the number of rows, the
        second dimension is frequency, and the third dimension is sample time.
        
        If only frequencies are averaged, the shape of the resulting column is
        three-dimensional, where the first dimension is the number of rows, the
        second dimension is channel (which can be referenced by name), and the
        third dimension is sample time.
        
        If nothing is averaged, the shape of the resulting column is
        four-dimensional, where the first dimension is the number of rows,
        the second dimension is the channel (which can be referenced by name),
        the third dimension is frequency, and the fourth dimension is sample
        time.
        
        *Version note:* New in 1.0.0
        
        %--
        python: |
            import numpy as np
            import pickle
            import mne
            from mne.time_frequency import tfr_morlet
            from matplotlib import pyplot as plt
            from datamatrix import operations as ops, convert as cnv
            
            # First read a simple dataset that contains data from three occipital EEG
            # channels (O1, O2, Oz). `events` is an mne style array with event codes
            # and timestamps. `dm` is a datamatrix with trial information.
            with open('data/eeg-data.pkl', 'rb') as fd:
                raw, events, dm = pickle.loads(fd.read())
            # Create an Epochs object. From there, create a TFR object. From there, create
            # a multidimensional column.
            epochs = mne.Epochs(raw, events, tmin=-.5, tmax=2, metadata=cnv.to_pandas(dm))
            tfr = tfr_morlet(epochs, freqs=np.arange(4, 30, 1), n_cycles=2,
                             return_itc=False, average=False)
            tfr.crop(0, 1.5)
            dm.tfr = cnv.from_mne_tfr(tfr)
            # Plot the 
            channels = dm.tfr.index_names[0]
            plt.title(f'channels = {channels}')
            # Average over trials and channels, but not frequency or time.
            plt.imshow(dm.tfr[..., ...], aspect='auto')
            plt.xticks(dm.tfr.index_values[2][::100], dm.tfr.index_names[2][::100])
            plt.yticks(dm.tfr.index_values[1][::4], dm.tfr.index_names[1][::4])
            plt.xlabel('Time (s)')
            plt.ylabel('Frequency (Hz)')
            plt.show()
        --%
    
    arguments:
        tfr:
            type: mne.EpochsTFR
    
    keywords:
        ch_avg:
            desc: Determines whether the data should be averaged across
                  channels or not.
            type: bool
        freq_avg:
            desc: Determines whether the data should be averaged across
                  frequencies or not.
            type: bool
    
    returns:
        type: MultiDimensionalColumn
    """    
    def inner(dm):
        data = tfr.data
        if ch_avg and freq_avg:
            data = data.mean(axis=(1, 2))
            shape = len(tfr.times)
        elif ch_avg:
            data = data.mean(axis=1)
            shape = tfr.freqs, tfr.times
        elif freq_avg:
            data = data.mean(axis=2)
            shape = tfr.info['ch_names'], tfr.times
        else:
            shape = tfr.info['ch_names'], tfr.freqs, tfr.times
        col = _MultiDimensionalColumn(dm, shape=shape, metadata=tfr.info)
        col._seq[tfr.metadata.index] = data
        return col
    return inner, {}
