def calc_momentum_factor(df, exclude, lag, norm=True):
    """Returns a dataframe consisting of the momentum of the stock"""
    if exclude >= lag:
        raise ValueError("Lag must be bigger than exclude recent period")
        
    mom_df = df["price_index"].pct_change(lag-exclude).shift(exclude)
    if norm:
        mean = mom_df.expanding().mean()
        std = mom_df.expanding().std()
        return (mom_df - mean) / std
    else:
        return mom_df

def calc_mean_reversion_factor(df, lag, norm=True):
    """
    Compute the mean reversion factor where the mean reversion is defined
    as the N-day return starting from the previous trading day.  
    """
    mr_df = df["price_index"].pct_change(lag)
    if norm:
        std = mr_df.expanding().std()
        mean = mr_df.expanding().mean()
        return (mr_df - mean) / std
    else:
        return mr_df

def calc_volatility_factor(df, lag, norm=True):
    """Returns a dataframe consisting of the historical normalized 
    historical volatility factor of the stock"""
    return_df = df["price_index"].pct_change()
    std = return_df.rolling(lag, min_periods=1).std()
    if norm:
        std_mu = std.expanding().mean() 
        return (std - std_mu) / std.expanding().std()
    else:
        return std