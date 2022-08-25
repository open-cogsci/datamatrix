<div class=" YAMLDoc" id="" markdown="1">

 

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

