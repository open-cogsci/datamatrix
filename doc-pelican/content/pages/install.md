title: Install


## Dependencies

`DataMatrix` requires only the Python standard library. That is, you can use it without installing any additional Python packages. Python 3.7 and higher are supported.

The following packages are required for extra functionality:

- `numpy` and `scipy` for using the `FloatColumn`, `IntColumn`, `SeriesColumn`, `MultiDimensionalColumn` objects
- `pandas` for conversion to and from `pandas.DataFrame`
- `mne` for conversion to and from `mne.Epochs` and `mne.TFR`
- `fastnumbers` for improved performance
- `prettytable` for creating a text representation of a DataMatrix (e.g. to print it out)
- `openpyxl` for reading and writing `.xlsx` files
- `json_tricks` for hashing, serialization to and from `json`, and memoization (caching)
- `tomlkit` for reading configuration from `pyproject.toml`
- `psutil` for dynamic loading of large data


## Installation

### PyPi (pip install)

~~~bash
pip install https://github.com/open-cogsci/python-datamatrix/releases/download/prerelease%2F1.0.0a4/datamatrix-1.0.0a4-py2.py3-none-any.whl --upgrade
~~~

Optional dependencies:

~~~bash
pip install fastnumbers numpy scipy prettytable openpyxl pandas json_tricks tomlkit mne psutil
~~~


### Anaconda

~~~bash
conda install -c conda-forge datamatrix
~~~

Optional dependencies:


~~~bash
conda install -c conda-forge scipy pandas json_tricks tomlkit mne psutil
~~~


### Ubuntu

~~~bash
sudo add-apt-repository ppa:smathot/cogscinl  # for stable releases
sudo add-apt-repository ppa:smathot/rapunzel  # for development releases
sudo apt-get update
sudo apt install python3-datamatrix
~~~


## Source code

- <https://github.com/open-cogsci/python-datamatrix>
