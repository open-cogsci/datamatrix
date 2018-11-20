title: Plotting

[TOC]

## Compatibility with Seaborn and Matplotlib

`DataMatrix` objects can be passed to most `seaborn` plotting functions as if they are `pandas.DataFrame` objects. Below are some examples of common plot types.

The data used for these examples is taken from <https://osf.io/pwhkc/>. It is data from a behavioral experiment with a single dependent variable (`RT_search`) and two independent variables (`condition` and `load`).


```python
from datamatrix import io
from matplotlib import pyplot as plt
import seaborn as sns

dm = io.readtxt('data/fratescu-replication-data-exp1.csv')
sns.set(style='darkgrid')
```


## Point plot

Seaborn documentation:

- <https://seaborn.pydata.org/generated/seaborn.pointplot.html#seaborn.pointplot>

```python
plt.clf()
sns.pointplot(
    x='condition',
    y='RT_search',
    hue='load',
    order=['no', 'unrel', 'rel-mis', 'rel-match'],
    data=dm,
)
plt.xlabel('Distractor condition')
plt.ylabel('Reaction time (ms)')
plt.legend(title='Memory load')
plt.savefig('content/pages/img/plotting/pointplot.png')
```


%--
figure:
 source: pointplot.png
 id: FigPointPlot
--%


## Bar plot (sns.barplot)

Seaborn documentation:

- <https://seaborn.pydata.org/generated/seaborn.barplot.html#seaborn.barplot>

```python
plt.clf()
sns.barplot(
    x='condition',
    y='RT_search',
    hue='load',
    order=['no', 'unrel', 'rel-mis', 'rel-match'],
    data=dm,
)
plt.ylim(700, 900)
plt.xlabel('Distractor condition')
plt.ylabel('Reaction time (ms)')
plt.legend(title='Memory load')
plt.savefig('content/pages/img/plotting/barplot.png')
```

%--
figure:
 source: barplot.png
 id: FigBarPlot
--%


## Distribution plot (sns.distplot)

Seaborn documentation:

- <https://seaborn.pydata.org/generated/seaborn.distplot.html#seaborn.distplot>


```python
plt.clf()
sns.distplot(dm.RT_search)
plt.savefig('content/pages/img/plotting/distplot.png')
```

%--
figure:
 source: distplot.png
 id: FigDistPlot
--%
