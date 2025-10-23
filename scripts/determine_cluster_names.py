import sys
import os
sys.path.insert(0, os.getcwd())

import pandas as pd
import numpy as np

# Load data
cluster_df = pd.read_parquet('data/processed/roles/317/player_cluster_probs.parquet')
style_df = pd.read_parquet('data/processed/roles/317/player_style_vectors.parquet')

# Merge
merged = style_df.merge(cluster_df[['player_id', 'predicted_cluster']], on='player_id', how='left')

pca_cols = [c for c in style_df.columns if c.startswith('pca_')]

print("=" * 100)
print("CLUSTER INTERPRETATION BASED ON PCA ANALYSIS")
print("=" * 100)

print("""
Based on PCA loadings:
- PC1: Playmaking (↑) vs Finishing (↓)  | carries, dribbles, key passes vs xG, box touches
- PC2: Pressing (↑) vs Playmaking (↓)   | pressures, regains vs passing ratio, xA
- PC3: Finishing (↑) vs Passing (↓)     | xG, box touches vs passing ratio
""")

cluster_profiles = {}

for cluster_id in [0, 1, 2]:
    cluster_data = merged[merged['predicted_cluster'] == cluster_id]
    
    pc1_mean = cluster_data['pca_1'].mean()
    pc2_mean = cluster_data['pca_2'].mean()
    pc3_mean = cluster_data['pca_3'].mean()
    
    # Interpret
    playmaking = "HIGH" if pc1_mean > 0.5 else "MODERATE" if pc1_mean > -0.5 else "LOW"
    pressing = "HIGH" if pc2_mean > 0.5 else "MODERATE" if pc2_mean > -0.5 else "LOW"
    finishing = "HIGH" if pc3_mean > 0.5 else "MODERATE" if pc3_mean > -0.5 else "LOW"
    
    print(f"\n🔹 CLUSTER {cluster_id} ({len(cluster_data)} players)")
    print("-" * 100)
    print(f"  PC1 (Playmaking vs Finishing): {pc1_mean:+.3f} → {playmaking} Playmaking")
    print(f"  PC2 (Pressing vs Playmaking):  {pc2_mean:+.3f} → {pressing} Pressing")
    print(f"  PC3 (Finishing vs Passing):    {pc3_mean:+.3f} → {finishing} Finishing")
    
    # Suggested name
    if pressing == "HIGH" and playmaking == "LOW":
        suggested_name = "Pressing Striker"
        description = "Leads the press, high defensive intensity, less playmaking"
    elif playmaking == "HIGH" and finishing == "LOW":
        suggested_name = "Link-Up / Complete Striker"
        description = "Excellent playmaker, ball retention, limited finishing"
    elif finishing == "HIGH" and pressing == "LOW" and playmaking == "LOW":
        suggested_name = "Poacher"
        description = "Pure finisher, box occupation, limited pressing/playmaking"
    elif finishing == "HIGH" and playmaking == "MODERATE":
        suggested_name = "Complete Forward"
        description = "Good finisher with playmaking ability"
    elif playmaking == "HIGH":
        suggested_name = "Creator"
        description = "Playmaking-focused striker"
    else:
        suggested_name = "Balanced Striker"
        description = "Balanced profile"
    
    print(f"\n  → SUGGESTED NAME: {suggested_name}")
    print(f"     {description}")
    
    cluster_profiles[cluster_id] = {
        'suggested_name': suggested_name,
        'description': description,
        'pc1': pc1_mean,
        'pc2': pc2_mean,
        'pc3': pc3_mean
    }

print("\n\n" + "=" * 100)
print("UPDATED CLUSTER MAPPING")
print("=" * 100)

mapping = {}
for cluster_id, profile in cluster_profiles.items():
    mapping[str(cluster_id)] = profile['suggested_name']
    print(f"  {cluster_id}: \"{profile['suggested_name']}\"")

print("\n\nProposed cluster_to_role.json:")
import json
print(json.dumps(mapping, indent=2))
