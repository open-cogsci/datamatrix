# -*- coding: utf-8 -*-

"""
This file is part of datamatrix.

datamatrix is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

datamatrix is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with datamatrix.  If not, see <http://www.gnu.org/licenses/>.
"""

from datamatrix import DataMatrix, MixedColumn, FloatColumn, IntColumn

# Create an empty DataMatrix with 5 rows and using MixedColumn as default column
# type.
dm = DataMatrix()
dm.length = 5
dm.default_col_type = MixedColumn
# Create a column and set it in various ways
dm.col = 0 # Set all to 0. This automatically creates a MixedColumn.
dm.col = [0, 1, 2, 3, 4] # Set values by list
dm.col[2] = 'text' # Set index 2 to a text string
dm.col[:] = 2 # Set all values to 2

print(dm[0]) # Get a row (DataMatrixRow)
print(dm.col) # Get a column
print(dm[1:3]) # Get a slice
print(dm[0, 4, 2]) # Get rows by index

# Iterate over rows
for row in dm:
	print(row)
# Iterate over columns
for name, col in dm.columns:
	print('%s = %s' % (name, col))
# Iterate over cells within a column
for value in dm.col:
	print(value)
# Iterate over values within a row
for name, value in dm[2]:
	print('%s = %s' % (name, value))

# Selecting rows. Set operations can be used to select by multiple criteria.
print('col > 3')
print(dm.col > 3)
print('col > 0 and col < 4')
print((dm.col > 0) & (dm.col < 4))
print('col = 0 or col = 4')
print((dm.col == 0) | (dm.col == 4))
print('col > 0 xor col < 4')
print((dm.col > 0) ^ (dm.col < 4))

# Concatenate two datamatrices
dm2 = DataMatrix(length=5)
dm2.col = 0
dm2.col2 = 'test'
dm3 = dm << dm2
print(dm3)

# Print summary statistics
print(dm)
print('Mean = %f' % dm.col.mean)
print('Median = %f' % dm.col.median)
print('Standard deviation = %f' % dm.col.std)

# Numeric operations
dm.col *= 3
dm.col += range(5)
dm.col += 'a'
print(dm)
