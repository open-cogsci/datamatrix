import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from datamatrix import DataMatrix

# Set the backend to Agg for headless operation
plt.switch_backend('Agg')

# ------------------------------------------------------------------
# Fixtures / helpers
# ------------------------------------------------------------------

TEST_CLASSES = pd.DataFrame, DataMatrix

def _make_sample(cls, with_nans=False):
    """Return a small sample object for a given class."""
    data = {
        "x": np.linspace(0, 2 * np.pi),
        "y": np.sin(np.linspace(0, 2 * np.pi)),
    }
    return cls(data)

# ------------------------------------------------------------------
# CRITICAL compatibility
# ------------------------------------------------------------------

def test_basic_plot():
    """Data can be passed as a dict at construction time."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.plot(obj['x'], obj['y'])
    plt.show()

def test_line_plot_multiple_lines():
    """Test plotting multiple lines."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.plot(obj['x'], obj['y'], label='sin(x)')
        plt.plot(obj['x'], np.cos(obj['x']), label='cos(x)')
        plt.legend()
    plt.show()

def test_scatter_plot():
    """Test basic scatter plot."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.scatter(obj['x'], obj['y'])
    plt.show()

def test_scatter_plot_custom():
    """Test scatter plot with custom colors and sizes."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        colors = np.random.rand(len(obj['x']))
        sizes = np.random.rand(len(obj['x'])) * 100
        plt.scatter(obj['x'], obj['y'], c=colors, s=sizes)
    plt.show()

def test_bar_plot():
    """Test basic bar plot."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.bar(obj['x'], obj['y'])
    plt.show()

def test_bar_plot_horizontal():
    """Test horizontal bar plot."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.barh(obj['x'], obj['y'])
    plt.show()

def test_histogram():
    """Test basic histogram."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.hist(obj['y'], bins=10)
    plt.show()

def test_histogram_custom_bins():
    """Test histogram with custom bin sizes."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.hist(obj['y'], bins=20)
    plt.show()

def test_pie_chart():
    """Test basic pie chart."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.pie(obj['x'])
    plt.show()

def test_pie_chart_custom():
    """Test pie chart with custom styles."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.pie(obj['x'], explode=np.zeros(len(obj['y'])), labels=obj['x'], autopct='%1.1f%%')
    plt.show()

def test_box_plot():
    """Test basic box plot."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.boxplot(obj['y'])
    plt.show()

def test_subplots():
    """Test creating multiple subplots."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        fig, axs = plt.subplots(2, 1)
        axs[0].plot(obj['x'], obj['y'])
        axs[1].plot(obj['x'], np.cos(obj['x']))
    plt.show()

def test_customization():
    """Test adding labels, titles, and legends."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.plot(obj['x'], obj['y'], label='sin(x)')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Sine Wave')
        plt.legend()
    plt.show()

def test_error_bars():
    """Test adding error bars to a plot."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        plt.errorbar(obj['x'], obj['y'], yerr=0.1, fmt='o')
    plt.show()