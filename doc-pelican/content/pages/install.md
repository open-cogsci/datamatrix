title: Install

## Dependencies

`DataMatrix` runs on Python 2 and 3, and requires only the Python standard library. That is, you can use it without installing any additional Python packages.

The following packages are required for extra functionality:

- `fastnumbers` for improved performance
- `numpy` and `scipy` for using the `FloatColumn`, `IntColumn`, and `SeriesColumn` objects
- `prettytable` for creating a text representation of a DataMatrix (e.g. to print it out)
- `openpyxl` for reading and writing `.xlsx` files

## Installation

The easiest way to install `DataMatrix` is through PyPi (`pip install`):

~~~
pip install python-datamatrix
~~~

Optional dependencies:

~~~
pip install fastnumbers numpy scipy prettytable openpyxl
~~~

## Source code

- <https://github.com/smathot/python-datamatrix>
