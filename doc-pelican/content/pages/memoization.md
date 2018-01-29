title: Memoization (caching)

[TOC]


## What is memoization?

[Memoization](https://en.wikipedia.org/wiki/Memoization) is a way to optimize code by storing the return values of functions called with a specific set of arguments. Memoization is a specific type of caching.


## When (not) to memoize?

Memoization is only valid for functions that are *referentially transparent*: functions that always return the same result for the same set of arguments, and that do not affect the state of the program.

Therefore, you should *not* memoize a function that returns random numbers, because it will end up returning the same set of random numbers over and over again. And you should also *not* memoize a function that depends on the state of the program, for example because it relies on the command-line arguments that were passed to a script.

But you *could* memoize a function that performs some time consuming operation that is always done in exactly the same way, such as a function that performs time-consuming operations on a large dataset.


## Examples

### Basic memoization

Memoization is done with the `memoize` decorator, which is part of [`datamatrix.functional`](%link:functional%). Let's take a time-consuming function that determines the highest prime number below a certain value, and measure the performance improvement that memoization gives us when we call the function twice with same argument.

%--
python: |
 import time
 from itertools import dropwhile
 from datamatrix import functional as fnc


 @fnc.memoize
 def prime_below(x):

 	"""Returns the highest prime that is lower than X."""

 	print('Calculating the highest prime number below %d' % x)
 	return next(
 		dropwhile(
 			lambda x: any(not x % i for i in range(x-1, 2, -1)),
 			range(x-1, 0, -1)
 			)
 		)


 t0 = time.time()
 prime_below(10000)
 t1 = time.time()
 prime_below(10000)
 t2 = time.time()

 print('Fresh: %.2f ms' % (1000*(t1-t0)))
 print('Memoized: %.2f ms' % (1000*(t2-t1)))
--%


### Chaining memoized functions and lazy evaluation

When you call a function, Python automatically evaluates the function arguments. This happens even if a function has been memoized. In some cases, this is undesirable because evaluating the arguments may be time-consuming in itself, for example because one of the arguments is a call to another time-consuming function.

Ideally, evaluation of the arguments occurs only when the memoized function actually needs to be executed. To approximate this behavior in Python, the `memoize` decorator accepts the `lazy` keyword. When `lazy=True` is specified, all callable objects that are passed to the memoized function are evaluated automatically, but *only* when the memoized function is actually executed.

%--
python: |
 @fnc.memoize(lazy=True)
 def prime_below(x):

 	print('Calculating the highest prime number below %d' % x)
 	return next(
 		dropwhile(
 			lambda x: any(not x % i for i in range(x-1, 2, -1)),
 			range(x-1, 0, -1)
 			)
 		)


 def thousand():

 	print('Returning a thousand!')
 	return 1000


 print(prime_below(thousand))
 print(prime_below(thousand))
--%


A slightly more complicated situation arises when you want to pass arguments to a function that is itself passed as argument, without evaluating the function. To accomplish this, you can first bind the argument to the function using `functools.partial` and then pass the resulting partial function as an argument. Like so:

%--
python: |
 from functools import partial

 print(prime_below(partial(prime_below, 1000)))
 print(prime_below(partial(prime_below, 1000)))
--%

You can also implement this behavior with the `>>` operator, in which the resulting of one function call is fed into the next function call, etc. The result is a `chain` object that needs to be explicitly called. The `>>` only works
with lazy memoization.

%--
python: |
 chain = 1000 >> prime_below >> prime_below
 print(chain())
 print(chain())
--%


### Persistent memoization, memoization keys, and cache clearing

If you pass `persistent=True` to the `memoize` decorator, the cache will be written to disk, by default to a subfolder `.memoize` of the current working directory. The filename will correspond to the memoization key, which by default is derived from the function name and the arguments.

If you want to change the cache folder, you can either pass a `folder` keyword to the `memoize` decorator, or change the `memoize.folder` class property before applying the `memoize` decorator to any functions.

You can also specify a custom memoization key through the `key` keyword. If you specify a custom key, `memoize` will no longer distinguish between different arguments (and thus no longer be real `memoization`).

To re-execute a memoized function, you can clear the memoization cache by calling the `.clear()` method on the memoized function, as shown below. If memoization is persistent, this will clear all files in the cache folder. Otherwise, this will only clear the in-memory cache.


%--
python: |
 @fnc.memoize(persistent=True, key='custom-key')
 def prime_below(x):

 	print('Calculating the highest prime number below %d' % x)
 	return next(
 		dropwhile(
 			lambda x: any(not x % i for i in range(x-1, 2, -1)),
 			range(x-1, 0, -1)
 			)
 		)


 print(prime_below(1000))
 print(prime_below(1000))
 prime_below.clear() # Clear the cache
 print(prime_below(1000))
--%


## Limitations

Memoization only works for functions with:

- Arguments and keywords that:
	- Can be serialized by `json_tricks`, which includes simple data types, DataMatrix objects, and numpy array; or
	- Are callable, which includes regular functions, `lambda` expressions, `partial` objects, and `memoize` objects.
- Return values that can be pickled.
