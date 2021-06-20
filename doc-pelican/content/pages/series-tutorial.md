title: Working with series


[TOC]


## What is a series?

A series in DataMatrix is a type of column, a `SeriesColumn` in which each cell is itself a series of values. 


## Mixing two- and three-dimensional data

With column-based, or tabular, data every cell is defined by two coordinates: the column name, and the row number; that is, column-based data is two dimensional. But for many kinds of data, two dimensions is not enough.

To illustrate this, let's imagine that you want to store the population of cities over a period of three years. You could do this by simply adding a column for every year, `population2008`, `population2009`, `population2010`:


```python
from datamatrix import DataMatrix

# Not very elegant!
dm = DataMatrix(length=2)
dm.city = 'Marseille', 'Lyon'
dm.population2010 = 850726, 484344
dm.population2009 = 850602, 479803
dm.population2008 = 851420, 474946
print(dm)
```

In this example, this approach is feasible, because there are only three years, so you need only three columns. But imagine that you want to store the year-by-year population over several centuries. You would then end up with hundreds of columns! Not impossible, but not very elegant either.

It would be much more elegant if you could have a single column for the population, and then give this column a third dimension (a *depth*) so that it can store the population over time. And that's where the `SeriesColumn` comes in.


```python
from datamatrix import DataMatrix, SeriesColumn

# Pretty elegant, right?
dm = DataMatrix(length=2)
dm.city = 'Marseille', 'Lyon'
dm.population = SeriesColumn(depth=3)
dm.population[0] = 850726, 850602, 851420 # Marseille
dm.population[1] = 484344, 479803, 474946 # Lyon
dm.year = SeriesColumn(depth=3)
dm.year = 2010, 2009, 2008
print(dm)
```


## Basic properties of series

`SeriesColumn`s have the same properties as regular columns: `mean`, `median`, `std`, `sum`, `min`, and `max`. But where these properties are single values for regular columns, they are iterators for `SeriesColumn`s (a one-dimensional numpy array, to be exact). 


```python
print(dm.population.mean)
```


## Indexing

### Accessing

The first dimension of a `SeriesColumn` refers to the row. So to get the population of Marseille (row 0) over time, you can do:


```python
print(dm.population[0])
```

The second dimension refers to the depth. So to get the population of both Marseille and Lyon in 2009, you can do:


```python
print(dm.population[:,1])
```

### Assigning

You can assign to a `SeriesColumn` as you would to a 2D numpy array:


```python
dm = DataMatrix(length=2)
dm.s = SeriesColumn(depth=3)
dm.s[0,0] = 1
dm.s[1:,1:] = 2
print(dm)
```

If you want to set all cells at once, you can directly assign a single value:


```python
dm.s = 10
print(dm)
```

If you want to set all rows at once, you can directly assign a sequence with a length that is equal to the depth of the series:


```python
dm.s = 100, 200, 300 
# Equal to: dm.s[:,:] = 100, 200, 300
print(dm) 
```

If you want to set all columns at once, you can directly assing a sequence with a length that is equal to the length of the DataMatrix:


```python
dm.s = 1000, 2000
# Equal to: dm.s[:,:] = 1000, 2000
print(dm)
```
