# Python DataMatrix

*An intuitive, Pythonic way to work with tabular data.*

Sebastiaan Mathôt  <br />
Copyright 2015-2025  <br />
<https://pydatamatrix.eu/>


[![Publish to PyPi](https://github.com/open-cogsci/python-datamatrix/actions/workflows/publish-package.yaml/badge.svg)](https://github.com/open-cogsci/python-datamatrix/actions/workflows/publish-package.yaml)

[![Tests](https://github.com/open-cogsci/python-datamatrix/actions/workflows/run-unittests.yaml/badge.svg)](https://github.com/open-cogsci/python-datamatrix/actions/workflows/run-unittests.yaml)


## Contents

- [About](#about)
- [Features](#features)
- [Ultra-short cheat sheet](#ultra-short-cheat-sheet)
- [Documentation](#documentation)
- [Dependencies](#dependencies)
- [Installation](#installation)
- [License](#license)


## About

`DataMatrix` is an intuitive Python library for working with column-based, time-series, and multidimensional data. It's a light-weight and easy-to-use alternative to `pandas`.

`DataMatrix` is also one of the core libraries of [OpenSesame](https://osdoc.cogsci.nl/), a graphical experiment builder for the social sciences, and [Rapunzel](https://rapunzel.cogsci.nl/), a modern code editor for numerical computing with Python and R.


## Features

- [An intuitive syntax](https://pydatamatrix.eu/basic) that makes your code easy to read
- Mix tabular data with [time series](https://pydatamatrix.eu/series) and [multidimensional data](https://pydatamatrix.eu/multidimensional) in a single data structure
- Support for [large data](https://pydatamatrix.eu/largedata) by intelligent (and automatic) offloading of data to disk when memory is running low
- Advanced [memoization (caching)](https://pydatamatrix.eu//memoization)
- Requires only the Python standard libraries (but you can use `numpy` to improve performance)
- Compatible with your favorite data-science libraries:
    - `seaborn` and `matplotlib` for [plotting](https://pythontutorials.eu/numerical/plotting)
    - `scipy`, `statsmodels`, and `pingouin` for [statistics](https://pythontutorials.eu/numerical/statistics)
    - `mne` for analysis of electroencephalographic (EEG) and magnetoencephalographic (MEG) data
    - [Convert](https://pydatamatrix.eu/convert) to and from `pandas.DataFrame`
    - Looks pretty inside a Jupyter Notebook


## Ultra-short cheat sheet

```python
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
print(dm.fibonacci[...])
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
```


## Documentation

The basic documentation (including function and module references) is hosted on <https://pydatamatrix.eu/>. Additional tutorials can be found in the data-science course on <https://pythontutorials.eu/>.


## Dependencies

`DataMatrix` requires only the Python standard library. That is, you can use it without installing any additional Python packages (although the pip and conda packages install some of the optional dependencies by default). Python 3.7 and higher are supported.

The following packages are required for extra functionality:

- `numpy` and `scipy` for using the `FloatColumn`, `IntColumn`, `SeriesColumn`, `MultiDimensionalColumn` objects
- `pandas` for conversion to and from `pandas.DataFrame`
- `mne` for conversion to and from `mne.Epochs` and `mne.TFR`
- `fastnumbers` for improved performance
- `prettytable` for creating a text representation of a DataMatrix (e.g. to print it out)
- `openpyxl` for reading and writing `.xlsx` files
- `json_tricks` for hashing, serialization to and from `json`, and memoization (caching)
- `tomlkit` for reading configuration from `pyproject.toml`
- `psutil` for dynamic loading of large data


## Installation


### PyPi

~~~
pip install datamatrix
~~~


*Historical note:* The DataMatrix project used to correspond to another package of the same name, which was discontinued in 2010. If you want to install this package, you can do still do so by providing an explicit version (0.9 is the latest version of this package), as shown below. With thanks to [dennogumi.org](https://www.dennogumi.org/) for handing over this project's entry on PyPi, thus avoiding much unnecessary confusion!

~~~
# Doesn't install datamatrix but a previous package by the same name!
pip install datamatrix==0.9
~~~


### Anaconda

~~~
conda install datamatrix -c conda-forge
~~~


### Ubuntu

~~~
sudo add-apt-repository ppa:smathot/cogscinl  # for stable releases
sudo add-apt-repository ppa:smathot/rapunzel  # for development releases
sudo apt-get update
sudo apt install python3-datamatrix
~~~


## License

`python-datamatrix` is licensed under the [GNU General Public License
v3](http://www.gnu.org/licenses/gpl-3.0.en.html).
