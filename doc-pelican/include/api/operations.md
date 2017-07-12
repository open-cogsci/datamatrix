<div class=" YAMLDoc" id="" markdown="1">

 

<div class="FunctionDoc YAMLDoc" id="auto_type" markdown="1">

## function __auto\_type__\(dm\)

*Requires fastnumbers*

Converts all columns of type MixedColumn to IntColumn if all values are
integer numbers, or FloatColumn if all values are non-integer numbes.

%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.A = 'a'
 dm.B = 1
 dm.C = 1.1
 dm_new = operations.auto_type(dm)
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

[auto_type]: #auto_type

<div class="FunctionDoc YAMLDoc" id="bin_split" markdown="1">

## function __bin\_split__\(col, bins\)

Splits a DataMatrix into bins; that is, the DataMatrix is first sorted
by a column, and then split into equal-size (or roughly equal-size)
bins.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.A = 1, 0, 3, 2, 4
 dm.B = 'a', 'b', 'c', 'd', 'e'
 for bin, dm in enumerate(operations.bin_split(dm.A, bins=3)):
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

[bin_split]: #bin_split

<div class="FunctionDoc YAMLDoc" id="filter_" markdown="1">

## function __filter\___\(fnc, obj\)

Filters rows from a datamatrix or column based on filter function
(`fnc`).

If `obj` is a column, `fnc` should be a function that accepts a single
value. If `obj` is a datamatrix, `fnc` should be a function that accepts
a keyword `dict`, where column names are keys and cells are values. In
both cases, `fnc` should return a `bool` indicating whether the row or
value should be included.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, functional as fnc
 
 dm = DataMatrix(length=5)
 dm.col = range(5)
 # Create a column with only odd values
 col_new = fnc.filter_(lambda x: x % 2, dm.col)
 print(col_new)
 # Create a new datamatrix with only odd values in col
 dm_new = fnc.filter_(lambda **d: d['col'] % 2, dm)
 print(dm_new)
--%

__Arguments:__

- `fnc` -- A filter function.
	- Type: callable
- `obj` -- A datamatrix or column to filter.
	- Type: BaseColumn, DataMatrix

__Returns:__

A new column or datamatrix.

- Type: BaseColumn, DataMatrix

</div>

[filter_]: #filter_

<div class="FunctionDoc YAMLDoc" id="fullfactorial" markdown="1">

## function __fullfactorial__\(dm, ignore=u''\)

*Requires numpy*

Creates a new DataMatrix that uses a specified DataMatrix as the base of
a full-factorial design. That is, each value of every row is combined
with each value from every other row. For example:
        
__Example:__
                
%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=2)
 dm.A = 'x', 'y'
 dm.B = 3, 4
 dm = operations.fullfactorial(dm)
 print(dm)
--%

__Arguments:__

- `dm` -- The source DataMatrix.
	- Type: DataMatrix

__Keywords:__

- `ignore` -- A value that should be ignored.
	- Default: ''

</div>

[fullfactorial]: #fullfactorial

<div class="FunctionDoc YAMLDoc" id="group" markdown="1">

## function __group__\(dm, by\)

*Requires numpy*

Groups the DataMatrix by unique values in a set of grouping columns.
Grouped columns are stored as SeriesColumns. The columns that are
grouped should contain numeric values.

__Example:__
                
%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=4)
 dm.A = 'x', 'x', 'y', 'y'
 dm.B = 0, 1, 2, 3
 print('Original:')
 print(dm)
 dm = operations.group(dm, by=dm.A)
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

[group]: #group

<div class="FunctionDoc YAMLDoc" id="keep_only" markdown="1">

## function __keep\_only__\(dm, \*cols\)

Removes all columns from the DataMatrix, except those listed in `cols`.

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

- `*cols`: OrderedDict([('desc', 'A list of column names, or columns.')])

</div>

[keep_only]: #keep_only

<div class="FunctionDoc YAMLDoc" id="map_" markdown="1">

## function __map\___\(fnc, obj\)

Maps a function (`fnc`) onto rows of datamatrix or cells of a column.

If `obj` is a column, the function `fnc` is mapped is mapped onto each
cell of the column, and a new column is returned. In this case,
`fnc` should be a function that accepts and returns a single value.

If `obj` is a datamatrix, the function `fnc` is mapped onto each row,
and a new datamatrix is returned. In this case, `fnc` should be a
function that accepts a keyword `dict`, where column names are keys and
cells are values. The return value should be another `dict`, again with
column names as keys, and cells as values. Columns that are not part of
the returned `dict` are left unchanged.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, functional as fnc
 
 dm = DataMatrix(length=3)
 dm.old = 0, 1, 2
 # Map a 2x function onto dm.old to create dm.new
 dm.new = fnc.map_(lambda i: i*2, dm.old)
 print(dm)
 # Map a 2x function onto the entire dm to create dm_new, using a fancy
 # dict comprehension wrapped inside a lambda function.
 dm_new = fnc.map_(
        lambda **d: {col : 2*val for col, val in d.items()},
        dm)
 print(dm_new)
