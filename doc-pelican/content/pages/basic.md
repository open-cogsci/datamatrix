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


## Basic operations

### Creating a DataMatrix

Create a new `DataMatrix` object, and add a column (named `col`). By default, the column is of the `MixedColumn` type, which can store numeric and string data.


```python
import sys
from datamatrix import DataMatrix, __version__
dm = DataMatrix(length=2)
dm.col = ':-)'
print(
    'Examples generated with DataMatrix v{} on Python {}\n'.format(
        __version__,
        sys.version
    )
)
print(dm)
```

You can change the length of the `DataMatrix` later on. If you reduce the length, data will be lost. If you increase the length, empty cells will be added.


```python
dm.length = 3
```

### Concatenating two DataMatrix objects

You can concatenate two `DataMatrix` objects using the `<<` operator. Matching columns will be combined. (Note that row 2 is empty. This is because we have increased the length of `dm` in the previous step, causing an empty row to be added.)


```python
dm2 = DataMatrix(length=2)
dm2.col = ';-)'
dm2.col2 = 10, 20
dm3 = dm << dm2
print(dm3)
```


### Creating columns

You can change all cells in column to a single value. This creates a new column if it doesn't exist yet.


```python
dm.col = 'Another value'
print(dm)
```

You can change all cells in a column based on a sequence. This creates a new column if it doesn't exist yet. This sequence must have the same length as the column (3 in this case).


```python
dm.col = 1, 2, 3
print(dm)
```

If you do not know the name of a column, for example because it is defined by a variable, you can also refer to columns as though they are items of a `dict`. However, this is *not* recommended, because it makes it less clear whether you are referring to column or a row.


```python
dm['col'] = 'X'
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

### Slicing and assigning to column cells

#### Assign to one cell


```python
dm.col[1] = ':-)'
print(dm)
```

#### Assign to multiple cells

This changes row 0 and 2. It is not a slice!


```python
dm.col[0,2] = ':P'
print(dm)
```

#### Assign to a slice of cells


```python
dm.col[1:] = ':D'
print(dm)
```

#### Assign to cells that match a selection criterion


```python
dm.col[1:] = ':D'
dm.is_happy = 'no'
dm.is_happy[dm.col == ':D'] = 'yes'
print(dm)
```

### Column properties

Basic numeric properties, such as the mean, can be accessed directly. Only numeric values are taken into account.


```python
dm.col = 1, 2, 'not a number'
# Numeric descriptives
print('mean: %s' % dm.col.mean)
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

### Iterating over rows, columns, and cells

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


### Selecting data

#### Comparing a column to a value

You can select by directly comparing columns to values. This returns a new `DataMatrix` object with only the selected rows.


```python
dm = DataMatrix(length=10)
dm.col = range(10)
dm_subset = dm.col > 5
print(dm_subset)
```

#### Selecting by multiple criteria with `|` (or), `&` (and), and `^` (xor)

You can select by multiple criteria using the `|` (or), `&` (and), and `^` (xor) operators (but not the actual words 'and' and 'or'). Note the parentheses, which are necessary because `|`, `&`, and `^` have priority over other operators.


```python
dm_subset = (dm.col < 1) | (dm.col > 8)
print(dm_subset)
```


```python
dm_subset = (dm.col > 1) & (dm.col < 8)
print(dm_subset)
```

#### Selecting by multiple criteria by comparing to a set `{}`

If you want to check whether column values are identical to, or different from, a set of test values, you can compare the column to a `set` object. (This is considerably faster than comparing the column values to each of the test values separately, and then merging the result using `&` or `|`.)


```python
dm_subset = dm.col == {1, 3, 5, 7}
print(dm_subset)
```

#### Selecting with a function or lambda expression

You can also use a function or `lambda` expression to select column values. The function must take a single argument and its return value determines whether the column value is selected. This is analogous to the classic `filter()` function.


```python
dm_subset = dm.col == (lambda x: x % 2)
print(dm_subset)
```

#### Selecting values that match another column (or sequence)

You can also select by comparing a column to a sequence, in which case a row-by-row comparison is done. This requires that the sequence has the same length as the column, is not a `set` object (because `set` objects are treated as described above).


```python
dm = DataMatrix(length=4)
dm.col = 'a', 'b', 'c', 'd'
dm_subset = dm.col == ['a', 'b', 'x', 'y']
print(dm_subset)
```

