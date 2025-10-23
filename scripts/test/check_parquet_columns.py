import pandas as pd

# Check what columns are in the player_cluster_probs
df = pd.read_parquet('data/processed/roles/317/player_cluster_probs.parquet')
print("Columns in player_cluster_probs.parquet:")
print(df.columns.tolist())
print("\nFirst few rows:")
print(df.head())
print("\nDataframe info:")
print(df.info())
