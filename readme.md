
# Python DataMatrix

*An intuitive, Pythonic way to work with tabular data.*

Sebastiaan Mathôt
Copyright 2015-2016
http://www.cogsci.nl/smathot

## About

The `datamatrix` package provides a high-level, intuitive way to work with
tabular data, that is, datasets that consist of named columns and numbered rows.

### License

`python-datamatrix` is licensed under the [GNU General Public License
v3](http://www.gnu.org/licenses/gpl-3.0.en.html).

### Table of contents

- [Basic usage](#Basic-usage)
    - [Basic operations](#Basic-operations)
    - [Accessing rows, columns, and cells](#Accessing-rows,-columns,-and-cells)
    - [Iterating over rows, columns, and cells](#Iterating-over-rows,-columns
,-and-cells)
    - [Selecting data](#Selecting-data)

## Basic usage

### Basic operations

Create a new `DataMatrix` object, and add a column (named `col`). By default,
the column is of the `MixedColumn` type, which can store numeric and string
data.


    from datamatrix import DataMatrix
    dm = DataMatrix(length=3)
    dm.col = 1, 2, 3
    dm.col[1] = 'x'
    print(dm)

    +---+-----+
    | # | col |
    +---+-----+
    | 0 | 1.0 |
    | 1 |  x  |
    | 2 | 3.0 |
    +---+-----+


### Accessing rows, columns, and cells

Access a row by index.


    print(dm[0])

    +------+-------+
    | Name | Value |
    +------+-------+
    | col  |  1.0  |
    +------+-------+


Access a column by name. This returns a `BaseColumn` object.


    print(dm.col)

    col[1.0, 'x', 3.0]


Access by slice or by list of indices. This returns another `DataMatrix` object.


    print(dm[1:3])
    print(dm[0, 2])

    +---+-----+
    | # | col |
    +---+-----+
    | 1 |  x  |
    | 2 | 3.0 |
    +---+-----+
    +---+-----+
    | # | col |
    +---+-----+
    | 0 | 1.0 |
    | 2 | 3.0 |
    +---+-----+


Access a cell by column name and index.


    print(dm.col[0])

    1.0


### Iterating over rows, columns, and cells


    for row in dm:
        print(row)

    +------+-------+
    | Name | Value |
    +------+-------+
    | col  |  1.0  |
    +------+-------+
    +------+-------+
    | Name | Value |
    +------+-------+
    | col  |   x   |
    +------+-------+
    +------+-------+
    | Name | Value |
    +------+-------+
    | col  |  3.0  |
    +------+-------+



    for name, col in dm.columns:
        print('%s = %s' % (name, col))

    col = col[1.0, 'x', 3.0]



    for value in dm.col:
        print(value)

    1.0
    x
    3.0



    for name, value in dm[2]:
        print('%s = %s' % (name, value))

    col = 3.0


### Selecting data

You can select by directly comparing columns to values. This returns a new
`DataMatrix` object.


    print(dm.col > 1)
    dm_only_x = dm.col == 'x'
    print(dm_only_x)

    +---+-----+
    | # | col |
    +---+-----+
    | 2 | 3.0 |
    +---+-----+
    +---+-----+
    | # | col |
    +---+-----+
    | 1 |  x  |
    +---+-----+


Multiple criteria can used as follows (the round brackets are necessary):


    print((dm.col == 1) | (dm.col == 3))

    +---+-----+
    | # | col |
    +---+-----+
    | 0 | 1.0 |
    | 2 | 3.0 |
    +---+-----+

