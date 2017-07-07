title: Functional programming


## What is functional programming?

[Functional programming](https://docs.python.org/3.6/howto/functional.html) is a style of programming that is characterized by:

- __Short functions__ — In the purest form of functional programming, each function is a single expression. In Python, this can be implemented through `lambda` expressions.
- __Stateless functions__ — Functions that rely only on the arguments that were passed to them, and not on the state of the program. In other words, no use of global variables and object properties.
- __Functions without side effects__ — Functions that do not affect the state of the program. Phrased differently, function do not alter the objects that are passed to them, and only communicate with the outside world through their return values.

In addition to these basic characteristics, functional programming is generally characterized by secondary characteristics, such as:

- Heavy use of __iterators__ (such as `DataMatrix`!), and standard iterator functions such as `map` and `filter` shown below.
- Heavy use of __higher-order functions__, or functions that operate on other functions.

Functional programming is excellently suited for numerical computing. Many libraries for numeric computing, such as `numpy`, implicitly use a (mostly) functional style of programming.


## Functional programming with DataMatrix

Below is an example of how you can manipulate DataMatrix objects using purely functional programming. This example is exaggerated to make a point; good code is generally a sensible mixture of functional and procedural programming styles.

In general, all functions in `datamatrix.operations` and `datamatrix.series` are suitable for functional programming.

%--
python: |
 from datamatrix import DataMatrix, operations as ops

 # Initializes and returns a DataMatrix
 init_dm = lambda: \
 	ops.setcol(
 		ops.setcol(
 			DataMatrix(length=8), 'x', range(8)
 			),
 		'y1', [-1, 0, 1, 0, -1, 0, 1, 0]
 		)
 # Adds a column to a DataMatrix and returns it
 add_y2 = lambda dm: \
 	ops.setcol(
 		dm, 'y2', ops.map_(
 			lambda y: abs(y)*2, dm.y1
 			)
 		)
 # Filters rows from the DataMatrix
 filter_by_y1 = lambda dm: \
 	ops.filter_(
 		lambda y: y >= 0, dm.y1
 		).dm
 
 # A main function that does everything
 main = lambda: \
 	filter_by_y1(
 		add_y2(
 			init_dm()
 			)
 		)
 # Go!
 print(main())
--%
