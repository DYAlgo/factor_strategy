import pandas as pd

def standardize(df, kind="time", use_median=False):
    """Standardize each column on a expanding basis. Because 
    we are standardizing data on an expanding() basis, there is 
    no guarantee that the data will have a mean 0 and standard deviation of
    1. However, this guarantee that no data leak occurs. 
    """
    if kind == "time":
        if use_median:
            # Time Series standardization
            return (df - df.expanding().median()) / df.expanding().std()
        else:
            return (df - df.expanding().mean()) / df.expanding().std()
    else:
        if use_median:
            # Cross-sectional standardization
            return ((df.T - df.median(axis=1)) / df.std(axis=1)).T
        else:
            # Cross-sectional standardization
            return ((df.T - df.mean(axis=1)) / df.std(axis=1)).T

def merge(df1, df2, var_name):
    """Merge new time series dataframe into an exising multi-level dataframe."""
    cols = pd.MultiIndex.from_tuples(
        [tuple([var_name] + [x]) for x in list(df2.columns)]
    )
    df2 = pd.DataFrame(df2.values, columns=cols, index=df2.index)
    return pd.merge(df1.copy(), df2.copy(), on="date", how="outer")

def winsorized(df):
    """Apply winsorized method of imputing outliers using only historical data.
    This method finds the 5% and 95% without considering the future data points in df.
    """
    upper = df.expanding().quantile(0.95, axis=1)
    lower = df.expanding().quantile(0.05, axis=1)
    df[df > upper] = upper[df > upper]
    df[df < lower] = lower[df < lower]
    return df

# def clip(df):
#     return df.clip(
#         df.quantile(0.05, axis=0),
#         df.quantile(0.95, axis=0),
#         axis=1
#     )

def full_winsorzed(df):
    """Apply winsorized method by finding the 5% and 95% level of the whole data set. 
    This introduces data leak, but will may make the data set more suitable for statistical
    modelling. 
    """
    lower = df.unstack().quantile(0.001)
    upper = df.unstack().quantile(0.999)
    return df.clip(
        lower,
        upper,
        axis=1
    )