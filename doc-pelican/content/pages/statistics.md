title: Statistics

[TOC]

## Compatibility with Pandas and StatsModels

`statsmodels` is a Python library for statistics. It relies heavily on `pandas.DataFrame` objects. However, it is easy to use these two libraries in combination with `DatMatrix` objects.

- <http://www.statsmodels.org/>
- <https://pandas.pydata.org/>


## Creating a pivot table

A pivot table is a table that contains aggregate data that is grouped in a certain way. For example, the example data below[^data] is from a behavioral experiment in which participants, coded by `subject_nr`, pressed a key on each trial. The key-press response time is stored as `RT_search`. The experiment had different experimental conditions: `condition` and `load`. A common way to summarize this data is to put each participant in a different row, and each condition in a different column. The cells then contain the mean response time for a specific participant in a specific condition. That's a pivot table!

You can create a pivot table with `pandas.pivot_table()`. This function accepts a `pandas.DataFrame` as first argument, and also returns a `pandas.DataFrame`. By wrapping this function with the `datamatrix.convert.wrap_pandas()` decorator, you can modify the function so that it works with `DataMatrix` objects instead.

- <https://pandas.pydata.org/pandas-docs/stable/generated/pandas.pivot_table.html>
- <%url:convert%>

Let's see how this works:

```python
from datamatrix import io, convert as cnv
from pandas import pivot_table
pivot_table = cnv.wrap_pandas(pivot_table)  # Make compatible with DataMatrix

dm = io.readtxt('data/fratescu-replication-data-exp1.csv')
pm = pivot_table(
    dm,
    values='RT_search',
    index='subject_nr',
    columns=['condition', 'load']
)
print(pm)
```


## Running a repeated measures ANOVA

A repeated measures ANOVA is a type of statistical analysis for within-subject designs, such as the one used for this tutorial. You typically run a repeated measures ANOVA on a dataset where one person contributes multiple data points.

You can perform a repeated measures ANVOA with `statsmodels.stats.anova.AnovaRM`.

- <http://www.statsmodels.org/stable/generated/statsmodels.stats.anova.AnovaRM.html>


Let's see how this works:

```python
from statsmodels.stats.anova import AnovaRM
AnovaRM = cnv.wrap_pandas(AnovaRM)  # Make compatible with DataMatrix

aov = AnovaRM(
    dm,
    depvar='RT_search',
    subject='subject_nr',
    within=['condition', 'load'],
    aggregate_func='mean'
)
print(aov.fit())
```


[^data]: The [example data]((/data/fratescu-replication-data-exp1.csv)) is adapted from [Frătescu et al. (2018)](https://doi.org/10.1101/474932), Experiment 1.
