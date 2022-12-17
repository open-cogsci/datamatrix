<div class=" YAMLDoc" id="" markdown="1">

 

<div class="ClassDoc YAMLDoc" id="Row" markdown="1">

## class __Row__

A single row from a DataMatrix.

<div class="FunctionDoc YAMLDoc" id="Row-__init__" markdown="1">

### function __Row\.\_\_init\_\___\(datamatrix, index\)

Constructor.

__Arguments:__

- `datamatrix` -- A DataMatrix object.
- `index` -- The row index.

</div>

</div>

<div class="ClassDoc YAMLDoc" id="_MultiDimensionalColumn" markdown="1">

## class ___MultiDimensionalColumn__

A column in which each cell is a float array.

<div class="FunctionDoc YAMLDoc" id="_MultiDimensionalColumn-__init__" markdown="1">

### function __\_MultiDimensionalColumn\.\_\_init\_\___\(datamatrix, shape, defaultnan=True, \*\*kwargs\)

Constructor. You generally don't call this constructor correctly, but use the MultiDimensional helper function.

__Arguments:__

- `datamatrix` -- The DataMatrix to which this column belongs.
	- Type: DataMatrix
- `shape` -- A tuple that specifies the number and size of the dimensions of each cell. Values can be integers, or tuples of non-integer values that specify names of indices, e.g. `shape=(('x', 'y'), 10)). Importantly, the length of the column (the number of rows) is implicitly used as the first dimension. That, if you specify a two-dimensional shape, then the resulting column has three dimensions.
	- Type: int

__Keywords:__

- `defaultnan` -- Indicates whether the column should be initialized with `nan` values (`True`) or 0s (`False`).
	- Type: bool
	- Default: True

__Keyword dict:__

- `**kwargs`: keywords that are passed on to the parent constructor.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-count" markdown="1">

### property ___MultiDimensionalColumn.count__

The number of unique values that occur in the column.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-depth" markdown="1">

### property ___MultiDimensionalColumn.depth__

A property to access and change the depth of the column. The depth is the second dimension of the column, where the length of the column (the number of rows) is the first dimension.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-dm" markdown="1">

### property ___MultiDimensionalColumn.dm__

The associated DataMatrix.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-loaded" markdown="1">

### property ___MultiDimensionalColumn.loaded__

A property to unloaded the column to disk (by assigning `False`) and load the column from disk (by assigning `True`). You don't usually change this property manually, but rather let the built-in memory management decide when and columns need to be (un)loaded.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-max" markdown="1">

### property ___MultiDimensionalColumn.max__

The highest numeric value in the column, or NAN if there are no numeric values.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-mean" markdown="1">

### property ___MultiDimensionalColumn.mean__

Arithmetic mean of all values. If there are non-numeric values, these are ignored. If there are no numeric values, NAN is returned.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-median" markdown="1">

### property ___MultiDimensionalColumn.median__

The median of all values. If there are non-numeric values, these are ignored. If there are no numeric values, NAN is returned.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-min" markdown="1">

### property ___MultiDimensionalColumn.min__

The lowest numeric value in the column, or NAN if there are no numeric values.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-name" markdown="1">

### property ___MultiDimensionalColumn.name__

The name of the column in the associated DataMatrix, or a list of names if the column occurs multiple times in the DataMatrix.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-plottable" markdown="1">

### property ___MultiDimensionalColumn.plottable__

Gives a view of the traces where the axes have been swapped. This is the format that matplotlib.pyplot.plot() expects.

</div>

<div class="FunctionDoc YAMLDoc" id="_MultiDimensionalColumn-setallrows" markdown="1">

### function __\_MultiDimensionalColumn\.setallrows__\(value\)

Sets all rows to a value, or array of values.

__Arguments:__

- `value` -- A value, or array of values that has the same length as the shape of the column.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-shape" markdown="1">

### property ___MultiDimensionalColumn.shape__

A property to access and change the shape of the column. The shape includes the length of the column (the number of rows) as the first dimension.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-std" markdown="1">

### property ___MultiDimensionalColumn.std__

The standard deviation of all values. If there are non-numeric values, these are ignored. If there are 0 or 1 numeric values, NAN is returned. The degrees of freedom are N-1.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-sum" markdown="1">

### property ___MultiDimensionalColumn.sum__

The sum of all values in the column, or NAN if there are no numeric values.

</div>

<div class="PropertyDoc YAMLDoc" id="_MultiDimensionalColumn-unique" markdown="1">

### property ___MultiDimensionalColumn.unique__

An interator for all unique values that occur in the column.

</div>

</div>

<div class="FunctionDoc YAMLDoc" id="auto_type" markdown="1">

## function __auto\_type__\(dm\)

*Requires fastnumbers*

Converts all columns of type MixedColumn to IntColumn if all values are
integer numbers, or FloatColumn if all values are non-integer numbers.

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=5)
 dm.A = 'a'
 dm.B = 1
 dm.C = 1.1
 dm_new = ops.auto_type(dm)
 print('dm_new.A: %s' % type(dm_new.A))
 print('dm_new.B: %s' % type(dm_new.B))
 print('dm_new.C: %s' % type(dm_new.C))
--%

__Arguments:__

- `dm` -- No description
	- Type: DataMatrix

__Returns:__

No description

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="bin_split" markdown="1">

## function __bin\_split__\(col, bins\)

Splits a DataMatrix into bins; that is, the DataMatrix is first sorted
by a column, and then split into equal-size (or roughly equal-size)
bins.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=5)
 dm.A = 1, 0, 3, 2, 4
 dm.B = 'a', 'b', 'c', 'd', 'e'
 for bin, dm in enumerate(ops.bin_split(dm.A, bins=3)):
    print('bin %d' % bin)
    print(dm)
--%

__Arguments:__

- `col` -- The column to split by.
	- Type: BaseColumn
- `bins` -- The number of bins.
	- Type: int

__Returns:__

A generator that iterates over the bins.

</div>

<div class="FunctionDoc YAMLDoc" id="fullfactorial" markdown="1">

## function __fullfactorial__\(dm, ignore=u''\)

*Requires numpy*

Creates a new DataMatrix that uses a specified DataMatrix as the base
of a full-factorial design. That is, each value of every row is 
combined with each value from every other row. For example:

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=2)
 dm.A = 'x', 'y'
 dm.B = 3, 4
 dm = ops.fullfactorial(dm)
 print(dm)
--%

__Arguments:__

- `dm` -- The source DataMatrix.
	- Type: DataMatrix

__Keywords:__

- `ignore` -- A value that should be ignored.
	- Default: ''

</div>

<div class="FunctionDoc YAMLDoc" id="group" markdown="1">

## function __group__\(dm, by\)

*Requires numpy*

Groups the DataMatrix by unique values in a set of grouping columns.
Grouped columns are stored as SeriesColumns. The columns that are
grouped should contain numeric values. The order in which groups appear
in the grouped DataMatrix is unpredictable.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=4)
 dm.A = 'x', 'x', 'y', 'y'
 dm.B = 0, 1, 2, 3
 print('Original:')
 print(dm)
 dm = ops.group(dm, by=dm.A)
 print('Grouped by A:')
 print(dm)
--%

__Arguments:__

- `dm` -- The DataMatrix to group.
	- Type: DataMatrix
- `by` -- A column or list of columns to group by.
	- Type: BaseColumn, list

__Returns:__

A grouped DataMatrix.

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="keep_only" markdown="1">

## function __keep\_only__\(dm, \*cols\)

Removes all columns from the DataMatrix, except those listed in `cols`.

*Version note:* As of 0.11.0, the preferred way to select a subset of
columns is using the `dm = dm[('col1', 'col2')]` notation.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=5)
 dm.A = 'a', 'b', 'c', 'd', 'e'
 dm.B = range(5)
 dm.C = range(5, 10)
 dm_new = ops.keep_only(dm, dm.A, dm.C)
 print(dm_new)
--%

__Arguments:__

- `dm` -- No description
	- Type: DataMatrix

__Argument list:__

- `*cols`: A list of column names, or column objects.

</div>

<div class="FunctionDoc YAMLDoc" id="pivot_table" markdown="1">

## function __pivot\_table__\(dm, values, index, columns, \*args, \*\*kwargs\)

*Requires pandas*

*Version note:* New in 0.14.1

Creates a pivot table where rows correspond to levels of `index`,
columns correspond to levels of `columns`, and cells contain aggregate
values of `values`.

A typical use for a pivot table is to create a summary report for a
data set. For example, in an experiment where reaction times of human
participants were measured on a large number of trials under different
conditions, each row might correspond to one participant, each column
to an experimental condition (or a combination of experimental
conditions), and cells might contain mean reaction times.

This function is a wrapper around the `pandas.pivot_table()`. For an
overview of possible `*args` and `**kwargs`, see
[this page](https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.pivot_table.html).

__Example:__

%--
python: |
 from datamatrix import operations as ops, io

 dm = io.readtxt('data/fratescu-replication-data-exp1.csv')
 pm = ops.pivot_table(dm, values=dm.RT_search, index=dm.subject_nr,
                      columns=dm.load)
 print(pm)
--%

__Arguments:__

- `dm` -- The source DataMatrix.
	- Type: DataMatrix
- `values` -- A column or list of columns to aggregate.
	- Type: BaseColumn, str, list
- `index` -- A column or list of columns to separate rows by.
	- Type: BaseColumn, str, list
- `columns` -- A column or list of columns to separate columns by.
	- Type: BaseColumn, str, list

__Argument list:__

- `*args`: No description.

__Keyword dict:__

- `**kwargs`: No description.

__Returns:__

No description

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="random_sample" markdown="1">

## function __random\_sample__\(obj, k\)

*New in v0.11.0*

Takes a random sample of `k` rows from a DataMatrix or column. The
order of the rows in the returned DataMatrix is random.

__Example:__

```python
from datamatrix import DataMatrix, operations as ops

