title: DataMatrix

`DataMatrix` is an intuitive Python library for working with column-based and continuous data.

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
- Great support for [functional programming](%link:functional%), including advanced [memoization (caching)](%link:memoization).
- Mix [two-dimensional](%link:series%) (series) and one-dimensional data in a single data structure.
- `DataMatrix` does what it does really well, but it cannot do everything that libraries such as `pandas` can. Therefore, you can [convert](%link:convert%) to and from `pandas.DataFrame`.


%--
video:
 source: youtube
 id: VidTutorial
 videoid: KLkJQUYFSlA
 width: 640
 height: 360
 caption: |
  Using <code>datamatrix</code> to play with movie data.
--%

%--
video:
 source: youtube
 id: VidTutorial2
 videoid: PtUmhQ2vupw
 width: 640
 height: 360
 caption: |
  Using <code>datamatrix</code> to analyze eye-movement data.
--%


## Example

%--
python: |
 from datamatrix import DataMatrix
 # Four philosophers with their names, fields, and genders
 dm = DataMatrix(length=4)
 dm.name = 'Ibn al-Haytam', 'Hypatia', 'Popper', 'de Beauvoir'
 dm.field = 'Optics', 'Mathematics', 'Science', 'Existentialism'
 dm.gender = 'M', 'F', 'M', 'F'
 print('Philosophers:')
 print(dm)
 # Select only women existentialists
 dm = (dm.gender == 'F') & (dm.field == 'Existentialism')
 print('Women Existentialists:')
 print(dm)
--%
