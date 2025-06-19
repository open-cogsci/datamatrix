"""Implements various functionality for compatibility with pandas. By executing
this module as a script, the _dataframe_compat_mixin module is generated. This
needs to be done only when there are changed in the pandas API.
"""

def _to_pandas(obj):
    """
    Convert a DataMatrix or BaseColumn object to a pandas DataFrame or Series.

    This function checks the type of the input object and converts it to the corresponding
    pandas object if it is an instance of DataMatrix or BaseColumn. If the input is a list
    or dictionary, it recursively converts each element. Otherwise, it returns the object as-is.

    Args:
        obj: The object to be converted. Can be a DataMatrix, BaseColumn, list, dictionary, or any other type.

    Returns:
        The converted pandas DataFrame, Series, or the original object if no conversion is needed.
    """
    from ._datamatrix import DataMatrix
    from ._basecolumn import BaseColumn
    from datamatrix import convert as cnv

    if isinstance(obj, DataMatrix):
        return cnv.to_dataframe(obj)
    if isinstance(obj, BaseColumn):
        return cnv.to_series(obj)
    if isinstance(obj, list):
        return [_to_pandas(val) for val in obj]
    if isinstance(obj, dict):
        return {key: _to_pandas(val) for key, val in obj.items()}
    return obj

def _from_pandas(obj):
    """
    Convert a pandas DataFrame or Series to a DataMatrix or BaseColumn object.

    This function checks the type of the input object and converts it to the corresponding
    DataMatrix or BaseColumn object if it is an instance of pandas DataFrame or Series.
    If the input is a list or dictionary, it recursively converts each element.
    Otherwise, it returns the object as-is.

    Args:
        obj: The object to be converted. Can be a pandas DataFrame, Series, list, dictionary, or any other type.

    Returns:
        The converted DataMatrix, BaseColumn, or the original object if no conversion is needed.

    Raises:
        ImportError: If pandas is not installed.
    """
    try:
        import pandas as pd
    except ImportError:
        raise ImportError('Trying to emulate pandas API, but pandas is not installed')
    from datamatrix import convert as cnv

    if isinstance(obj, pd.DataFrame):
        return cnv.from_dataframe(obj)
    if isinstance(obj, list):
        return [_from_pandas(val) for val in obj]
    if isinstance(obj, dict):
        return {key: _from_pandas(val) for key, val in obj.items()}
    return obj

def _inner(self, function_name, *args, **kwargs):
    """
    Internal function to handle method calls on DataMatrix objects using pandas API.

    This function checks if the method exists in the pandas API and calls it with the provided arguments.
    It also handles the conversion of the input and output objects between DataMatrix and pandas DataFrame.

    Args:
        self: The DataMatrix object on which the method is called.
        function_name (str): The name of the pandas method to be called.
        *args: Positional arguments to be passed to the pandas method.
        **kwargs: Keyword arguments to be passed to the pandas method.

    Returns:
        The result of the pandas method call, converted back to a DataMatrix object if necessary.

    Raises:
        ValueError: If inplace=True is provided as a keyword argument.
        NotImplementedError: If the specified method is not found in the pandas API.
    """
    if kwargs.get('inplace', False):
        raise ValueError('inplace=True is not supported')
    try:
        fnc = getattr(_to_pandas(self), function_name)
    except AttributeError:
        raise NotImplementedError(f'{function_name} not found in pandas API')
    if callable(fnc):
        result = fnc(*_to_pandas(args), **_to_pandas(kwargs))
    else:
        result = fnc
    return _from_pandas(result)

def df_compat_function(function_name):
    """
    Decorator to create a function that can be called on a DataMatrix object using the pandas API.

    This decorator wraps a function so that it can be called on a DataMatrix object and internally
    uses the pandas API to perform the operation.

    Args:
        function_name (str): The name of the pandas function to be called.

    Returns:
        A function that can be called on a DataMatrix object.
    """
    def inner(self, *args, **kwargs):
        return _inner(self, function_name, *args, **kwargs)
    return inner

def df_compat_property(function_name):
    """
    Decorator to create a property that can be accessed on a DataMatrix object using the pandas API.

    This decorator wraps a property so that it can be accessed on a DataMatrix object and internally
    uses the pandas API to perform the operation.

    Args:
        function_name (str): The name of the pandas property to be accessed.

    Returns:
        A property that can be accessed on a DataMatrix object.
    """
    @property
    def inner(self, *args, **kwargs):
        return _inner(self, function_name, *args, **kwargs)
    return inner

def df_compat_staticmethod(function_name):
    """
    Decorator to create a static method that can be called on a DataMatrix object using the pandas API.

    This decorator wraps a static method so that it can be called on a DataMatrix object and internally
    uses the pandas API to perform the operation.

    Args:
        function_name (str): The name of the pandas static method to be called.

    Returns:
        A static method that can be called on a DataMatrix object.
    """
    def inner(*args, **kwargs):
        from datamatrix import convert as cnv
        import pandas as pd
        try:
            fnc = getattr(pd.DataFrame, function_name)
        except AttributeError:
            raise NotImplementedError(f'{function_name} not found in pandas API')
        result = fnc(*args, **kwargs)
        if isinstance(result, pd.DataFrame):
            return cnv.from_dataframe(result)
        return result
    return inner


if __name__ == '__main__':
    
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from datamatrix import DataMatrix
    from datamatrix._datamatrix._basecolumn import BaseColumn
    import pandas as pd
    
    def get_attribute_type(attr):
        """Determine the type of an attribute (property, function, staticmethod, etc.)."""
        if isinstance(attr, property):
            return "property"
        elif isinstance(attr, staticmethod):
            return "staticmethod"
        elif isinstance(attr, classmethod):
            return "classmethod"
        elif callable(attr):
            return "function"
        else:
            return None
    
    def get_class_attributes(cls):
        """Get all relevant attributes of a class, excluding magic methods."""
        attributes = {}
        for attr_name in dir(cls):
            # Skip magic methods
            if not attr_name.startswith('_'):
                try:
                    attr = getattr(cls, attr_name)
                    attr_type = get_attribute_type(attr)
                    if attr_type:
                        attributes[attr_name] = attr_type
                except:
                    # Skip attributes that can't be accessed
                    continue
        return attributes
    
    def compare_classes(cls1, cls2):
        """Compare two classes and find attributes in cls2 not present in cls1."""
        cls1_attrs = get_class_attributes(cls1)
        cls2_attrs = get_class_attributes(cls2)
    
        missing_attributes = {}
    
        for attr_name, attr_type in cls2_attrs.items():
            if attr_name not in cls1_attrs:
                missing_attributes[attr_name] = attr_type
    
        return missing_attributes    
    
    
    with open('datamatrix/_datamatrix/_dataframe_compat_mixin.py', 'w') as file:
        file.write(f'''"""Auto-generated mixins for pandas compatibility.
Based on pandas {pd.__version__}.
"""
from ._dataframe_compat import df_compat_function, df_compat_property, df_compat_staticmethod
    
class DataFrameCompatMixin:
''')
        result = compare_classes(DataMatrix, pd.DataFrame)
        result['iterrows'] = 'function'
        result['__dataframe__'] = 'function'
        for attr, attr_type in result.items():
            file.write(f"    {attr} = df_compat_{attr_type}('{attr}')\n")
        file.write(f'''
class SeriesCompatMixin:
''')
        result = compare_classes(BaseColumn, pd.Series)
        for attr, attr_type in result.items():
            file.write(f"    {attr} = df_compat_{attr_type}('{attr}')\n")