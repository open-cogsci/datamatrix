# Python DataMatrix

*An intuitive, Pythonic way to work with tabular data.*

Sebastiaan Mathôt  <br />
Copyright 2015-2022  <br />
<https://pydatamatrix.eu/>

[![Build Status](https://travis-ci.com/open-cogsci/python-datamatrix.svg?branch=0.12)](https://travis-ci.com/open-cogsci/python-datamatrix)


## About

`DataMatrix` is an intuitive Python library for working with column-based and continuous data. It's a light-weight and easy-to-use alternative to `pandas`.

`datamatrix` is also one of the core libraries of [OpenSesame](https://osdoc.cogsci.nl/), a graphical experiment builder for the social sciences, and [Rapunzel](https://rapunzel.cogsci.nl/), a modern code editor for numerical computing with Python and R.


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
```


## Dependencies

- Python >= 3.7

Optional:

- `numpy` and `scipy` for using the `FloatColumn`, `IntColumn`, and `SeriesColumn` objects
- `prettytable` for creating a text representation of a DataMatrix (e.g. to print it out)
- `openpyxl` for reading and writing `.xlsx` files
- `fastnumbers` for improved performance

## Installation


### PyPi

~~~
pip install python-datamatrix
~~~


### Anaconda

~~~
conda install datamatrix -c conda-forge
~~~


### Ubuntu

~~~
sudo add-apt-repository ppa:smathot/cogscinl
sudo apt-get update
sudo apt install python3-datamatrix
~~~


## Documentation

See <https://pydatamatrix.eu/>


## License

`python-datamatrix` is licensed under the [GNU General Public License
v3](http://www.gnu.org/licenses/gpl-3.0.en.html).
