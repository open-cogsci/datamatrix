<div class=" YAMLDoc" id="" markdown="1">

 

<div class="FunctionDoc YAMLDoc" id="flatten" markdown="1">

## function __flatten__\(dm\)

Flattens all multidimensional columns of a datamatrix to float columns.
The result is a new datamatrix where each row of the original
datamatrix is repeated for each value of the multidimensional column.
The new datamatrix does not contain any multidimensional columns.

This function requires that all multidimensional columns in `dm` have
the same shape, or that `dm` doesn't contain any multidimensional
columns, in which case a copy of `dm` is returned.

*Version note:* Moved to `datamatrix.multidimensional` in 0.16.0

*Version note:* New in 0.15.0

__Example:__

%--
python: |
 from datamatrix import DataMatrix, MultiDimensionalColumn,              multidimensional as mdim

 dm = DataMatrix(length=2)
 dm.col = 'a', 'b'
 dm.m1 = MultiDimensionalColumn(shape=(3,))
 dm.m1[:] = 1,2,3
 dm.m2 = MultiDimensionalColumn(shape=(3,))
 dm.m2[:] = 3,2,1
 flat_dm = mdim.flatten(dm)
 print('Original:')
 print(dm)
 print('Flattened:')
 print(flat_dm)
--%

__Arguments:__

- `dm` -- A DataMatrix
	- Type: DataMatrix

__Returns:__

A 'flattened' DataMatrix without multidimensional columns

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="infcount" markdown="1">

## function __infcount__\(col\)

Counts the number of `INF` values for each cell in a multidimensional
column, and returns this as an int column.

*Version note:* Moved to `datamatrix.multidimensional` in 0.16.0

*Version note:* New in 0.15.0

__Example:__

%--
python: |
 from datamatrix import DataMatrix, MultiDimensionalColumn,              multidimensional as mdim, INF

 dm = DataMatrix(length=3)
 dm.m = MultiDimensionalColumn(shape=(3,))
 dm.m[0] = 1, 2, 3
 dm.m[1] = 1, 2, INF
 dm.m[2] = INF, INF, INF
 dm.nr_of_inf = mdim.infcount(dm.m)
 print(dm)
--%

__Arguments:__

- `col` -- A multidimensional column to count the `INF` values in.
	- Type: MultiDimensionalColumn

__Returns:__

An int column with the number of `INF` values in each cell.

- Type: IntColumn

</div>

<div class="FunctionDoc YAMLDoc" id="nancount" markdown="1">

## function __nancount__\(col\)

Counts the number of `NAN` values for each cell in a multidimensional
column, and returns this as an int column.

*Version note:* Moved to `datamatrix.multidimensional` in 0.16.0

*Version note:* New in 0.15.0

__Example:__

%--
python: |
 from datamatrix import DataMatrix, MultiDimensionalColumn,              multidimensional as mdim, NAN

 dm = DataMatrix(length=3)
 dm.m = MultiDimensionalColumn(shape=(3,))
 dm.m[0] = 1, 2, 3
 dm.m[1] = 1, 2, NAN
 dm.m[2] = NAN, NAN, NAN
 dm.nr_of_nan = mdim.nancount(dm.m)
 print(dm)
--%

__Arguments:__

- `col` -- A column to count the `NAN` values in.
	- Type: MultiDimensionalColumn

__Returns:__

An int column with the number of `NAN` values in each cell.

- Type: IntColumn

</div>

<div class="FunctionDoc YAMLDoc" id="reduce" markdown="1">

## function __reduce__\(col, operation=<function nanmean at 0x7f0ffbf8b370>\)

Transforms multidimensional values to single values by applying an
operation (typically a mean) to each multidimensional value.

*Version note:* Moved to `datamatrix.multidimensional` in 0.16.0

*Version note:* As of 0.11.0, the function has been renamed to
`reduce()`. The original `reduce_()` is deprecated.

__Example:__

%--
python: |
 import numpy as np
 from datamatrix import DataMatrix, MultiDimensionalColumn,              multidimensional as mdim

 dm = DataMatrix(length=5)
 dm.m = MultiDimensionalColumn(shape=(3, 3))
 dm.m = np.random.random((5, 3, 3))
 dm.mean_y = mdim.reduce(dm.m)
 print(dm)
--%

__Arguments:__

- `col` -- The column to reduce.
	- Type: MultiDimensionalColumn

__Keywords:__

- `operation` -- The operation function to use for the reduction. This function should accept `col` as first argument, and `axis=1` as keyword argument.
	- Default: <function nanmean at 0x7f0ffbf8b370>

__Returns:__

A reduction of the signal.

- Type: FloatColumn

</div>

</div>

