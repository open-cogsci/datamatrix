title: datamatrix.series

[TOC]

## What are series?

A `SeriesColumn` is a column with a depth. For example, imagine a table that combines the names of two cities with their populations during the past four years. Here, the names the cities are single values that fit into a normal table. But the population corresponds to a series of values for each city. This is where the `SeriesColumn` comes in.

__Example:__

%--
python: |
 from matplotlib import pyplot as plt
 from datamatrix import DataMatrix, SeriesColumn
 
 NR_CITIES = 2
 NR_YEARS = 4
 
 dm = DataMatrix(length=NR_CITIES)
 dm.city = 'Marseille', 'Lyon'
 # Create a series for the population
 dm.population = SeriesColumn(depth=NR_YEARS)
 dm.population[0] = 850726, 850602, 851420, 797491 # Marseille
 dm.population[1] = 484344, 479803, 474946, 445274 # Lyon
 # Create a series for the years that correspond to the populations
 dm.year = SeriesColumn(depth=NR_YEARS)
 dm.year.setallrows( [2010, 2009, 2008, 1999])
 
 print(dm)

 plt.clf()
 for row in dm:
     plt.plot(row.year, row.population, 'o-', label=row.city)
 plt.legend(loc='upper left')
 plt.xlabel('Year')
 plt.ylabel('Population')
 plt.xlim(1998, 2011)
 plt.ylim(400000, 1000000)
 plt.savefig('content/pages/img/series/series.png')
--%

%--
figure:
 source: series.png
 id: FigSeries.png
 caption: The populations of Marseille and Lyon over time.
--%

Data of this kind is very common. For example, imagine a psychology experiment in which participants see positive or negative pictures, while their brain activity is recorded using electroencephalography (EEG). Here, picture type (positive or negative) is a single value that could be stored in a normal table. But EEG activity is a continuous signal, and could be stored as `SeriesColumn`.

%-- include: include/api/series.md --%
