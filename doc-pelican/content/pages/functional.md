title: datamatrix.functional

A set of functions and decorators for [functional programming](https://docs.python.org/3.6/howto/functional.html).

[TOC]

## What is functional programming?

Functional programming is a style of programming that is characterized by the following:

- __Lack of statements__—In its purest form, functional programming does not use any statements. Statements are things like assignments (e.g. `x  = 1`), `for` loops, `if` statements, etc. Instead of statements, functional programs are chains of function calls.
- __Short functions__—In the purest form of functional programming, each function is a single expression. In Python, this can be implemented through `lambda` expressions.
- __Referential transparency__—Functions are referentially transparent when they always return the same result given the same set of arguments (i.e. they are *stateless*), and when they do not alter the state of the program (i.e. they have no *side effects*).

%-- include: include/api/functional.md --%
