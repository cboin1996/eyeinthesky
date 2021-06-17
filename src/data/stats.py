import pandas as pd 
from scipy import stats 
import numpy as np 

def remove_outliers(df):
    z_scores = stats.zscore(df)
    abs_z_scores = np.abs(z_scores)

    good_entries = (abs_z_scores < 3).all(axis=1)
    good_df = df[good_entries]

    outlier_entries = (abs_z_scores > 3).all(axis=1)
    outlier_df = df[outlier_entries]

    return good_df, outlier_df

def remove_outliers_from_cols(df, cols):
    z_scores = stats.zscore(df[cols])
    abs_z_scores = np.abs(z_scores)

    good_entries = (abs_z_scores < 3).all(axis=1)
    good_df = df[good_entries]

    outlier_entries = (abs_z_scores > 3).all(axis=1)
    outlier_df = df[outlier_entries]

    return good_df, outlier_df
