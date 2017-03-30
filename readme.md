# Python DataMatrix

*An intuitive, Pythonic way to work with tabular data.*

Sebastiaan Mathôt  <br />
Copyright 2015-2017  <br />
http://www.cogsci.nl/smathot

[![Build Status](https://travis-ci.org/smathot/python-datamatrix.svg?branch=master)](https://travis-ci.org/smathot/python-datamatrix)


## About

The `datamatrix` package provides a high-level, intuitive way to work with
tabular data, that is, datasets that consist of named columns and numbered rows.

The main advantage of `datamatrix` over similar libraries is the clean, Pythonic syntax, which makes your code easy to read and understand.


## Dependencies

Required:

- Python 2.7 or >= 3.4

Optional:

- `numpy` and `scipy` for using the `FloatColumn`, `IntColumn`, and `SeriesColumn` objects
- `prettytable` for creating a text representation of a DataMatrix (e.g. to print it out)
- `openpyxl` for reading and writing `.xlsx` files
- `fastnumbers` for improved performance

## Installation

~~~
pip install python-datamatrix
~~~


## Documentation

See <http://datamatrix.cogsci.nl/>


## License

`python-datamatrix` is licensed under the [GNU General Public License
v3](http://www.gnu.org/licenses/gpl-3.0.en.html).
