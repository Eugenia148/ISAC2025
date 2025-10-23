import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import numpy as np
from sklearn.decomposition import PCA
import pickle

# Load data for player 26353
cluster_df = pd.read_parquet('data/processed/roles/317/player_cluster_probs.parquet')
style_df = pd.read_parquet('data/processed/roles/317/player_style_vectors.parquet')

player_id = 26353

# Get cluster info
player_cluster = cluster_df[cluster_df['player_id'] == player_id]
if player_cluster.empty:
    print(f"Player {player_id} not found in cluster data")
    exit(1)

row = player_cluster.iloc[0]
print(f"Player {player_id} cluster assignment:")
print(f"  Cluster 0 (Link-Up): {row['cluster_0']:.3f}")
print(f"  Cluster 1 (Pressing): {row['cluster_1']:.3f}")
print(f"  Cluster 2 (Poacher): {row['cluster_2']:.3f}")
print(f"  Predicted cluster: {int(row['predicted_cluster'])}")

# Get style vectors
player_style = style_df[style_df['player_id'] == player_id]
if player_style.empty:
    print(f"Player {player_id} not found in style vectors")
    exit(1)

pca_row = player_style.iloc[0]
print(f"\nPlayer {player_id} PCA components:")
for i in range(1, 7):
    col = f'pca_{i}'
    print(f"  PCA {i}: {pca_row[col]:.3f}")

# Load PCA model to understand what each component represents
print("\nChecking PCA model explained variance...")
with open('data/processed/roles/317/pca_model.pkl', 'rb') as f:
    pca_model = pickle.load(f)
    print(f"  Explained variance ratio: {pca_model.explained_variance_ratio_}")
    print(f"  Cumulative variance: {np.cumsum(pca_model.explained_variance_ratio_)}")

# Load features to see what PCA is built on
import json
with open('data/processed/roles/317/features.json', 'r') as f:
    features = json.load(f)['features']
    print(f"\nFeatures used in PCA ({len(features)}):")
    for i, feat in enumerate(features):
        print(f"  {i+1}. {feat}")
