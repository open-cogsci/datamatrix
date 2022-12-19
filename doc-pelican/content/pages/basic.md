title: Basic use

Ultra-short cheat sheet:

~~~python
from datamatrix import DataMatrix, io
# Read a DataMatrix from file
dm = io.readtxt('data.csv')
# Create a new DataMatrix
dm = DataMatrix(length=5)
# The first two rows
print(dm[:2])
# Create a new column and initialize it with the Fibonacci series
dm.fibonacci = 0, 1, 1, 2, 3
# You can also specify column names as if they are dict keys
dm['fibonacci'] = 0, 1, 1, 2, 3
# Remove 0 and 3 with a simple selection
dm = (dm.fibonacci > 0) & (dm.fibonacci < 3)
# Get a list of indices that match certain criteria
print(dm[(dm.fibonacci > 0) & (dm.fibonacci < 3)])
# Select 1, 1, and 2 by matching any of the values in a set
dm = dm.fibonacci == {1, 2}
# Select all odd numbers with a lambda expression
dm = dm.fibonacci == (lambda x: x % 2)
# Change all 1s to -1
dm.fibonacci[dm.fibonacci == 1] = -1
# The first two cells from the fibonacci column
print(dm.fibonacci[:2])
# Column mean
print('Mean: %s' % dm.fibonacci.mean)
# Multiply all fibonacci cells by 2
dm.fibonacci_times_two = dm.fibonacci * 2
# Loop through all rows
for row in dm:
    print(row.fibonacci) # get the fibonacci cell from the row
# Loop through all columns
for colname, col in dm.columns:
    for cell in col: # Loop through all cells in the column
        print(cell) # do something with the cell
# Or just see which columns exist
print(dm.column_names)
~~~

__Important note:__ Because of a limitation (or feature, if you will) of the Python language, the behavior of `and`, `or`, and chained (`x < y < z`) comparisons cannot be modified. These therefore do not work with `DataMatrix` objects as you would expect them to:

~~~python
# INCORRECT: The following does *not* work as expected
dm = dm.fibonacci > 0 and dm.fibonacci < 3
# INCORRECT: The following does *not* work as expected
dm = 0 < dm.fibonacci < 3
# CORRECT: Use the '&' operator
dm = (dm.fibonacci > 0) & (dm.fibonacci < 3)
~~~

Slightly longer cheat sheet:

[TOC]


## Creating a DataMatrix

Create a new `DataMatrix` object with a length (number of rows) of 2, and add a column (named `col`). By default, the column is of the `MixedColumn` type, which can store numeric, string, and `None` data.

```python
import sys
from datamatrix import DataMatrix, __version__
dm = DataMatrix(length=2)
dm.col = '☺'
print('DataMatrix v{} on Python {}\n'.format(__version__, sys.version))
print(dm)
```

You can change the length of the `DataMatrix` later on. If you reduce the length, data will be lost. If you increase the length, empty cells (by default containing empty strings) will be added.

```python
dm.length = 3
```

## Reading and writing files

You can read and write files with functions from the `datamatrix.io` module. The main supported file types are `csv` and `xlsx`.

```python
from datamatrix import io

dm = DataMatrix(length=3)
dm.col = 1, 2, 3
# Write to disk
io.writetxt(dm, 'my_datamatrix.csv')
io.writexlsx(dm, 'my_datamatrix.xlsx')
# And read it back from disk!
dm = io.readtxt('my_datamatrix.csv')
dm = io.readxlsx('my_datamatrix.xlsx')
```

Multidimensional columns cannot be saved to `csv` or `xlsx` format but instead need to be saved to a custom binary format.

```
from datamatrix import MultiDimensionalColumn
dm.mdim_col = MultiDimensionalColumn(shape=2)
# Write to disk
io.writebin(dm, 'my_datamatrix.dm')
# And read it back from disk!
dm = io.readbin('my_datamatrix.dm')
```


## Stacking (vertically concatenating) DataMatrix objects

You can stack two `DataMatrix` objects using the `<<` operator. Matching columns will be combined. (Note that row 2 is empty. This is because we have increased the length of `dm` in the previous step, causing an empty row to be added.)


```python
dm2 = DataMatrix(length=2)
dm2.col = '☺'
dm2.col2 = 10, 20
dm3 = dm << dm2
print(dm3)
```

Pro-tip: To stack three or more `DataMatrix` objects, using [the `stack()` function from the `operations` module](%url:operations) is faster than iteratively using the `<<` operator.

```python
from datamatrix import operations as ops
dm4 = ops.stack(dm, dm2, dm3)
```

## Working with columns

### Referring to columns

You can refer to columns in two ways: as keys in a `dict` or as properties. The two notations are identical for most purposes. The main reason to use a `dict` style is when the name of the column is itself variable. Otherwise, the property style is recommended for clarity.

