#!/usr/bin/env python3
# coding=utf-8

import sys
sys.path.insert(0, '/home/sebastiaan/git/python-yamldoc/')
import yamldoc
import imp

ROOT = '/home/sebastiaan/git/python-datamatrix/'
TARGET = 'include/api/'
sys.path.insert(0, ROOT)


def createdoc(src, target, cls, **kwdict):

    if 'dummy' in sys.modules:
        del sys.modules['dummy']
    if cls is None:
        obj = imp.load_source('dummy', ROOT + src)
    else:
        obj = getattr(imp.load_source(cls, ROOT + src), cls)
    df = yamldoc.DocFactory(obj, container=u'div', **kwdict)
    print('Writing %s\n' % target)
    with open(TARGET + target, 'w') as fd:
        fd.write(str(df))


def main():

    global ROOT

    createdoc('datamatrix/operations.py',
        target='operations.md', onlyContents=True,
        types=['function', 'module'], cls=None, exclude=[
            '_SeriesColumn', 'BaseColumn', 'DataMatrix', 'FloatColumn',
            'MixedColumn', 'Index', 'IntColumn', 'convert',
            'map_', 'filter_', 'setcol'])
    createdoc('datamatrix/functional.py',
        target='functional.md', onlyContents=True,
        types=['function', 'module'], cls=None, exclude=[
            '_SeriesColumn', 'BaseColumn', 'Index', 'DataMatrix'])
    createdoc('datamatrix/convert/__init__.py',
        target='convert.md', onlyContents=True,
        types=['function', 'module'], cls=None, exclude=['DataMatrix'])
    createdoc('datamatrix/series.py',
        target='series.md', onlyContents=True,
        types=['function', 'module'], cls=None, exclude=[
            '_SeriesColumn', 'FloatColumn', 'ops', 'fnc', 'BaseColumn',
            'DataMatrix', 'reduce_', '_MultiDimensionalColumn', 'nancount',
            'infcount', 'flatten', 'reduce'])
    createdoc('datamatrix/multidimensional.py',
        target='multidimensional.md', onlyContents=True,
        types=['function', 'module'], cls=None, exclude=[
            '_MultiDimensionalColumn', 'FloatColumn', 'IntColumn', 'ops', 
            'fnc', 'BaseColumn', 'DataMatrix'])
    createdoc('datamatrix/io/__init__.py',
        target='io.md', onlyContents=True,
        types=['function', 'module'], cls=None, exclude=[])

if __name__ == '__main__':
    main()