When a column contains values of different types, you can also select values by type: (Note: On Python 2, all `str` values are automatically decoded to `unicode`, so you'd need to compare the column to `unicode` to extract `str` values.)


```python
dm = DataMatrix(length=4)
dm.col = 'a', 1, 'c', 2
dm_subset = dm.col == int
print(dm_subset)
```

#### Getting indices for rows that match selection criteria ('where')

You can get the indices for rows that match certain selection criteria by slicing a `DataMatrix` with a subset of itself. This is similar to the `numpy.where()` function.

```python
dm = DataMatrix(length=4)
dm.col = 1, 2, 3, 4
print(dm[(dm.col > 1) & (dm.col < 4)])
```

### Element-wise column operations

#### Multiplication, addition, etc.

You can apply basic mathematical operations on all cells in a column simultaneously. Cells with non-numeric values are ignored, except by the `+` operator, which then results in concatenation.


```python
dm = DataMatrix(length=3)
dm.col = 0, 'a', 20
dm.col2 = dm.col*.5
dm.col3 = dm.col+10
dm.col4 = dm.col-10
dm.col5 = dm.col/50
print(dm)
```

#### Applying a function or lambda expression

<div class="alert alert-warning">
The <code>@</code> operator is only available in Python 3.5 and later.
</div>

You can apply a function or `lambda` expression to all cells in a column simultaneously with the `@` operator.


```python
dm = DataMatrix(length=3)
dm.col = 0, 1, 2
dm.col2 = dm.col @ (lambda x: x*2)
print(dm)
```


## Column types

When you create a `DataMatrix`, you can indicate a default column type. If you do not specify a default column type, a `MixedColumn` is used by default.

```python
from datamatrix import DataMatrix, IntColumn
dm = DataMatrix(length=2, default_col_type=IntColumn)
dm.i = 1, 2 # This is an IntColumn
```

You can also explicitly indicate the column type when creating a new column:

```python
from datamatrix import FloatColumn
dm.f = FloatColumn
```

### MixedColumn (default)

A `MixedColumn` contains text (`unicode` in Python 2, `str` in Python 3), `int`, `float`, or `None`.

Important notes:

- `utf-8` encoding is assumed for byte strings
- String with numeric values, including `NAN` and `INF`, are automatically converted to the most appropriate type
- The string 'None' is *not* converted to the type `None`
- Trying to assign a non-supported type results in a `TypeError`

```python
from datamatrix import DataMatrix, NAN, INF
dm = DataMatrix(length=12)
dm.datatype = (
    'int',
    'int (converted)',
    'float',
    'float (converted)',
    'None',
    'str',
    'float',
    'float (converted)',
    'float',
    'float (converted)',
    'float',
    'float (converted)',
)
dm.value = (
    1,
    '1',
    1.2,
    '1.2',
    None,
    'None',
    NAN,
    'nan',
    INF,
    'inf',
    -INF,
    '-inf'
)
print(dm)
```


### IntColumn (requires numpy)

The `IntColumn` contains only `int` values. As of 0.14, the easiest way to create a `FloatColumn` column is to assign `int` to a new column name.

Important notes:

- Trying to assign a value that cannot be converted to an `int` results in a `TypeError`
- Float values will be rounded down (i.e. the decimals will be lost)
- `NAN` or `INF` values are not supported because these are `float`


```python
from datamatrix import DataMatrix
dm = DataMatrix(length=2)
dm.i = int
dm.i = 1, 2
print(dm)
```

If you insert non-`int` values, they are automatically converted to `int` if possible. Decimals are discarded (i.e. values are floored, not rounded):


```python
dm.i = '3', 4.7
print(dm)
```

If you insert values that cannot converted to `int`, a `TypeError` is raised:


```python
try:
    dm.i = 'x'
except TypeError as e:
    print(repr(e))
```


### FloatColumn (requires numpy)

The `FloatColumn` contains `float`, `nan`, and `inf` values. As of 0.14, the easiest way to create a `FloatColumn` column is to assign `float` to a new column name.

Important notes:

- Values that are accepted by a `MixedColumn` but cannot be converted to a numeric value become `NAN`. Examples are non-numeric strings or `None`.
- Trying to assign a non-supported type results in a `TypeError`



```python
import numpy as np
from datamatrix import DataMatrix, FloatColumn
dm = DataMatrix(length=3)
dm.f = float
dm.f = 1, np.nan, np.inf
print(dm)
```

If you insert other values, they are automatically converted if possible.


```python
dm.f = '3.3', 'inf', 'nan'
print(dm)
```

If you insert values that cannot be converted to `float`, they become `nan`.


```python
dm.f = 'x'
print(dm)
```


<div class="alert alert-warning">
Note: Careful when working with <code>nan</code> data!
</div>

You have to take special care when working with `nan` data. In general, `nan` is not equal to anything else, not even to itself: `nan != nan`. You can see this behavior when selecting data from a `FloatColumn` with `nan` values in it.

```python
from datamatrix import DataMatrix, FloatColumn
dm = DataMatrix(length=3)
dm.f = FloatColumn
dm.f = 0, np.nan, 1
dm = dm.f == [0, np.nan, 1]
print(dm)
```

However, for convenience, you can select all `nan` values by comparing a `FloatColumn` to a single `nan` value:

```python
from datamatrix import DataMatrix, FloatColumn
dm = DataMatrix(length=3)
dm.f = FloatColumn
dm.f = 0, np.nan, 1
print('NaN values')
print(dm.f == np.nan)
print('Non-NaN values')
print(dm.f != np.nan)
```

### SeriesColumn: Working with continuous data (requires numpy)

The `SeriesColumn` is 2 dimensional; that is, each cell is by itself an array of values. Therefore, the `SeriesColumn` can be used to work with sets of continuous data, such as EEG or eye-position traces.

For more information about series, see:

- %link:series%

```python
import numpy as np
from matplotlib import pyplot as plt
from datamatrix import SeriesColumn

length = 10 # Number of traces
depth = 50 # Size of each trace

x = np.linspace(0, 2*np.pi, depth)
sinewave = np.sin(x)
noise = np.random.random(depth)*2-1

dm = DataMatrix(length=length)
dm.series = SeriesColumn(depth=depth)
dm.series[0] = noise
dm.series[1:].setallrows(sinewave)
dm.series[1:] *= np.linspace(-1, 1, 9)

plt.xlim(x.min(), x.max())
plt.plot(x, dm.series.plottable, color='green', linestyle=':')
y1 = dm.series.mean-dm.series.std
y2 = dm.series.mean+dm.series.std
plt.fill_between(x, y1, y2, alpha=.2, color='blue')
plt.plot(x, dm.series.mean, color='blue')
plt.show()
```

You can also create a `SeriesColumn` by assigning a 2D numpy array to a new column, where one of the dimensions matches the length of the DataMatrix. The other dimension is then assumed to be the depth of the `SeriesColumn`:

```python
dm = DataMatrix(length=3)
dm.random_noise = np.random.random((3, 10))
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
