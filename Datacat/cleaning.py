
import pandas as pd

def missing_val_drop(df):

    df = df.dropna()

    return df

def fill_missing_val(df):

    df= df.fillna(df.mean(numeric_only=True))

    return df

def outliers(df):
    numeric_columns = df.select_dtypes(include="number").columns

    for column in numeric_columns:
        # Skip empty or constant columns.
        if df[column].nunique() <= 1:
            continue

        values = df[column]
        z_scores = (values - values.mean()) / values.std(ddof=0)
        mask = abs(z_scores) > 3

        for row_index, value in df.loc[mask, column].items():
            print(f"Row: {row_index} | Column: {column} | Value: {value}")

def duplicates(df):
    df= df.drop_duplicates()

    return df
