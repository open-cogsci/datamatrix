<div class=" YAMLDoc" id="" markdown="1">

 

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

<div class="FunctionDoc YAMLDoc" id="to_pandas" markdown="1">

## function __to\_pandas__\(dm\)

Converts a DataMatrix to a pandas DataFrame.

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

- `dm` -- No description
	- Type: DataMatrix

__Returns:__

No description

- Type: DataFrame

</div>

</div>

