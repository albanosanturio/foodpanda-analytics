import pandas as pd


# Show all columns
pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)

# Load
df = pd.read_csv('data/foodpanda_raw.csv')  # wildcard in case filename varies


# Quick overview
print("Shape:", df.shape)
print("\nColumns:", df.columns.tolist())
print("\nData types:\n", df.dtypes)
print("\nFirst few rows:\n", df.head())
print("\nMissing values:\n", df.isnull().sum())
print("\nBasic stats:\n", df.describe())