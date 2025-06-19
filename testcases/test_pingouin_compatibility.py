import numpy as np
from matplotlib import pyplot as plt
import pandas as pd
from datamatrix import DataMatrix
import pingouin as pg

# Set the backend to Agg for headless operation
plt.switch_backend('Agg')

# ------------------------------------------------------------------
# Fixtures / helpers
# ------------------------------------------------------------------

TEST_CLASSES = pd.DataFrame, DataMatrix

def _make_sample(cls, design='between', n_subjects=32, seed=42):
    """Return a sample dataset for a given class."""
    np.random.seed(seed)
    
    if design == 'between':
        # Between-subjects design
        data = {
            'subject': np.arange(n_subjects),
            'group': np.repeat(['A', 'B'], n_subjects // 2),
            'score': np.concatenate([
                np.random.normal(100, 15, n_subjects // 2),
                np.random.normal(110, 15, n_subjects // 2)
            ]),
            'age': np.random.normal(25, 5, n_subjects),
            'treatment': np.tile(['placebo', 'drug'], n_subjects // 2)
        }
    elif design == 'within':
        # Within-subjects design
        n_obs = n_subjects // 3
        data = {
            'subject': np.repeat(np.arange(n_obs), 3),
            'time': np.tile(['T1', 'T2', 'T3'], n_obs),
            'score': np.concatenate([
                np.random.normal(100, 10, n_obs),
                np.random.normal(105, 10, n_obs),
                np.random.normal(110, 10, n_obs)
            ]) + np.random.normal(0, 5, n_obs * 3)
        }
    elif design == 'mixed':
        # Mixed design
        n_obs = n_subjects // 2
        data = {
            'subject': np.tile(np.arange(n_obs), 2),
            'time': np.repeat(['pre', 'post'], n_obs),
            'group': np.concatenate([np.repeat(['control', 'treatment'], n_obs // 2)] * 2),
            'score': np.concatenate([
                np.random.normal(100, 10, n_obs),
                np.random.normal(110, 10, n_obs)
            ])
        }
    elif design == 'correlation':
        # For correlation analyses
        data = {
            'x': np.random.normal(100, 15, n_subjects),
            'y': np.random.normal(100, 15, n_subjects),
            'z': np.random.normal(100, 15, n_subjects)
        }
        # Add correlation
        data['y'] = data['x'] * 0.7 + np.random.normal(0, 10, n_subjects)
        data['z'] = data['x'] * 0.3 + data['y'] * 0.4 + np.random.normal(0, 10, n_subjects)
    
    return cls(data)

# ------------------------------------------------------------------
# T-test Tests
# ------------------------------------------------------------------

def test_ttest_one_sample():
    """Test one-sample t-test."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        result = pg.ttest(df['score'], 100)
        assert 'T' in result
        assert 'p_val' in result

def test_ttest_independent():
    """Test independent samples t-test."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        group_a = df[df['group'] == 'A']['score']
        group_b = df[df['group'] == 'B']['score']
        result = pg.ttest(group_a, group_b, paired=False)
        assert 'T' in result
        assert 'p_val' in result

def test_ttest_paired():
    """Test paired samples t-test."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='within')
        t1_scores = df[df['time'] == 'T1']['score']
        t2_scores = df[df['time'] == 'T2']['score']
        # Ensure same length for paired test
        min_len = min(len(t1_scores), len(t2_scores))
        result = pg.ttest(t1_scores[:min_len], t2_scores[:min_len], paired=True)
        assert 'T' in result
        assert 'p_val' in result

# ------------------------------------------------------------------
# ANOVA Tests
# ------------------------------------------------------------------

def test_anova_oneway():
    """Test one-way ANOVA."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        result = pg.anova(data=df, dv='score', between='group')
        assert 'F' in result.columns
        assert 'p_unc' in result.columns

def test_rm_anova():
    """Test repeated measures ANOVA."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='within')
        result = pg.rm_anova(data=df, dv='score', within='time', subject='subject')
        assert 'F' in result.columns
        assert 'p_unc' in result.columns

def test_mixed_anova():
    """Test mixed ANOVA."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='mixed')
        result = pg.mixed_anova(data=df, dv='score', within='time', 
                               between='group', subject='subject')
        assert 'F' in result.columns
        assert 'p_unc' in result.columns

# ------------------------------------------------------------------
# Correlation Tests
# ------------------------------------------------------------------

def test_correlation():
    """Test Pearson and Spearman correlation."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='correlation')
        
        # Pearson correlation
        n, r, ci, p, bf, power = pg.corr(df['x'], df['y'], method='pearson').values[0]
        assert -1 <= r <= 1
        assert 0 <= p <= 1
        
        # Spearman correlation
        n, r, ci, p, power = pg.corr(df['x'], df['y'], method='spearman').values[0]
        assert -1 <= r <= 1
        assert 0 <= p <= 1

def test_pairwise_correlation():
    """Test pairwise correlations."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='correlation')
        result = pg.pairwise_corr(df, columns=['x', 'y', 'z'])
        assert len(result) > 0
        assert 'r' in result.columns
        assert 'p_unc' in result.columns

def test_partial_correlation():
    """Test partial correlation."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='correlation')
        result = pg.partial_corr(data=df, x='x', y='y', covar='z')
        assert 'r' in result.columns
        assert 'p_val' in result.columns

# ------------------------------------------------------------------
# Non-parametric Tests
# ------------------------------------------------------------------

def test_wilcoxon():
    """Test Wilcoxon signed-rank test."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='within')
        t1_scores = df[df['time'] == 'T1']['score']
        t2_scores = df[df['time'] == 'T2']['score']
        min_len = min(len(t1_scores), len(t2_scores))
        result = pg.wilcoxon(t1_scores[:min_len], t2_scores[:min_len])
        assert 'W_val' in result
        assert 'p_val' in result

def test_mann_whitney():
    """Test Mann-Whitney U test."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        group_a = df[df['group'] == 'A']['score']
        group_b = df[df['group'] == 'B']['score']
        result = pg.mwu(group_a, group_b)
        assert 'U_val' in result
        assert 'p_val' in result

def test_kruskal():
    """Test Kruskal-Wallis test."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        result = pg.kruskal(data=df, dv='score', between='group')
        assert 'H' in result.columns
        assert 'p_unc' in result.columns

# ------------------------------------------------------------------
# Regression Tests
# ------------------------------------------------------------------

def test_linear_regression():
    """Test linear regression."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='correlation')
        result = pg.linear_regression(df[['x', 'z']], df['y'])
        assert 'coef' in result.columns
        assert 'pval' in result.columns

def test_logistic_regression():
    """Test logistic regression."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        # Create binary outcome
        
        df['outcome'] = 0
        for i, row in df.iterrows():
            if row['score'] > df['score'].median():
                df['outcome'][i] = 1
        result = pg.logistic_regression(df[['age']], df['outcome'])
        assert 'coef' in result.columns
        assert 'pval' in result.columns

# ------------------------------------------------------------------
# Effect Size Tests
# ------------------------------------------------------------------

def test_effect_size():
    """Test effect size calculations."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        group_a = df[df['group'] == 'A']['score']
        group_b = df[df['group'] == 'B']['score']
        
        # Cohen's d
        d = pg.compute_effsize(group_a, group_b, eftype='cohen')
        assert isinstance(d, (int, float))
        
        # Hedge's g
        g = pg.compute_effsize(group_a, group_b, eftype='hedges')
        assert isinstance(g, (int, float))

# ------------------------------------------------------------------
# Normality Tests
# ------------------------------------------------------------------

def test_normality():
    """Test normality tests."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        result = pg.normality(df['score'])
        assert 'W' in result.columns
        assert 'pval' in result.columns

def test_normality_grouped():
    """Test normality tests by group."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='between')
        result = pg.normality(data=df, dv='score', group='group')
        assert len(result) == 2  # Two groups
        assert 'W' in result.columns
        assert 'pval' in result.columns

# ------------------------------------------------------------------
# Post-hoc Tests
# ------------------------------------------------------------------

def test_pairwise_ttests():
    """Test pairwise t-tests."""
    for cls in TEST_CLASSES:
        df = _make_sample(cls, design='within')
        result = pg.pairwise_ttests(data=df, dv='score', within='time', 
                                   subject='subject', padjust='bonf')
        assert 'T' in result.columns
        assert 'p_unc' in result.columns
        assert 'p_corr' in result.columns