--%

__Arguments:__

- `fnc` -- A function to map onto each row or each cell.
	- Type: callable
- `obj` -- A datamatrix or column to map `fnc` onto.
	- Type: BaseColumn, DataMatrix

__Returns:__

A new column or datamatrix.

- Type: BaseColumn, DataMatrix

</div>

[map_]: #map_

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

[replace]: #replace

<div class="FunctionDoc YAMLDoc" id="setcol" markdown="1">

## function __setcol__\(dm, name, value\)

Returns a new DataMatrix to which a column has been added or in which
a column has been modified.

The main difference with regular assignment (`dm.col = 'x'`) is that
`setcol()` does not modify the original DataMatrix, and can be used in
`lambda` expressions.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, functional as fnc

 dm1 = DataMatrix(length=5)
 dm2 = fnc.setcol(dm1, 'y', range(5))
 print(dm2)
--%

__Arguments:__

- `dm` -- A DataMatrix.
	- Type: DataMatrix
- `name` -- A column name.
	- Type: str
- `value` -- The value to be assigned to the column. This can be any value this is valid for a regular column assignment.

__Returns:__

A new DataMatrix.

- Type: DataMatrix

</div>

[setcol]: #setcol

<div class="FunctionDoc YAMLDoc" id="shuffle" markdown="1">

## function __shuffle__\(obj\)

Shuffles a DataMatrix or a column. If a DataMatrix is shuffled, the order
of the rows is shuffled, but values that were in the same row will stay
in the same row.

__Example:__
                
%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.A = 'a', 'b', 'c', 'd', 'e'
 dm.B = operations.shuffle(dm.A)
 print(dm)
--%

__Arguments:__

- `obj` -- No description
	- Type: DataMatrix, BaseColumn

__Returns:__

The shuffled DataMatrix or column.

- Type: DataMatrix, BaseColumn

</div>

[shuffle]: #shuffle

<div class="FunctionDoc YAMLDoc" id="shuffle_horiz" markdown="1">

## function __shuffle\_horiz__\(\*obj\)

Shuffles a DataMatrix, or several columns from a DataMatrix,
horizontally. That is, the values are shuffled between columns from the
same row.

__Example:__
                
%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.A = 'a', 'b', 'c', 'd', 'e'
 dm.B = range(5)
 dm = operations.shuffle_horiz(dm.A, dm.B)
 print(dm)
--%

__Argument list:__

- `*desc`: A list of BaseColumns, or a single DataMatrix.
- `*obj`: No description.

__Returns:__

The shuffled DataMatrix.

- Type: DataMatrix

</div>

[shuffle_horiz]: #shuffle_horiz

<div class="FunctionDoc YAMLDoc" id="sort" markdown="1">

## function __sort__\(obj, by=None\)

Sorts a column or DataMatrix. In the case of a DataMatrix, a column must
be specified to determine the sort order. In the case of a column, this
needs to be specified if the column should be sorted by another column.

The sort order depends on the version of Python. Python 2 is more
flexible, and allows comparisons between types such as `str` and `int`.
Python 3 does not allow such comparisons.

In general, whenever incomparable values are encountered, all values are
forced to `float`. Values that cannot be converted to float are
considered `inf`.

__Example:__
                
%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=3)
 dm.A = 2, 0, 1
 dm.B = 'a', 'b', 'c'
 dm = operations.sort(dm, by=dm.A)
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

[sort]: #sort

<div class="FunctionDoc YAMLDoc" id="split" markdown="1">

## function __split__\(col, \*values\)

Splits a DataMatrix by unique values in a column.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations as ops
  
 dm = DataMatrix(length=4)
 dm.A = 0, 0, 1, 1
 dm.B = 'a', 'b', 'c', 'd'
 # If no values are specified, a (value, DataMatrix) iterator is
 # returned.
 for A, dm in ops.split(dm.A):
        print('dm.A = %s' % A)
        print(dm)
 # If values are specific an iterator over DataMatrix objects is
 # returned.
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

[split]: #split

<div class="FunctionDoc YAMLDoc" id="weight" markdown="1">

## function __weight__\(col\)

Weights a DataMatrix by a column. That is, each row from a DataMatrix is
repeated as many times as the value in the weighting column.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=3)
 dm.A = 1, 2, 0
 dm.B = 'x', 'y', 'z'
 print('Original:')
 print(dm)
 dm = operations.weight(dm.A)
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

[weight]: #weight

<div class="FunctionDoc YAMLDoc" id="z" markdown="1">

## function __z__\(col\)

Transforms a column into z scores.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.col = range(5)
 dm.z = operations.z(dm.col)
 print(dm)
--%

__Arguments:__

- `col` -- The column to transform.
	- Type: BaseColumn

__Returns:__

No description

- Type: BaseColumn

</div>

[z]: #z

</div>

[dummy]: #dummy