```python
dm['col']  # dict style
dm.col     # property style
```

### Creating columns

By assigning a value to a non-existing colum, a new column is created and initialized to this value.

```python
dm.col = 'Another value'
print(dm)
```


### Renaming columns


```python
dm.rename('col', 'col2')
print(dm)
```

### Deleting columns

You can delete a column using the `del` keyword:


```python
dm.col = 'x'
del dm.col2
print(dm)
```

### Column types

There are five column types:

- `MixedColumn` is the default column type. This can contain numbers (`int` and `float`), strings (`str`), and `None` values. This column type is flexible but not very fast because it is (mostly) implemented in pure Python, rather than using `numpy`, which is the basis for the other columns. The default value for empty cells is an empty string.
- `FloatColumn` contains `float` numbers. The default value for empty cells is `NAN`.
- `IntColumn` contains `int` numbers. (This does not include `INF`, and `NAN`, which are of type `float` in Python.) The default value for empty cells is 0.
- `MultiDimensionalColumn` contains higher-dimensional `float` arrays. This allows you to mix higher-dimensional data, such as time series or images, with regular one-dimensional data. The default value for empty cells is `NAN`.
- `SeriesColumn` is identical to a two-dimensional `MultiDimensionalColumn`.

When you create a `DataMatrix`, you can indicate a default column type.

```python
# Create IntColumns by default
dm = DataMatrix(length=2, default_col_type=int)
dm.i = 1, 2  # This is an IntColumn
```

You can also explicitly indicate the column type when creating a new column. 

```python
dm.f = float  # This creates an empty (`NAN`-filled) FloatColumn
dm.i = int    # This creates an empty (0-filled) IntColumn
```

To create a `MultiDimensionalColumn` you need to import the column type and specify a shape:

```python
from datamatrix import MultiDimensionalColumn
dm.mdim_col = MultiDimensionalColumn(shape=(2, 3))
print(dm)
```

You can also specify named dimensions. For example, `('x', 'y')` creates a dimension of size 2 where index 0 can be referred to as 'x' and index 1 can be referred to as 'y':

```python
dm.mdim_col = MultiDimensionalColumn(shape=(('x', 'y'), 3))
```


### Column properties

Basic numerical properties, such as the mean, can be accessed directly. For this purpose, only numerical, non-`NAN` values are taken into account.


```python
dm = DataMatrix(length=3)
dm.col = 1, 2, 'not a number'
# Numeric descriptives
print('mean: %s' % dm.col.mean)  #  or dm.col[...]
print('median: %s' % dm.col.median)
print('standard deviation: %s' % dm.col.std)
print('sum: %s' % dm.col.sum)
print('min: %s' % dm.col.min)
print('max: %s' % dm.col.max)
# Other properties
print('unique values: %s' % dm.col.unique)
print('number of unique values: %s' % dm.col.count)
print('column name: %s' % dm.col.name)
```

The `shape` property indicates the number and sizes of the dimensions of the column. For regular columns, the shape is a tuple containing only the length of the datamatrix (the number of rows). For multidimensional columns, the shape is a tuple containing the length of the datamatrix and the shape of cells as specified through the `shape` keyword.

```python
print(dm.col.shape)
dm.mdim_col = MultiDimensionalColumn(shape=(2, 4))
print(dm.mdim_col.shape)
```

The `loaded` property indicates whether a column is currently stored in memory, or whether it is offloaded to disk. This is mainly relevant for multidimensional columns, which are [automatically offloaded to disk when memory runs low](%link:largedata%).

```python
print(dm.mdim_col.loaded)
```


## Assigning

### Assigning by index, multiple indices, or slice

You can assign a single value to one or more cells in various ways.

```python
dm = DataMatrix(length=4)
# Create a new columm
dm.col = ''
# By index: assign to a single cell (at row 1)
dm.col[1] = ':-)'
# By a tuple (or other iterable) of multiple indices:
# assign to cells at rows 0 and 2
dm.col[0, 2] = ':P'
# By slice: assign from row 1 until the end
dm.col[2:] = ':D'
print(dm)
```

You can also assign multiple values at once, provided that the to-be-assigned sequence is of the correct length.

```python
# Assign to the full column
dm.col = 1, 2, 3, 4
# Assign to two cells
dm.col[0, 2] = 'a', 'b'
print(dm)
```


### Assigning to cells that match a selection criterion

As will be described in more detail later on, comparing a column to a value gives a new `DataMatrix` that contains only the matching rows. This subsetted `DataMatrix` can in turn be used to assign to the matching rows of the original `DataMatrix`. This sounds a bit abstract but is very easy in practice:

```python
dm.col[1:] = ':D'
dm.is_happy = 'no'
dm.is_happy[dm.col == ':D'] = 'yes'
print(dm)
```

### Assigning to multidimensional columns

