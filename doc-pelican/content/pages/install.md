title: Install


## Dependencies

`DataMatrix` requires only the Python standard library. That is, you can use it without installing any additional Python packages (although the pip and conda packages install some of the optional dependencies by default). Python 3.7 and higher are supported.

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
pip install datamatrix
~~~


### Anaconda

~~~bash
conda install -c conda-forge datamatrix
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
