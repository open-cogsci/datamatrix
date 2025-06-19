import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from datamatrix import DataMatrix
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.robust.robust_linear_model import RLM
from scipy import stats

# Set the backend to Agg for headless operation
plt.switch_backend('Agg')

# ------------------------------------------------------------------
# Fixtures / helpers
# ------------------------------------------------------------------

TEST_CLASSES = pd.DataFrame, DataMatrix

def _make_sample(cls, with_nans=False):
    """Return a small sample object for a given class."""
    np.random.seed(42)
    n = 100
    data = {
        "x": np.linspace(0, 2 * np.pi, n),
        "x2": np.random.normal(0, 1, n),
        "y": np.sin(np.linspace(0, 2 * np.pi, n)) + np.random.normal(0, 0.1, n),
        "binary": np.random.binomial(1, 0.5, n),
        "count": np.random.poisson(3, n),
        "group": np.random.choice(['A', 'B', 'C'], n),
        "time": np.arange(n),
        "weights": np.random.uniform(0.5, 1.5, n)
    }
    if with_nans:
        # Insert some NaN values
        data["x2"][::10] = np.nan
        data["y"][::15] = np.nan
    return cls(data)

def _make_time_series(cls):
    """Return a time series sample for ARIMA testing."""
    np.random.seed(42)
    dates = np.arange(0, 100)
    trend = np.linspace(100, 110, 100)
    seasonal = 10 * np.sin(np.linspace(0, 8 * np.pi, 100))
    noise = np.random.normal(0, 2, 100)
    data = {
        'date': dates,
        'value': trend + seasonal + noise
    }
    return cls(data)

# ------------------------------------------------------------------
# OLS Regression Tests
# ------------------------------------------------------------------

def test_ols_basic():
    """Test basic OLS regression with statsmodels."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        # Add constant for intercept
        X = sm.add_constant(obj[['x', 'x2']])
        y = obj['y']
        model = sm.OLS(y, X)
        results = model.fit()
        assert results.params is not None
        assert len(results.params) == 3  # intercept + 2 predictors

def test_ols_formula():
    """Test OLS using formula API."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.ols('y ~ x + x2', data=obj)
        results = model.fit()
        assert results.rsquared is not None
        assert results.pvalues is not None

def test_ols_with_categorical():
    """Test OLS with categorical variables."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.ols('y ~ x + C(group)', data=obj)
        results = model.fit()
        # Should have parameters for intercept, x, and group levels
        assert len(results.params) >= 3

# ------------------------------------------------------------------
# Logistic Regression Tests
# ------------------------------------------------------------------

def test_logit_basic():
    """Test basic logistic regression."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        X = sm.add_constant(obj[['x', 'x2']])
        y = obj['binary']
        model = sm.Logit(y, X)
        results = model.fit(disp=0)  # disp=0 to suppress output
        assert results.params is not None
        assert results.llf is not None  # log-likelihood

def test_logit_formula():
    """Test logistic regression using formula API."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.logit('binary ~ x + x2', data=obj)
        results = model.fit(disp=0)
        # Test predictions
        predictions = results.predict()
        assert len(predictions) == len(obj)
        assert all(0 <= p <= 1 for p in predictions)

# ------------------------------------------------------------------
# GLM Tests
# ------------------------------------------------------------------

def test_glm_poisson():
    """Test GLM with Poisson family for count data."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.glm('count ~ x + x2', 
                       data=obj, 
                       family=sm.families.Poisson())
        results = model.fit()
        assert results.aic is not None
        assert results.deviance is not None

def test_glm_binomial():
    """Test GLM with Binomial family."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.glm('binary ~ x + x2', 
                       data=obj, 
                       family=sm.families.Binomial())
        results = model.fit()
        assert results.params is not None

# ------------------------------------------------------------------
# Time Series Tests
# ------------------------------------------------------------------

def test_arima_basic():
    """Test basic ARIMA model."""
    for cls in TEST_CLASSES:
        obj = _make_time_series(cls)
        model = ARIMA(obj['value'], order=(1, 1, 1))
        results = model.fit()
        assert results.aic is not None
        # Test forecasting
        forecast = results.forecast(steps=5)
        assert len(forecast) == 5

# ------------------------------------------------------------------
# Robust Regression Tests
# ------------------------------------------------------------------

def test_rlm_basic():
    """Test Robust Linear Model."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        X = sm.add_constant(obj[['x', 'x2']])
        y = obj['y']
        model = RLM(y, X, M=sm.robust.norms.HuberT())
        results = model.fit()
        assert results.params is not None
        assert results.scale is not None

# ------------------------------------------------------------------
# Weighted Least Squares Tests
# ------------------------------------------------------------------

def test_wls_basic():
    """Test Weighted Least Squares."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        X = sm.add_constant(obj[['x', 'x2']])
        y = obj['y']
        weights = obj['weights']
        model = sm.WLS(y, X, weights=weights)
        results = model.fit()
        assert results.params is not None
        assert results.rsquared is not None

# ------------------------------------------------------------------
# Statistical Tests
# ------------------------------------------------------------------

def test_normality_tests():
    """Test normality tests on residuals."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.ols('y ~ x + x2', data=obj)
        results = model.fit()
        
        # Jarque-Bera test
        jb_stat, jb_pval = stats.jarque_bera(results.resid)
        assert jb_pval is not None
        
        # Shapiro-Wilk test
        sw_stat, sw_pval = stats.shapiro(results.resid)
        assert sw_pval is not None

def test_heteroscedasticity():
    """Test for heteroscedasticity using Breusch-Pagan test."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.ols('y ~ x + x2', data=obj)
        results = model.fit()
        
        # Breusch-Pagan test
        from statsmodels.stats.diagnostic import het_breuschpagan
        bp_stat, bp_pval, _, _ = het_breuschpagan(results.resid, results.model.exog)
        assert bp_pval is not None

def test_autocorrelation():
    """Test for autocorrelation using Durbin-Watson."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        model = smf.ols('y ~ x + x2', data=obj)
        results = model.fit()
        
        # Durbin-Watson test
        from statsmodels.stats.stattools import durbin_watson
        dw_stat = durbin_watson(results.resid)
        assert 0 <= dw_stat <= 4  # DW statistic is always between 0 and 4

# ------------------------------------------------------------------
# Missing Data Handling Tests
# ------------------------------------------------------------------

def test_ols_with_nans():
    """Test OLS with missing data."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls, with_nans=True)
        # statsmodels should handle NaNs automatically
        model = smf.ols('y ~ x + x2', data=obj)
        results = model.fit()
        assert results.params is not None
        # Check that some observations were dropped
        assert results.nobs < len(obj)

# ------------------------------------------------------------------
# Model Comparison Tests
# ------------------------------------------------------------------

def test_model_comparison():
    """Test comparing nested models."""
    for cls in TEST_CLASSES:
        obj = _make_sample(cls)
        
        # Fit two nested models
        model1 = smf.ols('y ~ x', data=obj)
        results1 = model1.fit()
        
        model2 = smf.ols('y ~ x + x2', data=obj)
        results2 = model2.fit()
        
        # Compare using likelihood ratio test
        from statsmodels.stats.api import anova_lm
        anova_results = anova_lm(results1, results2)
        assert anova_results is not None
        assert 'F' in anova_results.columns or 'LR' in anova_results.columns