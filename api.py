from datamatrix import DataMatrix, MixedColumn

# Create an empty DataMatrix with 5 rows and a MixedColumn
dm = DataMatrix(length=5)
dm.col = MixedColumn
dm.col = 0 # Set all to 0
dm.col = [0, 1, 2, 3, 4] # Set values by list
dm.col[2] = 'text' # Set index 2 to a text string
print(dm)

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

# Print summary statistics
print('Mean = %f' % dm.col.mean)
print('Median = %f' % dm.col.median)
print('Standard deviation = %f' % dm.col.std)

# Select rows
print(dm.col > 3)
print(dm.col == 0)
print((dm.col > 3) | (dm.col == 0))

# Concatenate two datamatrices
dm2 = DataMatrix(length=5)
dm2.col = MixedColumn
dm2.col = 0
dm2.col2 = MixedColumn
dm2.col2 = 'test'
dm += dm2
print(dm)
