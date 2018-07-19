<div class=" YAMLDoc" id="" markdown="1">

 

<div class="FunctionDoc YAMLDoc" id="from_json" markdown="1">

## function __from\_json__\(s\)

*Requires json_tricks*

Creates a DataMatrix from a `json` string.

__Arguments:__

- `s` -- A json string.
	- Type: str

__Returns:__

A DataMatrix.

- Type: DataMatrix.

</div>

<div class="FunctionDoc YAMLDoc" id="from_pandas" markdown="1">

## function __from\_pandas__\(df\)

Converts a pandas DataFrame to a DataMatrix.

__Example:__

%--
python: |
 import pandas as pd
 from datamatrix import convert

 df = pd.DataFrame( {'col' : [1,2,3] } )
 dm = convert.from_pandas(df)
 print(dm)
--%

__Arguments:__

- `df` -- No description
	- Type: DataFrame

__Returns:__

No description

- Type: DataMatrix

</div>

<div class="FunctionDoc YAMLDoc" id="to_json" markdown="1">

## function __to\_json__\(dm\)

*Requires json_tricks*

Creates (serializes) a `json` string from a DataMatrix.

__Arguments:__

- `dm` -- A DataMatrix to serialize.
	- Type: DataMatrix

__Returns:__

A json string.

- Type: str

</div>

<div class="FunctionDoc YAMLDoc" id="to_pandas" markdown="1">

## function __to\_pandas__\(obj\)

Converts a DataMatrix to a pandas DataFrame, or a column to a Series.

__Example:__

%--
python: |
 from datamatrix import DataMatrix, convert

 dm = DataMatrix(length=3)
 dm.col = 1, 2, 3
 df = convert.to_pandas(dm)
 print(df)
--%

__Arguments:__

- `obj` -- No description
	- Type: DataMatrix, BaseColumn

__Returns:__

No description

- Type: DataFrame, Series

</div>

<div class="FunctionDoc YAMLDoc" id="wrap_pandas" markdown="1">

## function __wrap\_pandas__\(fnc\)

A decorator for pandas functions. It converts a DataMatrix to a DataFrame, passes it to a function, and then converts the returned DataFrame back to a DataMatrix.

__Example:__

~~~ .python
import pandas as pd
from datamatrix import convert as cnv

pivot_table = cnv.wrap_pandas(pd.pivot_table)
~~~

__Arguments:__

- `fnc` -- A function that takes a DataFrame as first argument and returns a DataFrame as sole return argument.
	- Type: callable

__Returns:__

A function takes a DataMatrix as first argument and returns a DataMatrix as sole return argument.

</div>

</div>