dm = DataMatrix(length=5)
dm.A = 'a', 'b', 'c', 'd', 'e'
dm = ops.random_sample(dm, k=3)
print(dm)
```

__Arguments:__

- `obj` -- No description
	- Type: DataMatrix, BaseColumn
- `k` -- No description
	- Type: int

__Returns:__

A random sample from a DataMatrix or column.

- Type: DataMatrix, BaseColumn

</div>

<div class="FunctionDoc YAMLDoc" id="replace" markdown="1">

## function __replace__\(col, mappings=\{\}\)

Replaces values in a column by other values.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=3)
 dm.old = 0, 1, 2
 dm.new = ops.replace(dm.old, {0 : 'a', 2 : 'c'})
 print(dm_new)
--%

__Arguments:__

- `col` -- The column to weight by.
	- Type: BaseColumn

__Keywords:__

- `mappings` -- A dict where old values are keys and new values are values.
	- Type: dict
	- Default: {}

</div>

<div class="FunctionDoc YAMLDoc" id="shuffle" markdown="1">

## function __shuffle__\(obj\)

Shuffles a DataMatrix or a column. If a DataMatrix is shuffled, the
order of the rows is shuffled, but values that were in the same row
will stay in the same row.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=5)
 dm.A = 'a', 'b', 'c', 'd', 'e'
 dm.B = ops.shuffle(dm.A)
 print(dm)
--%

__Arguments:__

- `obj` -- No description
	- Type: DataMatrix, BaseColumn

__Returns:__

The shuffled DataMatrix or column.

- Type: DataMatrix, BaseColumn

</div>

<div class="FunctionDoc YAMLDoc" id="shuffle_horiz" markdown="1">

## function __shuffle\_horiz__\(\*obj\)

Shuffles a DataMatrix, or several columns from a DataMatrix,
horizontally. That is, the values are shuffled between columns from the
same row.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=5)
 dm.A = 'a', 'b', 'c', 'd', 'e'
 dm.B = range(5)
 dm = ops.shuffle_horiz(dm.A, dm.B)
 print(dm)
--%

__Argument list:__

- `*desc`: A list of BaseColumns, or a single DataMatrix.
- `*obj`: No description.

__Returns:__

The shuffled DataMatrix.

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="sort" markdown="1">

## function __sort__\(obj, by=None\)

Sorts a column or DataMatrix. In the case of a DataMatrix, a column
must be specified to determine the sort order. In the case of a column,
this needs to be specified if the column should be sorted by another
column.

The sort order is as follows:

- `-INF`
- `int` and `float` values in increasing order
- `INF`
- `str` values in alphabetical order, where uppercase letters come
  first
- `None`
- `NAN`

You can also sort columns (but not DataMatrix objects) using the
built-in `sorted()` function. However, when sorting different mixed
types, this may lead to Exceptions or (in the case of `NAN` values)
unpredictable results.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=3)
 dm.A = 2, 0, 1
 dm.B = 'a', 'b', 'c'
 dm = ops.sort(dm, by=dm.A)
 print(dm)
--%

__Arguments:__

- `obj` -- No description
	- Type: DataMatrix, BaseColumn

__Keywords:__

- `by` -- The sort key, that is, the column that is used for sorting the DataMatrix, or the other column.
	- Type: BaseColumn
	- Default: None

__Returns:__

The sorted DataMatrix, or the sorted column.

- Type: DataMatrix, BaseColumn

</div>

<div class="FunctionDoc YAMLDoc" id="split" markdown="1">

## function __split__\(col, \*values\)

Splits a DataMatrix by unique values in a column.

*Version note:* As of 0.12.0, `split()` accepts multiple columns as
shown below.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=4)
 dm.A = 0, 0, 1, 1
 dm.B = 'a', 'b', 'c', 'd'
 # If no values are specified, a (value, DataMatrix) iterator is
 # returned.
 print('Splitting by a single column')
 for A, sdm in ops.split(dm.A):
     print('sdm.A = %s' % A)
     print(sdm)
 # You can also split by multiple columns at the same time.
 print('Splitting by two columns')
 for A, B, sdm in ops.split(dm.A, dm.B):
     print('sdm.A = %s, sdm.B = %s' % (A, B))
 # If values are specific an iterator over DataMatrix objects is
 # returned.
 print('Splitting by values')
 dm_a, dm_c = ops.split(dm.B, 'a', 'c')
 print('dm.B == "a"')
 print(dm_a)
 print('dm.B == "c"')
 print(dm_c)
--%

__Arguments:__

- `col` -- The column to split by.
	- Type: BaseColumn

__Argument list:__

- `*values`: Splits the DataMatrix based on these values. If this is provided, an iterator over DataMatrix objects is returned, rather than an iterator over (value, DataMatrix) tuples.

__Returns:__

A iterator over (value, DataMatrix) tuples if no values are provided; an iterator over DataMatrix objects if values are provided.

- Type: Iterator

</div>

<div class="FunctionDoc YAMLDoc" id="stack" markdown="1">

## function __stack__\(\*dms\)

*Version note:* New in 0.16.0

Stacks multiple DataMatrix objects such that the resulting DataMatrix
has a length that is equal to the sum of all the stacked DataMatrix
objects. Phrased differently, this function vertically concatenates
DataMatrix objects.

Stacking two DataMatrix objects can also be done with the `<<`
operator. However, when stacking more than two DataMatrix objects,
using `stack()` is much faster than iteratively stacking with `<<`.

__Example:__

%--
python: |
 from datamatrix import operations as ops

 dm1 = DataMatrix(length=2)
 dm1.col = 'A'
 dm2 = DataMatrix(length=2)
 dm2.col = 'B'
 dm3 = DataMatrix(length=2)
 dm3.col = 'C'
 dm = ops.stack(dm1, dm2, dm3)
 print(dm)
--%

__Argument list:__

- `*dms`: OrderedDict([('desc', 'A list of DataMatrix objects.'), ('type', 'list')])

__Returns:__

No description

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="weight" markdown="1">

## function __weight__\(col\)

Weights a DataMatrix by a column. That is, each row from a DataMatrix
is repeated as many times as the value in the weighting column.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=3)
 dm.A = 1, 2, 0
 dm.B = 'x', 'y', 'z'
 print('Original:')
 print(dm)
 dm = ops.weight(dm.A)
 print('Weighted by A:')
 print(dm)
--%

__Arguments:__

- `col` -- The column to weight by.
	- Type: BaseColumn

__Returns:__

No description

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="z" markdown="1">

## function __z__\(col\)

Transforms a column into z scores such that the mean of all values is
0 and the standard deviation is 1.

*Version note:* As of 0.13.2, `z()` returns a `FloatColumn` when a
regular column is give. For non-numeric values, the z score is NAN. If
the standard deviation is 0, z scores are also NAN.

*Version note:* As of 0.15.3, `z()` also accepts series columns, in
which case the series is z-transformed such that the grand mean of
all samples is 0, and the grand standard deviation of all samples is
1.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 dm = DataMatrix(length=5)
 dm.col = range(5)
 dm.z = ops.z(dm.col)
 print(dm)
--%

__Arguments:__

- `col` -- The column to transform.
	- Type: BaseColumn

__Returns:__

No description

- Type: BaseColumn

</div>

</div>

