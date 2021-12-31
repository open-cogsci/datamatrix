<div class=" YAMLDoc" id="" markdown="1">

 

<div class="FunctionDoc YAMLDoc" id="curry" markdown="1">

## function __curry__\(fnc\)

A [currying](https://en.wikipedia.org/wiki/Currying) decorator that
turns a function with multiple arguments into a chain of partial
functions, each of which takes at least a single argument. The input
function may accept keywords, but the output function no longer does
(i.e. currying turns all keywords into positional arguments).

__Example:__

%--
python: |
 from datamatrix import functional as fnc

 @fnc.curry
 def add(a, b, c):

    return a + b + c

 print(add(1)(2)(3)) # Curried approach with single arguments
 print(add(1, 2)(3)) # Partly curried approach
 print(add(1)(2, 3)) # Partly curried approach
 print(add(1, 2, 3)) # Original approach multiple arguments
--%

__Arguments:__

- `fnc` -- A function to curry.
	- Type: callable

__Returns:__

A curried function that accepts at least the first argument, and returns a function that accepts the second argument, etc.

- Type: callable

</div>

<div class="FunctionDoc YAMLDoc" id="filter_" markdown="1">

## function __filter\___\(fnc, obj\)

Filters rows from a datamatrix or column based on filter function
(`fnc`).

If `obj` is a column, `fnc` should be a function that accepts a single
value. If `obj` is a datamatrix, `fnc` should be a function that
accepts a keyword `dict`, where column names are keys and cells are 
values. In both cases, `fnc` should return a `bool` indicating whether 
the row or value should be included.

*New in v0.8.0*: You can also directly compare a column with a function
or `lambda` expression. However, this is different from `filter_()` in
that it returns a datamatrix object and not a column.

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

*New in v0.8.0*: In Python 3.5 and later, you can also map a function
onto a column using the `@` operator:
`dm.new = dm.old @ (lambda i: i*2)`

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
    dm
 )
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

<div class="ClassDoc YAMLDoc" id="memoize" markdown="1">

## class __memoize__

*Requires json_tricks*

A memoization decorator that stores the result of a function call, and
returns the stored value when the function is called again with the
same arguments. That is, memoization is a specific kind of caching that
improves performance for expensive function calls.

This decorator only works for return values that can be pickled, and
arguments that can be serialized to `json`.

The memoized function becomes a callable object. To clear the
memoization cache, call the `.clear()` function on the memoized
function. The total size of all cached return values is available as 
the `.cache_size` property.

For a more detailed description, see:

- %link:memoization%

*Changed in v0.8.0*: You can no longer pass the `memoclear` keyword to
the memoized function. Use the `.clear()` function instead.

__Example:__

%--
python: |
 from datamatrix import functional as fnc

 @fnc.memoize
 def add(a, b):

    print('add(%d, %d)' % (a, b))
    return a + b

 three = add(1, 2)  # Storing result in memory
 three = add(1, 2)  # Re-using previous result
 add.clear()  # Clear cache, but only for the next call
 three = add(1, 2)  # Calculate again

 @fnc.memoize(persistent=True, key='persistent-add')
 def persistent_add(a, b):

    print('persistent_add(%d, %d)' % (a, b))
    return a + b

 three = persistent_add(1, 2)  # Writing result to disk
 three = persistent_add(1, 2)  # Re-using previous result
--%

</div>

<div class="FunctionDoc YAMLDoc" id="profile" markdown="1">

## function __profile__\(\*args, \*\*kwds\)

A context manager (`with`) for easy profiling, using cProfile. The
results of the profile are written to the file specified in the `path`
keyword (default=`u'profile'`), and the sorting order, as accepted by
`pstats.Stats.sort_stats()`, is specified in the the `sortby` keyword
(default=`u'cumulative'`).

__Example:__

%--
python: |
 from datamatrix import functional as fnc

 with fnc.profile(path=u'profile.txt', sortby=u'cumulative'):
     dm = DataMatrix(length=1000)
     dm.col = range(1000)
     dm.is_even = dm.col @ (lambda x: not x % 2)
--%

__Argument list:__

- `*args`: No description.

__Keyword dict:__

- `**kwds`: No description.

</div>

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

</div>

