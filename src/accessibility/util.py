import pandas as pd
import os
from itertools import accumulate
from src.util import download_file

def get_lodes_file(raw_path, lodes_type, file_name):
    lodes_file = raw_path + file_name
    if not os.path.isfile(lodes_file):
        print("Downloading LODES data into " + lodes_file)
        url = f"https://lehd.ces.census.gov/data/lodes/LODES8/md/{lodes_type}/{file_name}"
        download_file(url, lodes_file)
    lodes_data = pd.read_csv(lodes_file)
    return lodes_data

def restrict_to_Baltimore(df, geocode_col):
    df[geocode_col] = column_to_str(df, geocode_col)
    df[(df[geocode_col].str[:5] == '24510') & (df['C000'] != 0)]

    return df[(df[geocode_col].str[:5] == '24510') & (df['C000'] != 0)]

def column_to_str(df, col):
    return df[col].astype(str)

def cumulativeSum(lst):
    return list(accumulate(lst))