Assigning to multidimensional columns works much the same as assigning to regular columns. The main differences are that there are multiple dimensions, and that dimensions can be named.


```python
dm = DataMatrix(length=2)
dm.mdim_col = MultiDimensionalColumn(shape=(('x', 'y'), 3))
# Set all values to a single value
dm.mdim_col = 1
# Set all last dimensions to a single array of shape 3
dm.mdim_col = [ 1,  2,  3]
# Set all rows to a single array of shape (2, 3)
dm.mdim_col = [[ 1,  2,  3],
               [ 4,  5,  6]]
# Set the column to an array of shape (2, 3, 3)
dm.mdim_col = [[[ 1,  2,  3],
                [ 4,  5,  6]],
               [[ 7,  8,  9],
                [10, 11, 12]]]
```

To assign to dimensions by name:

```python
dm.mdim_col[:, 'x'] = 1, 2, 3  # identical to assigning to dm.mdim_col[:, 0]
dm.mdim_col[:, 'y'] = 4, 5, 6  # identical to assigning to dm.mdim_col[:, 1]
```

*Pro-tip:* When assigning an array-like object to a multidimensional column, the shape of the to-be-assigned array needs to match the final part of the shape of the column. This means that you can assign a (2, 3) array to a (2, 2, 3) column in which case all rows (the first dimension) are set to the array. shape However, you *cannot* assign a (2, 2) array to a (2, 2, 3) column.

## Accessing

### Accessing by index, multiple indices, or slice

```python
dm = DataMatrix(length=4)
# Create a new column
dm.col = 'a', 'b', 'c', 'd'
# By index: select a single cell (at row 1).
print(dm.col[1])
# By a tuple (or other iterable) of multiple indices:
# select cells at rows 0 and 2. This gives a new column.
print(dm.col[0, 2])
# By slice: assign from row 1 until the end. This gives a new column.
print(dm.col[2:])
```


### Accessing and averaging (ellipsis averaging) multidimensional columns

Accessing multidimensional columns works much the same as accessing regular columns. The main differences are that there are multiple dimensions, and that dimensions can be named.

```python
dm = DataMatrix(length=2)
dm.mdim_col = MultiDimensionalColumn(shape=(('x', 'y'), 3))
dm.mdim_col = [[[ 1,  2,  3],
                [ 4,  5,  6]],
               [[ 7,  8,  9],
                [10, 11, 12]]]
# From all rows, get index 1 (named 'y') from the second dimension and index 2 from the third dimension.
print(dm.mdim_col[:, 'y', 2])
```

You can select the average of a column using the ellipsis (`...`) index. For regular columns, this is indentical to accessing the `mean` property:

```python
dm.col = 1, 2
print(dm.col[...])  # identical to `dm.col.mean`
```

Ellipsis averaging (`...`) is especially useful when working with multidimensional data, in which case it allows you to average over specific dimensions. As long as you don't average over the first dimension, which corresponds to the rows of the `DataMatrix`, the result is a new column.


```python

# Averaging gover the third dimension gives a column of shape (2, 2)
dm.avg3 = dm.mdim_col[:, :, ...]
# Average over the second dimension gives a colum of shape (2, 3)
dm.avg2 = dm.mdim_col[:, ...]
# Averaging over the second and third dimensions gives a `FloatColumn`.
dm.avg23 = dm.mdim_col[:, ..., ...]
print(dm)
```

When averaging over the first dimension, which corresponds to the rows of the `DataMatrix`, the result is either an array or (if all dimensions are averaged) a float:

```python
# Averaging over the rows gives an array of shape (2, 3)
print(dm.mdim_col[...])
# Averaging over all dimensions gives a float
print(dm.mdim_col[..., ..., ...])
```


## Selecting

### Selecting by column values

You can select by directly comparing columns to values. This returns a new `DataMatrix` object with only the selected rows.


```python
dm = DataMatrix(length=10)
dm.col = range(10)
dm_subset = dm.col > 5
print(dm_subset)
```

### Selecting by multiple criteria with `|` (or), `&` (and), and `^` (xor)

You can select by multiple criteria using the `|` (or), `&` (and), and `^` (xor) operators (but not the actual words 'and' and 'or'). Note the parentheses, which are necessary because `|`, `&`, and `^` have priority over other operators.


```python
dm_subset = (dm.col < 1) | (dm.col > 8)
print(dm_subset)
```


```python
dm_subset = (dm.col > 1) & (dm.col < 8)
print(dm_subset)
```

### Selecting by multiple criteria by comparing to a set `{}`

If you want to check whether column values are identical to, or different from, a set of test values, you can compare the column to a `set` object. (This is considerably faster than comparing the column values to each of the test values separately, and then merging the result using `&` or `|`.)


```python
dm_subset = dm.col == {1, 3, 5, 7}
print(dm_subset)
```

