import statsmodels.api as sm
from statsmodels.formula.api import ols


def describe_data(df):

    summary = df.describe()
    print("\nSummary statistics:")
    print(summary)

    return summary


def anova_table(df, x, y, typ=2):

    model = ols(f"Q({y!r}) ~ C(Q({x!r}))", data=df).fit()
    anova = sm.stats.anova_lm(model, typ=typ)
    print(anova)

    return anova


def mean(df, column):

    y = df[column].mean()
    print(y)

    return y


def correlation(df):

    correlation = df.corr(method="spearman", numeric_only=True)
    print(correlation)

    return correlation