title: Working with large data (dynamic loading)


[TOC]


## Dynamic loading of large data

When working with large datasets, especially those containing multidimensional data, the available memory easily becomes a limiting factor. For example, a multidimensional column of shape `(2000, 500, 500)` takes 3.7 Gb of memory.

DataMatrix automatically offloads multidimensional columns to disk when memory is running low. Let's see how this works by creating a DataMatrix with a single column of shape `(2000, 500, 500)`. (The first dimension corresponds to the length of the `DataMatrix`.) On its own, this column easily fits in memory, and we can use the `loaded` property to verify that the column has indeed been loaded into memory.


~~~python
from datamatrix import DataMatrix, MultiDimensionalColumn

dm = DataMatrix(length=2000)
dm.large_data1 = MultiDimensionalColumn(shape=(500, 500))
print(f'large_data1 loaded: {dm.large_data1.loaded}')
~~~

__Output:__

~~~
large_data1 loaded: True
~~~


However, if we add another column of the same size, memory starts to run low. Therefore, the old column (`large_data1`) is offloaded to disk, while the newly created column (`large_data2`) is held in memory. This happens automatically. 


~~~python
dm.large_data2 = MultiDimensionalColumn(shape=(500, 500))
print(f'large_data1 loaded: {dm.large_data1.loaded}')
print(f'large_data2 loaded: {dm.large_data2.loaded}')
~~~

__Output:__

~~~
large_data1 loaded: False
large_data2 loaded: True
~~~


DataMatrix tries to keep the most recently used columns in memory, and offloads the least recently used columns to disk. Therefore, if we assign the value 0 to `large_data1`, this column gets loaded into memory, while `large_data2` is offloaded to disk.


~~~python
import numpy as np

dm.large_data1 = 0
print(f'large_data1 loaded: {dm.large_data1.loaded}')
print(f'large_data2 loaded: {dm.large_data2.loaded}')
~~~

__Output:__

~~~
large_data1 loaded: True
large_data2 loaded: False
~~~


You can also manually force columns to be loaded into memory or offloaded to disk by changing the `loaded` property.


~~~python
dm.large_data1.loaded = False
print(f'large_data1 loaded: {dm.large_data1.loaded}')
print(f'large_data2 loaded: {dm.large_data2.loaded}')
~~~

__Output:__

~~~
large_data1 loaded: False
large_data2 loaded: False
~~~

## Individual column sizes should not exceed available memory

Dynamic loading works best when columns do not, by themselves, exceed the available memory, even though the total size of the `DataMatrix` may exceed the available memory. For example, dynamic loading works well for a 16 Gb system when working with a `DataMatrix` that consists of 3 multidimensional columns of 8 Gb. Here, the total size of the `DataMatrix` is 3 × 4 = 24 Gb, which exceeds the 16 Gb of available memory; however, each column on its own is only 8 Gb, which does not exceed the available memory.

It is aso possible (though not recommended) to create columns that, by themselves, exceed the available memory, such as a 24 Gb column on a 16 Gb system. However, many numerical operations, such as taking the mean or standard deviation, will cause all data to be loaded into memory, thus causing Python to crash due to insufficient memory.


## Implementation details

When a column is offloaded to disk, a `numpy.memmap` object is created instead of a regular `numpy.ndarray`. This object is mapped onto a hidden temporary file in the current working directory. Depending on the operating system, this temporary file is either invisible (unlinked) or has the extension `.memmap`.

See also:

- <https://numpy.org/doc/stable/reference/generated/numpy.memmap.html>
