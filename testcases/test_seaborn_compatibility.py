import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from datamatrix import DataMatrix
import seaborn as sns

# Set the backend to Agg for headless operation
plt.switch_backend('Agg')

# ------------------------------------------------------------------
# Fixtures / helpers
# ------------------------------------------------------------------

TEST_CLASSES = pd.DataFrame, DataMatrix

def _make_sample(cls, with_categorical=False):
    """Return a small sample object for a given class."""
    n = 50
    data = {
        "x": np.linspace(0, 2 * np.pi, n),
        "y": np.sin(np.linspace(0, 2 * np.pi, n)) + np.random.normal(0, 0.1, n),
        "z": np.cos(np.linspace(0, 2 * np.pi, n)) + np.random.normal(0, 0.1, n),
        "value": np.random.randn(n),
    }
    
    if with_categorical:
        data["category"] = np.random.choice(['A', 'B', 'C'], n)
        data["group"] = np.random.choice(['Group1', 'Group2'], n)
    
    return cls(data)

# ------------------------------------------------------------------
# Relational plots
# ------------------------------------------------------------------

def test_scatterplot():
    """Test basic scatter plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.scatterplot(data=obj, x='x', y='y')
        plt.savefig(f'test_seaborn_scatterplot_{i}.png')
        plt.close()

def test_scatterplot_with_hue():
    """Test scatter plot with hue semantic."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.scatterplot(data=obj, x='x', y='y', hue='category')
        plt.savefig(f'test_seaborn_scatterplot_hue_{i}.png')
        plt.close()

def test_lineplot():
    """Test basic line plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.lineplot(data=obj, x='x', y='y')
        plt.savefig(f'test_seaborn_lineplot_{i}.png')
        plt.close()

def test_lineplot_with_confidence():
    """Test line plot with confidence intervals."""
    for i, cls in enumerate(TEST_CLASSES):
        # Create data with multiple observations per x value
        data = []
        for x in np.linspace(0, 2*np.pi, 20):
            for _ in range(10):
                data.append({'x': x, 'y': np.sin(x) + np.random.normal(0, 0.2)})
        obj = cls(data)
        sns.lineplot(data=obj, x='x', y='y')
        plt.savefig(f'test_seaborn_lineplot_confidence_{i}.png')
        plt.close()

# ------------------------------------------------------------------
# Categorical plots
# ------------------------------------------------------------------

def test_boxplot():
    """Test basic box plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.boxplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_boxplot_{i}.png')
        plt.close()

def test_violinplot():
    """Test violin plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.violinplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_violinplot_{i}.png')
        plt.close()

def test_barplot():
    """Test bar plot with error bars."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.barplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_barplot_{i}.png')
        plt.close()

def test_stripplot():
    """Test strip plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.stripplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_stripplot_{i}.png')
        plt.close()

def test_swarmplot():
    """Test swarm plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        # Reduce sample size for swarmplot to avoid warning
        obj = obj.iloc[:30] if hasattr(obj, 'iloc') else obj[:30]
        sns.swarmplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_swarmplot_{i}.png')
        plt.close()

def test_countplot():
    """Test count plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.countplot(data=obj, x='category')
        plt.savefig(f'test_seaborn_countplot_{i}.png')
        plt.close()

# ------------------------------------------------------------------
# Distribution plots
# ------------------------------------------------------------------

def test_histplot():
    """Test histogram plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.histplot(data=obj, x='value')
        plt.savefig(f'test_seaborn_histplot_{i}.png')
        plt.close()

def test_histplot_2d():
    """Test 2D histogram plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.histplot(data=obj, x='y', y='z')
        plt.savefig(f'test_seaborn_histplot_2d_{i}.png')
        plt.close()

def test_kdeplot():
    """Test KDE plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.kdeplot(data=obj, x='value')
        plt.savefig(f'test_seaborn_kdeplot_{i}.png')
        plt.close()

def test_kdeplot_2d():
    """Test 2D KDE plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.kdeplot(data=obj, x='y', y='z')
        plt.savefig(f'test_seaborn_kdeplot_2d_{i}.png')
        plt.close()

def test_ecdfplot():
    """Test ECDF plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.ecdfplot(data=obj, x='value')
        plt.savefig(f'test_seaborn_ecdfplot_{i}.png')
        plt.close()

# ------------------------------------------------------------------
# Regression plots
# ------------------------------------------------------------------

def test_regplot():
    """Test regression plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.regplot(data=obj, x='x', y='y')
        plt.savefig(f'test_seaborn_regplot_{i}.png')
        plt.close()

def test_lmplot():
    """Test lmplot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.lmplot(data=obj, x='x', y='y', hue='category')
        plt.savefig(f'test_seaborn_lmplot_{i}.png')
        plt.close()

# ------------------------------------------------------------------
# Matrix plots
# ------------------------------------------------------------------

def test_heatmap():
    """Test heatmap."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        # Create a correlation matrix
        corr_data = obj[['x', 'y', 'z', 'value']]
        if cls == DataMatrix:
            # For DataMatrix, we need to convert to DataFrame for correlation
            corr_matrix = pd.DataFrame(corr_data).corr()
        else:
            corr_matrix = corr_data.corr()
        sns.heatmap(corr_matrix, annot=True)
        plt.savefig(f'test_seaborn_heatmap_{i}.png')
        plt.close()

# ------------------------------------------------------------------
# Multi-plot grids
# ------------------------------------------------------------------

def test_pairplot():
    """Test pair plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        # Select subset of columns for pairplot
        sns.pairplot(obj[['x', 'y', 'z', 'value', 'category']], hue='category')
        plt.savefig(f'test_seaborn_pairplot_{i}.png')
        plt.close()

def test_jointplot():
    """Test joint plot."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.jointplot(data=obj, x='y', y='z', kind='scatter')
        plt.savefig(f'test_seaborn_jointplot_{i}.png')
        plt.close()

def test_jointplot_kde():
    """Test joint plot with KDE."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls)
        sns.jointplot(data=obj, x='y', y='z', kind='kde')
        plt.savefig(f'test_seaborn_jointplot_kde_{i}.png')
        plt.close()

# ------------------------------------------------------------------
# Style and customization
# ------------------------------------------------------------------

def test_with_style():
    """Test plot with seaborn style."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.set_style("whitegrid")
        sns.boxplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_style_{i}.png')
        plt.close()
        sns.set_style("white")  # Reset style

def test_with_palette():
    """Test plot with custom palette."""
    for i, cls in enumerate(TEST_CLASSES):
        obj = _make_sample(cls, with_categorical=True)
        sns.set_palette("husl")
        sns.violinplot(data=obj, x='category', y='value')
        plt.savefig(f'test_seaborn_palette_{i}.png')
        plt.close()
        sns.set_palette("deep")  # Reset palette