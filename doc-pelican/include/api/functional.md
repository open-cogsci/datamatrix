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

<div class="FunctionDoc YAMLDoc" id="memoize" markdown="1">

## function __memoize__\(fnc=None, key=None, persistent=False, lazy=False, debug=False\)

A memoization decorator that stores the result of a function call, and
returns the stored value when the function is called again with the same
arguments. That is, memoization is a specific kind of caching that
improves performance for expensive function calls.

This decorator only works for arguments and return values
that can be serialized (i.e. arguments that you can pickle).

To clear memoization, either pass `~[function name]` as a command line
argument to a script, or pass `memoclear=True` as a keyword to the
memoized function (not to the decorator).

For a more detailed description, see:

- %link:memoization%

__Example:__

%--
python: |
 from datamatrix import functional as fnc

 @fnc.memoize
 def add(a, b):

        print('add(%d, %d)' % (a, b))
        return a + b

 three = add(1, 2) # Storing result in memory
 three = add(1, 2) # Re-using previous result
 three = add(1, 2, memoclear=True) # Clear cache!

 @fnc.memoize(persistent=True, key='persistent-add')
 def persistent_add(a, b):

        print('persistent_add(%d, %d)' % (a, b))
        return a + b

 three = persistent_add(1, 2) # Writing result to disk
 three = persistent_add(1, 2) # Re-using previous result
--%

__Keywords:__

- `fnc` -- A function to memoize.
	- Type: callable
	- Default: None
- `key` -- Indicates a key that identifies the results. If no key is provided, a key is generated based on the function name, and the arguments passed to the function. However, this requires the arguments to be serialized, which can take some time.
	- Type: str, None
	- Default: None
- `persistent` -- Indicates whether the result should be written to disk so that the result can be re-used when the script is run again. If set to `True`, the result is stored as a pickle in a `.memoize` subfolder of the working directory.
	- Type: bool
	- Default: False
- `lazy` -- If `True`, any callable that is passed onto the memoized function is automatically called, and the memoized function receives the return value instead of the function object. This allows for lazy evaluation.
	- Type: bool
	- Default: False
- `debug` -- If `True`, the memoized function returns a `(retval, memkey, source)` tuple, where `retval` is the function's return value, `memkey` is the key used for caching, and `source` is one of 'memory', 'disk', or 'function', indicating whether and how the return value was cached. This is mostly for debugging and testing.
	- Type: bool
	- Default: False

__Returns:__

A memoized version of fnc.

- Type: callable

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

