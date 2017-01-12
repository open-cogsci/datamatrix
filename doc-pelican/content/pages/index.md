title: DataMatrix

`DataMatrix` is a Python library for working with column-based and continuous data.

<div class="btn-group" role="group" aria-label="...">
  <a role="button" class="btn btn-success" href="%url:install%">
		<span class="glyphicon glyphicon-download" aria-hidden="true"></span>
		Install
	 </a>
  <a role="button" class="btn btn-success" href="%url:basic%">
  <span class="glyphicon glyphicon-education" aria-hidden="true"></span>
  	Basic use
  </a>
  <a role="button" class="btn btn-success" href="http://forum.cogsci.nl/">
  <span class="glyphicon glyphicon-comment" aria-hidden="true"></span>
  Forum</a>
</div>


## Features

- [An intuitive syntax](%link:basic%) that makes your code easy to read.
- Requires only the Python standard libraries (but you can use `numpy` to improve performance).
- Mix [two-dimensional](%link:series%) (series) and one-dimensional data in a single data structure.
- `DataMatrix` does what it does really well, but it cannot do everything that libraries such as `pandas` can. Therefore, you can [convert](%link:convert%) to and from `pandas.DataFrame`.


## Example

%--
python: |
 from datamatrix import DataMatrix
 dm = DataMatrix(length=5)
 dm.prime = 2, 3, 5, 7, 11
 print('First five prime numbers')
 print(dm)
 dm = (dm.prime >= 3) & (dm.prime <= 7)
 print('Keep only numbers between 3 and 7')
 print(dm)
--%