### Selecting (filtering) with a function or lambda expression

You can also use a function or `lambda` expression to select column values. The function must take a single argument and its return value determines whether the column value is selected. This is analogous to the classic `filter()` function.


```python
dm_subset = dm.col == (lambda x: x % 2)
print(dm_subset)
```

### Selecting values that match another column (or sequence)

You can also select by comparing a column to a sequence, in which case a row-by-row comparison is done. This requires that the sequence has the same length as the column, is not a `set` object (because `set` objects are treated as described above).


```python
dm = DataMatrix(length=4)
dm.col = 'a', 'b', 'c', 'd'
dm_subset = dm.col == ['a', 'b', 'x', 'y']
print(dm_subset)
```

### Selecting values by type

When a column contains values of different types, you can also select values by type:


```python
dm = DataMatrix(length=4)
dm.col = 'a', 1, 'c', 2
dm_subset = dm.col == int
print(dm_subset)
```

### Getting indices for rows that match selection criteria ('where')

You can get the indices for rows that match certain selection criteria by slicing a `DataMatrix` with a subset of itself. This is similar to the `numpy.where()` function.

```python
dm = DataMatrix(length=4)
dm.col = 1, 2, 3, 4
indices = dm[(dm.col > 1) & (dm.col < 4)]
print(indices)
```

### Selecting a subset of columns

You can select a subset of columns by passing the columns as an index to `dm[]`. Columns can be specified by name ('col3') or by object (`dm.col1`).

```python
dm = DataMatrix(length=4)
dm.col1 = '☺'
dm.col2 = 'a'
dm.col3 = 1
dm_subset = dm[dm.col1, 'col3']
print(dm_subset)
```


## Element-wise column operations

### Multiplication, addition, etc.

You can apply basic mathematical operations on all cells in a column simultaneously. Cells with non-numeric values are ignored, except by the `+` operator, which then results in concatenation.

```python
dm = DataMatrix(length=3)
dm.col = 0, 'a', 20
dm.col2 = dm.col * .5
dm.col3 = dm.col + 10
dm.col4 = dm.col - 10
dm.col5 = dm.col / 50
print(dm)
```

### Applying (mapping) a function or lambda expression

You can apply a function or `lambda` expression to all cells in a column simultaneously with the `@` operator. This analogous to the classic `map()` function.


```python
dm = DataMatrix(length=3)
dm.col = 0, 1, 2
dm.col2 = dm.col @ (lambda x: x*2)
print(dm)
```

## Iterating over rows, columns, and cells (for loops)

By iterating directly over a `DataMatrix` object, you get successive `Row` objects. From a `Row` object, you can directly access cells.


```python
dm.col = 'a', 'b', 'c'
for row in dm:
    print(row)
    print(row.col)
```

By iterating over `DataMatrix.columns`, you get successive `(column_name, column)` tuples.


```python
for colname, col in dm.columns:
    print('%s = %s' % (colname, col))
```

By iterating over a column, you get successive cells:


```python
for cell in dm.col:
    print(cell)
```

By iterating over a `Row` object, you get (`column_name, cell`) tuples:


```python
row = dm[0] # Get the first row
for colname, cell in row:
    print('%s = %s' % (colname, cell))
```

The `column_names` property gives a sorted list of all column names (without the corresponding column objects):


```python
print(dm.column_names)
```


## Miscellanous notes

### Type conversion and character encoding

For `MixedColumn`:

- The strings 'nan', 'inf', and '-inf' are converted to the corresponding `float` values (`NAN`, `INF`, and `-INF`).
- Byte-string values (`bytes`) are automatically converted to `str` assuming `utf-8` encoding.
- Trying to assign an unsupported type results in a `TypeError`.
- The string 'None' is *not* converted to the type `None`.


For `FloatColumn`:

- The strings 'nan', 'inf', and '-inf' are converted to the corresponding `float` values (`NAN`, `INF`, and `-INF`).
- Unsupported types are converted to `NAN`. A warning is shown.


For `IntColumn`:

- Trying to assign non-`int` values results in a `TypeError`.


### NAN and INF values

You have to take special care when working with `nan` data. In general, `nan` is not equal to anything else, not even to itself: `nan != nan`. You can see this behavior when selecting data from a `FloatColumn` with `nan` values in it.

```python
from datamatrix import DataMatrix, FloatColumn, NAN
dm = DataMatrix(length=3)
dm.f = FloatColumn
dm.f = 0, NAN, 1
dm = dm.f == [0, NAN, 1]
print(dm)
```

However, for convenience, you can select all `nan` values by comparing a `FloatColumn` to a single `nan` value:

```python
dm = DataMatrix(length=3)
dm.f = FloatColumn
dm.f = 0, NAN, 1
print(dm.f == NAN)
print('NaN values')
print('Non-NaN values')
print(dm.f != NAN)
```
