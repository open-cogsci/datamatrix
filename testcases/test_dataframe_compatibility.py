import pandas as pd
from datamatrix import DataMatrix

# ------------------------------------------------------------------
# Fixtures / helpers
# ------------------------------------------------------------------

TEST_CLASSES = pd.DataFrame, DataMatrix


def _make_sample(cls, with_nans=False):
    """Return a small sample object for a given class."""
    data = {
        "A": [1, 2, 3, None] if with_nans else [1, 2, 3, 4],
        "B": [4, 5, 6, 7],
        "C": ["x", "y", "z", "w"],
    }
    return cls(data)


# ------------------------------------------------------------------
# CRITICAL compatibility
# ------------------------------------------------------------------

def test_dict_initialization():
    """Data can be passed as a dict at construction time."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        assert set(obj.columns if cls is pd.DataFrame else obj.columns) == {"A", "B", "C"}


def test_list_of_dicts_initialization():
    """Data can be passed as a list of dicts at construction time."""
    data = [
        {"A": 1, "B": 4.1, "C": "x"},
        {"A": 2, "B": 5, "C": "y"},
        {"A": 3, "B": 6, "C": "z"},
        {"A": 4, "B": 7, "C": "w"},
    ]
    
    for cls in TEST_CLASSES:
        obj = cls(data)
        # Check column names
        assert set(obj.columns if cls is pd.DataFrame else obj.columns) == {"A", "B", "C"}
        # Check data integrity
        assert list(obj["A"]) == [1, 2, 3, 4]
        assert obj['A'].dtype == int
        assert list(obj["B"]) == [4.1, 5, 6, 7]
        assert obj['B'].dtype == float
        assert list(obj["C"]) == ["x", "y", "z", "w"]
        assert obj['C'].dtype == object


def test_list_of_dicts_with_missing_keys():
    """Test list of dicts where some dicts have missing keys."""
    data = [
        {"A": 1, "B": 4, "C": "x"},
        {"A": 2, "C": "y"},  # Missing "B"
        {"B": 6, "C": "z"},  # Missing "A"
        {"A": 4, "B": 7},    # Missing "C"
    ]
    
    for cls in TEST_CLASSES:
        obj = cls(data)
        # Check column names
        assert set(obj.columns if cls is pd.DataFrame else obj.columns) == {"A", "B", "C"}
        # Check that missing values are handled (None or NaN)
        assert len(obj) == 4
        # Note: DataFrame uses NaN for missing numeric values and None for objects
        # DataMatrix should handle this similarly


def test_empty_list_initialization():
    """Test initialization with an empty list."""
    for cls in TEST_CLASSES:
        obj = cls([])
        assert len(obj) == 0
        assert len(obj.columns if cls is pd.DataFrame else obj.columns) == 0


def test_list_of_empty_dicts():
    """Test initialization with a list of empty dicts."""
    data = [{}, {}, {}]
    for cls in TEST_CLASSES:
        obj = cls(data)
        assert len(obj) == 3
        assert len(obj.columns if cls is pd.DataFrame else obj.columns) == 0

def test_multi_column_selection():
    """Selecting a list of columns returns the expected subset."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        sub = obj[["A", "B"]]
        expected_cols = ["A", "B"]
        assert list(sub.columns) == expected_cols


def test_head_tail_size():
    """head, tail and size work as with pandas."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        assert len(obj.head(2)) == 2
        assert len(obj.tail(1)) == 1
        assert obj.size == 12  # 4 rows * 3 cols


def test_loc_iloc_indexers():
    """Basic .loc / .iloc retrieval."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        # Single cell
        assert obj.loc[0, "A"] == 1
        assert obj.iloc[1, 1] == 5
        # Row slice
        sliced = obj.loc[1:2, ["A", "B"]]
        assert sliced.equals(obj[["A", "B"]].iloc[1:3])


# ------------------------------------------------------------------
# IMPORTANT compatibility
# ------------------------------------------------------------------

def test_to_dict_roundtrip():
    """Conversion to dict matches pandas orient='list'."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        d = obj.to_dict(orient="list")
        assert d["A"][0] == 1


def test_groupby_like():
    """Groupby wrapper returns grouped means identical to pandas."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        res = obj.groupby("C")["A"].mean().sort_index()
        assert res.loc["x"] == 1


def test_drop_and_rename():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        dropped = obj.drop(columns=["C"])
        renamed = dropped.rename(columns={"A": "alpha"})
        cols = list(renamed.columns)
        assert cols == ["alpha", "B"]


def test_values_numpy():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        arr = obj.values
        assert arr.shape == (4, 3)


def test_dropna_fillna():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls, with_nans=True)
        filled = obj.fillna(0)
        assert (filled["A"][3]) == 0
        dropped = obj.dropna()
        assert len(dropped) == 3


# ------------------------------------------------------------------
# USEFUL compatibility
# ------------------------------------------------------------------

def test_sort_values():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        sorted_obj = obj.sort_values("B", ascending=False)
        first_b = sorted_obj.iloc[0]["B"]
        assert first_b == 7


def test_value_counts():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        counts = obj["C"].value_counts()
        assert counts["x"] == 1


def test_corr():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        corr = obj[["A", "B"]].corr()
        assert isinstance(corr, float) or corr.iloc[0, 0] == corr.iloc[1, 1]


def test_apply():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        doubled = obj["A"].apply(lambda x: x * 2)
        assert doubled.iloc[0] == 2


def test_iterrows():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        rows = [row for row in obj.iterrows()]
        assert len(rows) == 4


def test_copy():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        obj_copy = obj.copy()
        assert len(obj_copy) == len(obj)


def test_reset_and_set_index():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        obj2 = obj.set_index("C")
        obj3 = obj2.reset_index()
        assert len(obj3) == 4


def test_column_methods():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls, with_nans=True)
        assert obj["A"].isna().sum() == 1
        converted = obj["B"].astype(float)
        assert converted.iloc[0] == 4.0
        assert obj["C"].nunique() == 4


def test_dtypes_property():
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        dtypes = obj.dtypes
        # pandas returns Series, DataMatrix could return dict-like
        assert "A" in str(dtypes)
        

# ------------------------------------------------------------------
# EXTRA compatibility
# ------------------------------------------------------------------

def test_shape_property():
    """The .shape property matches (n_rows, n_cols)."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        rows, cols = obj.shape
        assert rows == 4 and cols == 3
        assert rows == len(obj)


def test_column_assignment():
    """Assigning a new column works the same way."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        obj["D"] = obj["A"] + obj["B"]
        val = obj.loc[0, "D"]
        obj.D = obj.A + obj.B
        val = obj.D[0]
        assert val == 5  # 1 + 4


def test_boolean_selection():
    """Boolean row filtering behaves identically."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        sub = obj[obj["A"] > 2]
        assert len(sub) == 2  # rows with A = 3 and 4
        