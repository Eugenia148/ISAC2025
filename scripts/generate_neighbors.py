"""
Generate missing player_neighbors.parquet from existing role artifacts.

This script reads the PCA vectors from existing per-season artifacts
and builds the multi-season neighbor similarity data.
"""

import os
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

# Paths
ARTIFACTS_ROOT = "data/processed/roles"

def generate_neighbors(top_k=10):
    """Build and save multi-season neighbor similarity data."""
    
    all_season_data = []
    
    # Load each season's data
    for season_dir in os.listdir(ARTIFACTS_ROOT):
        season_path = os.path.join(ARTIFACTS_ROOT, season_dir)
        
        if not os.path.isdir(season_path):
            continue
        
        try:
            season_id = int(season_dir)
        except ValueError:
            continue
        
        # Load style vectors
        style_vec_path = os.path.join(season_path, "player_style_vectors.parquet")
        if not os.path.exists(style_vec_path):
            print(f"⚠️ No style vectors for season {season_id}")
            continue
        
        style_df = pd.read_parquet(style_vec_path)
        print(f"✓ Loaded season {season_id} with {len(style_df)} players")
        
        all_season_data.append((season_id, style_df))
    
    if not all_season_data:
        print("❌ No season data found!")
        return
    
    print(f"\n📊 Building neighbor similarity from {len(all_season_data)} seasons...\n")
    
    # Combine all PCA vectors
    combined_vectors = []
    combined_metadata = []
    
    for season_id, style_df in all_season_data:
        pca_cols = [c for c in style_df.columns if c.startswith('pca_')]
        vectors = style_df[pca_cols].values
        
        for position, (idx, row) in enumerate(style_df.iterrows()):
            combined_vectors.append(vectors[position])
            combined_metadata.append({
                'player_id': int(row['player_id']),
                'season_id': int(row['season_id']),
            })
    
    combined_vectors = np.array(combined_vectors)
    print(f"🔍 Computing similarity for {len(combined_vectors)} player-seasons...")
    
    # Compute pairwise cosine similarity
    similarity_matrix = cosine_similarity(combined_vectors)
    
    # Extract top-K neighbors for each row
    neighbors_list = []
    
    for i in range(len(combined_metadata)):
        anchor = combined_metadata[i]
        sims = similarity_matrix[i]
        
        # Get indices sorted by similarity (excluding self at index i)
        neighbor_indices = np.argsort(-sims)[1:top_k+1]
        
        for neighbor_idx in neighbor_indices:
            neighbor = combined_metadata[neighbor_idx]
            sim_score = float(sims[neighbor_idx])
            
            neighbors_list.append({
                'anchor_player_id': anchor['player_id'],
                'anchor_season_id': anchor['season_id'],
                'neighbor_player_id': neighbor['player_id'],
                'neighbor_season_id': neighbor['season_id'],
                'cosine_sim': sim_score
            })
    
    neighbors_df = pd.DataFrame(neighbors_list)
    neighbors_path = os.path.join(ARTIFACTS_ROOT, "player_neighbors.parquet")
    neighbors_df.to_parquet(neighbors_path, index=False)
    
    print(f"\n✅ Saved {len(neighbors_df)} neighbor records to {neighbors_path}")


if __name__ == "__main__":
    generate_neighbors(top_k=10)
