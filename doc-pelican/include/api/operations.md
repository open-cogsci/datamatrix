<div class=" YAMLDoc" id="" markdown="1">

 

<div class="FunctionDoc YAMLDoc" id="auto_type" markdown="1">

## function __auto\_type__\(dm\)

*This modifies the DataMatrix in place.*

Converts all columns of type MixedColumn to IntColumn if all values are
integer numbers, or FloatColumn if all values are non-integer numbes.

%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.A = 'a'
 dm.B = 1
 dm.C = 1.1
 operations.auto_type(dm)
 print('dm.A: %s' % type(dm.A))
 print('dm.B: %s' % type(dm.B))
 print('dm.C: %s' % type(dm.C))
--%

__Arguments:__

- `dm` -- No description
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

## function __keep\_only__\(dm, cols=\[\]\)

*This modifies the DataMatrix in place.*

Removes all columns from the DataMatrix, except those listed in `cols`.

__Example:__
                
%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=5)
 dm.A = 'a', 'b', 'c', 'd', 'e'
 dm.B = range(5)
 operations.keep_only(dm, [dm.A])
 print(dm)
--%

__Arguments:__

- `dm` -- No description
	- Type: DataMatrix

__Keywords:__

- `cols` -- A list of column names, or columns.
	- Type: list
	- Default: []

</div>

[keep_only]: #keep_only

<div class="FunctionDoc YAMLDoc" id="replace" markdown="1">

## function __replace__\(col, mappings=\{\}\)

*This modifies the DataMatrix in place.*

Replaces values in a column by other values.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations
 
 dm = DataMatrix(length=3)
 dm.old = 0, 1, 2
 dm.new = dm.old[:]
 operations.replace(dm.new, {0 : 'a', 2 : 'c'})
 print(dm)
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

## function __split__\(col\)

Splits a DataMatrix by unique values in a column.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, operations
  
 dm = DataMatrix(length=4)
 dm.A = 0, 0, 1, 1
 dm.B = 'a', 'b', 'c', 'd'
 for A, dm in operations.split(dm.A):
        print('col.A = %s' % A)
        print(dm)               
--%

__Arguments:__

- `col` -- The column to split by.
	- Type: BaseColumn

__Returns:__

A iterator over (value, DataMatrix) tuples.

- Type: Iterator

</div>

[split]: #split

<div class="FunctionDoc YAMLDoc" id="tuple_split" markdown="1">

## function __tuple\_split__\(col, \*values\)

Splits a DataMatrix by values in a column, and returns the split as a
tuple of DataMatrix objects.

__Example:__

%--
python: |
         from datamatrix import DataMatrix, operations
         
         dm = DataMatrix(length=4)
         dm.A = 0, 0, 1, 1
         dm.B = 'a', 'b', 'c', 'd'
         dm0, dm1 = operations.tuple_split(dm.A, 0, 1)
         print('dm.A = 0')
         print(dm0)
         print('dm.A = 1')
         print(dm1)
--%

__Arguments:__

- `col` -- The column to split by.
	- Type: BaseColumn

__Argument list:__

- `*values`: A list values to split.

__Returns:__

A tuple of DataMatrix objects.

</div>

[tuple_split]: #tuple_split

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

