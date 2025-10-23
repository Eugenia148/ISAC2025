import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import numpy as np

# Load all necessary data
cluster_df = pd.read_parquet('data/processed/roles/317/player_cluster_probs.parquet')
style_df = pd.read_parquet('data/processed/roles/317/player_style_vectors.parquet')

# Load raw metrics if available
try:
    perf_df = pd.read_parquet('data/processed/performance_artifacts_317/performance_raw_metrics.parquet')
    print("Using performance raw metrics...")
except:
    print("Performance metrics not available")
    perf_df = None

# Merge cluster with style data
merged = style_df.merge(cluster_df[['player_id', 'predicted_cluster']], on='player_id', how='left')

# Get PCA components
pca_cols = [c for c in style_df.columns if c.startswith('pca_')]

print("=" * 80)
print("CLUSTER ANALYSIS - PCA Component Averages")
print("=" * 80)

for cluster_id in [0, 1, 2]:
    cluster_data = merged[merged['predicted_cluster'] == cluster_id]
    print(f"\n🔹 CLUSTER {cluster_id}: '{['Link-Up', 'Pressing', 'Poacher'][cluster_id]}' ({len(cluster_data)} players)")
    print("-" * 80)
    
    for col in pca_cols:
        mean_val = cluster_data[col].mean()
        std_val = cluster_data[col].std()
        print(f"  {col:15s}: {mean_val:8.3f} (±{std_val:.3f})")
    
    print(f"  Top players in this cluster:")
    top_players = cluster_data.nlargest(3, 'predicted_cluster')[['player_id', 'player_name', 'minutes']]
    for idx, row in cluster_data.nlargest(3, 'minutes').iterrows():
        print(f"    - {row['player_name']} ({int(row['minutes'])} min)")

print("\n" + "=" * 80)
print("CLUSTER INTERPRETATION")
print("=" * 80)
print("""
Looking at PCA components:
- Negative PCA values = Low on that component
- Positive PCA values = High on that component

Since PCA 1 explains 30% of variance and is computed from the 14 features,
we need to check which features load heavily on each component.
""")

# Example: Check specific player
print("\nExample Player Analysis: Ángel Baltazar Sepúlveda Sánchez (ID 26353)")
player_data = merged[merged['player_id'] == 26353]
if not player_data.empty:
    p = player_data.iloc[0]
    print(f"  Cluster: {int(p['predicted_cluster'])} ({['Link-Up', 'Pressing', 'Poacher'][int(p['predicted_cluster'])]}")
    print(f"  Minutes: {int(p['minutes'])}")
    print(f"  PCA Components:")
    for col in pca_cols:
        print(f"    {col}: {p[col]:.3f}")
