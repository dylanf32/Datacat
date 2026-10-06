import pandas as pd
import numpy as np

def overview(df):
    df.info()
    print("\nTotal cells",df.size)
    print("\n Number of rows",df.shape)
    print("First five rows:",df.head(n=5))


def missing_val_drop(df):
    missing = df.isna().sum()
    print("\n Missing values per column:")
    print(missing)

    return missing

    


def duplicates(df):

    duplicate_count = df.duplicated().sum()
    print(f"\nDuplicate rows: {duplicate_count}")
    return duplicate_count

def describe_data(df):

    summary = df.describe()
    print("\nSummary statistics:")
    print(summary)
    
    return summary