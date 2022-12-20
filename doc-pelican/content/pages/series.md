title: datamatrix.series


This module is typically imported as `srs` for brevity:

```python
from datamatrix import series as srs
```



[TOC]

## What are series?

A `SeriesColumn` is a column with a depth; that is, each cell contains multiple values. Data of this kind is very common. For example, imagine a psychology experiment in which participants see positive or negative pictures, while their brain activity is recorded using electroencephalography (EEG). Here, picture type (positive or negative) is a single value that could be stored in a normal table. But EEG activity is a continuous signal, and could be stored as `SeriesColumn`.

A `SeriesColumn` is identical to a `MultiDimensionalColumn` with a shape of length 1. Therefore, all functions in the [`multidimensional` module](%url:multidimensional) can also be applied to `SeriesColumn`s.

For more information, see:

- <https://pythontutorials.eu/numerical/time-series/>

%-- include: include/api/series.md --%
