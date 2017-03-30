title: Basic use

Ultra-short cheat sheet:

~~~ .python
from datamatrix import DataMatrix
# Create a new DataMatrix
dm = DataMatrix(length=5)
# The first two rows
print(dm[:2])
# Create a new column and initialize it with the Fibonacci series
dm.fibonacci = 0, 1, 1, 2, 3 
# A simple selection (remove 0 and 2)
dm = (dm.fibonacci != 0) & (dm.fibonacci != 2)
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

Slightly longer cheat sheet:

[TOC]


## Basic operations

### Creating a DataMatrix

Create a new `DataMatrix` object, and add a column (named `col`). By default, the column is of the `MixedColumn` type, which can store numeric and string data.

%--
python: |
 from datamatrix import DataMatrix, __version__
 dm = DataMatrix(length=2)
 dm.col = ':-)'
 print('These examples were generated with DataMatrix v%s\n' % __version__)
 print(dm)
--%

You can change the length of the `DataMatrix` later on. If you reduce the length, data will be lost. If you increase the length, empty cells will be added.

%--
python: |
 dm.length = 3
--%

### Concatenating two DataMatrix objects

You can concatenate two `DataMatrix` objects using the `<<` operator. Matching columns will be combined. (Note that row 2 is empty. This is because we have increased the length of `dm` in the previous step, causing an empty row to be added.)

%--
python: |
 dm2 = DataMatrix(length=2)
 dm2.col = ';-)'
 dm2.col2 = 10, 20
 dm3 = dm << dm2
 print(dm3)
--%


### Creating columns

You can change all cells in column to a single value. This creates a new column if it doesn't exist yet.

%--
python: |
 dm.col = 'Another value'
 print(dm)
--%

You can change all cells in a column based on a sequence. This creates a new column if it doesn't exist yet. This sequence must have the same length as the column (3 in this case).

%--
python: |
 dm.col = 1, 2, 3
 print(dm)
--%

If you do not know the name of a column, for example becaues it is defined by a variable, you can also refer to columns as though they are items of a `dict`. However, this is *not* recommended, because it makes it less clear whether you are referring to column or a row.

%--
python: |
 dm['col'] = 'X'
 print(dm)
--%


### Renaming columns

%--
python: |
 dm.rename('col', 'col2')
 print(dm)
--%

### Deleting columns

You can delete a column using the `del` keyword:

%--
python: |
 dm.col = 'x'
 del dm.col2
 print(dm)
--%

### Changing column cells (and slicing)

Change one cell:

%--
python: |
 dm.col[1] = ':-)'
 print(dm)
--%

Change multiple cells. (This changes row 0 and 2. It is not a slice!)

%--
python: |
 dm.col[0,2] = ':P'
 print(dm)
--%

Change a slice of cells:

%--
python: |
 dm.col[1:] = ':D'
 print(dm)
--%

### Column properties

Basic numeric properties, such as the mean, can be accessed directly. Only numeric values are taken into account.

%--
python: |
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
--%

### Iterating over rows, columns, and cells

By iterating directly over a `DataMatrix` object, you get successive `Row` objects. From a `Row` object, you can directly access cells.

%--
python: |
 dm.col = 'a', 'b', 'c'
 for row in dm:
 	print(row)
 	print(row.col)
--%

By iterating over `DataMatrix.columns`, you get successive `(column_name, column)` tuples.

%--
python: |
 for colname, col in dm.columns:
 	print('%s = %s' % (colname, col))
--%

By iterating over a column, you get successive cells:

%--
python: |
 for cell in dm.col:
  print(cell)
--%

By iterating over a `Row` object, you get (`column_name, cell`) tuples:

%--
python: |
 row = dm[0] # Get the first row
 for colname, cell in row:
 	print('%s = %s' % (colname, cell))
--%

The `column_names` property gives a sorted list of all column names (without the corresponding column objects):

%--
python: |
 print(dm.column_names)
--%


### Selecting data

You can select by directly comparing columns to values. This returns a new `DataMatrix` object with only the selected rows.

%--
python: |
 dm = DataMatrix(length=10)
 dm.col = range(10)
 dm_subset = dm.col > 5
 print(dm_subset)
--%

You can select by multiple criteria using the `|` (or), `&` (and), and `^` (xor) operators (but not the actual words 'and' and 'or'). Note the parentheses, which are necessary because `|` and `&` have priority over other operators.

%--
python: |
 dm_subset = (dm.col < 1) | (dm.col > 8)
 print(dm_subset)
--%

%--
python: |
 dm_subset = (dm.col > 1) & (dm.col < 8)
 print(dm_subset)
--%

You can also select by comparing to a series of values, in which case a row-by-row comparison is done:

%--
python: |
 dm = DataMatrix(length=4)
 dm.col = 'a', 'b', 'c', 'd'
 dm_subset = dm.col == ['a', 'b', 'x', 'y']
 print(dm_subset)
--%

When a column contains values of different types, you can also select values by type: (Note: On Python 2, all `str` values are automatically decoded to `unicode`, so you'd need to compare the column to `unicode` to extract `str` values.)

%--
python: |
 dm = DataMatrix(length=4)
 dm.col = 'a', 1, 'c', 2
 dm_subset = dm.col == int
 print(dm_subset)
--%


### Basic column operations (multiplication, addition, etc.)

You can apply basic mathematical operations on all cells in a column simultaneously. Cells with non-numeric values are ignored, except by the `+` operator, which then results in concatenation.

%--
python: |
 dm = DataMatrix(length=3)
 dm.col = 0, 'a', 20
 dm.col2 = dm.col*.5
 dm.col3 = dm.col+10
 dm.col4 = dm.col-10
 dm.col5 = dm.col/50
 print(dm)
--%


## Column types

When you create a `DataMatrix`, you can indicate a default column type. If you do not specify a default column type, a `MixedColumn` is used by default.

%--
python: |
 from datamatrix import DataMatrix, IntColumn
 dm = DataMatrix(length=2, default_col_type=IntColumn)
 dm.i = 1, 2 # This is an IntColumn
--%

You can also explicitly indicate the column type when creating a new column:

%--
python: |
 from datamatrix import FloatColumn
 dm.f = FloatColumn
--%

### MixedColumn (default)

A `MixedColumn` contains text (`unicode` in Python 2, `str` in Python 3), `int`, `float`, or `None`. Values are automatically converted to the most appropriate type, and a `utf-8` encoding is assumed where applicable.

%--
python: |
 from datamatrix import DataMatrix
 dm = DataMatrix(length=4)
 dm.datatype = 'int', 'float', 'float (converted)', 'None'
 dm.value = 1, 1.2, '1.2', None
 print(dm)
--%

### IntColumn (requires numpy)

The `IntColumn` contains only `int` values. It does not support `nan` values. 

%--
python: |
 from datamatrix import DataMatrix, IntColumn
 dm = DataMatrix(length=2)
 dm.i = IntColumn
 dm.i = 1, 2
 print(dm)
--%

If you insert non-`int` values, they are automatically converted to `int` if possible. Decimals are discarded (i.e. values are floored, not rounded):

%--
python: |
 dm.i = '3', 4.7
 print(dm)
--%

If you insert values that cannot converted to `int`, a `TypeError` is raised:

%--
python: |
 try:
 	dm.i = 'x'
 except TypeError as e:
 	print(repr(e))
--%


### FloatColumn (requires numpy)

The `FloatColumn` contains `float`, `nan`, and `inf` values.

%--
python: |
 import numpy as np
 from datamatrix import DataMatrix, FloatColumn
 dm = DataMatrix(length=3)
 dm.f = FloatColumn
 dm.f = 1, np.nan, np.inf
 print(dm)
--%

If you insert other values, they are automatically converted if possible.

%--
python: |
 dm.f = '3.3', 'inf', 'nan'
 print(dm)
--%

If you insert values that cannot be converted to `float`, they become `nan`.

%--
python: |
 dm.f = 'x'
 print(dm)
--%


<div class="alert alert-warning">
Note: Careful when working with <code>nan</code> data!
</div>

You have to take special care when working with `nan` data. In general, `nan` is not equal to anything else, not even to itself: `nan != nan`. You can see this behavior when selecting data from a `FloatColumn` with `nan` values in it.

%--
python: |
 from datamatrix import DataMatrix, FloatColumn
 dm = DataMatrix(length=3)
 dm.f = FloatColumn
 dm.f = 0, np.nan, 1
 dm = dm.f == [0, np.nan, 1]
 print(dm)
--%

However, for convenience, you can select all `nan` values by comparing a `FloatColumn` to a single `nan` value:

%--
python: |
 from datamatrix import DataMatrix, FloatColumn
 dm = DataMatrix(length=3)
 dm.f = FloatColumn
 dm.f = 0, np.nan, 1 
 print('NaN values')
 print(dm.f == np.nan)
 print('Non-NaN values')
 print(dm.f != np.nan)
--%

### SeriesColumn: Working with continuous data (requires numpy)

The `SeriesColumn` is 2 dimensional; that is, each cell is by itself an array of values. Therefore, the `SeriesColumn` can be used to work with sets of continuous data, such as EEG or eye-position traces.

For more information about series, see:

- %link:series%

%--
python: |
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
 plt.savefig('content/pages/img/basic/sinewave-series.png')
--%

%--
figure:
 source: sinewave-series.png
 id: FigSineWaveSeries
--%
