"""
Helper functions to save role artifacts from striker_pca_clustering notebook.

Mirrors the approach used for radar chart artifacts - saves already-computed
PCA vectors and GMM results directly without recomputing.
"""

import os
import json
import pickle
import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity


# Fixed role mappings
CLUSTER_TO_ROLE = {
    0: "Link-Up / Complete Striker",
    1: "Pressing Striker",
    2: "Poacher"
}

ROLE_DESCRIPTIONS = {
    "Link-Up / Complete Striker": "Connects play, drops in, combines efficiently and contributes to buildup.",
    "Pressing Striker": "Leads the press, initiates defensive actions and disrupts buildup.",
    "Poacher": "Focuses on box occupation and finishing, limited link play."
}


def save_role_artifacts(
    pca_vectors,
    gmm_model,
    posteriors,
    assignments,
    striker_df_with_season,
    artifacts_root: str = "data/processed/roles"
):
    """
    Save role artifacts directly from already-computed PCA/GMM results.
    
    Args:
        pca_vectors: 6D PCA vectors (N x 6)
        gmm_model: Fitted GMM model
        posteriors: GMM posteriors (N x 3)
        assignments: GMM cluster assignments (N,)
        striker_df_with_season: DataFrame with columns: player_id, player_name, team_id, team_name, season_id, minutes
        artifacts_root: Root directory for artifacts
    """
    os.makedirs(artifacts_root, exist_ok=True)
    
    # Get unique seasons from the data
    seasons = striker_df_with_season['season_id'].unique()
    
    print(f"Saving role artifacts for {len(seasons)} seasons...\n")
    
    all_season_data = []
    
    for season_id in sorted(seasons):
        season_dir = os.path.join(artifacts_root, str(season_id))
        os.makedirs(season_dir, exist_ok=True)
        
        # Filter to this season
        season_mask = striker_df_with_season['season_id'] == season_id
        season_strikers = striker_df_with_season[season_mask].copy()
        season_pca = pca_vectors[season_mask]
        season_posteriors = posteriors[season_mask]
        season_assignments = assignments[season_mask]
        
        # Create player_style_vectors.parquet
        style_vectors_df = season_strikers[['player_id', 'player_name', 'team_id', 'team_name']].copy()
        style_vectors_df['season_id'] = season_id
        if 'player_season_minutes' in season_strikers.columns:
            style_vectors_df['minutes'] = season_strikers['player_season_minutes'].values
        else:
            style_vectors_df['minutes'] = 0
        
        for i in range(season_pca.shape[1]):
            style_vectors_df[f'pca_{i+1}'] = season_pca[:, i]
        
        style_vectors_df.to_parquet(
            os.path.join(season_dir, "player_style_vectors.parquet"),
            index=False
        )
        
        # Create player_cluster_probs.parquet
        cluster_probs_df = season_strikers[['player_id']].copy()
        cluster_probs_df['season_id'] = season_id
        
        for i in range(season_posteriors.shape[1]):
            cluster_probs_df[f'cluster_{i}'] = season_posteriors[:, i]
        
        cluster_probs_df['predicted_cluster'] = season_assignments
        cluster_probs_df.to_parquet(
            os.path.join(season_dir, "player_cluster_probs.parquet"),
            index=False
        )
        
        # Save GMM model (same for all seasons)
        with open(os.path.join(season_dir, "gmm_model.pkl"), "wb") as f:
            pickle.dump(gmm_model, f)
        
        # Save configs
        with open(os.path.join(season_dir, "cluster_to_role.json"), "w") as f:
            json.dump(CLUSTER_TO_ROLE, f, indent=2)
        
        with open(os.path.join(season_dir, "role_descriptions.json"), "w") as f:
            json.dump(ROLE_DESCRIPTIONS, f, indent=2)
        
        print(f"✓ Saved season {season_id} artifacts: {len(season_strikers)} strikers")
        
        # Collect for multi-season neighbors
        all_season_data.append((season_id, style_vectors_df, cluster_probs_df))
    
    # Save multi-season neighbors
    _save_multiseasson_neighbors(all_season_data, artifacts_root)
    
    # Save global config
    _save_global_config(artifacts_root)


def _save_multiseasson_neighbors(
    all_season_data: list,
    artifacts_root: str = "data/processed/roles",
    top_k: int = 10
):
    """Build and save multi-season neighbor similarity data."""
    
    # Combine all PCA vectors
    combined_vectors = []
    combined_metadata = []
    
    for season_id, style_df, _ in all_season_data:
        pca_cols = [c for c in style_df.columns if c.startswith('pca_')]
        vectors = style_df[pca_cols].values
        
        for position, (idx, row) in enumerate(style_df.iterrows()):
            combined_vectors.append(vectors[position])
            combined_metadata.append({
                'player_id': row['player_id'],
                'season_id': row['season_id'],
            })
    
    combined_vectors = np.array(combined_vectors)
    print(f"\nBuilding neighbor similarity ({len(combined_vectors)} player-seasons)...")
    
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
    neighbors_path = os.path.join(artifacts_root, "player_neighbors.parquet")
    neighbors_df.to_parquet(neighbors_path, index=False)
    
    print(f"✓ Saved {len(neighbors_df)} neighbor records")


def _save_global_config(
    artifacts_root: str = "data/processed/roles",
    minutes_threshold: int = 500,
    n_components_pca: int = 6,
    n_clusters_gmm: int = 3,
    top_k_neighbors: int = 10
):
    """Save global configuration file."""
    config = {
        "cluster_to_role": CLUSTER_TO_ROLE,
        "role_descriptions": ROLE_DESCRIPTIONS,
        "minutes_threshold": minutes_threshold,
        "n_components_pca": n_components_pca,
        "n_clusters_gmm": n_clusters_gmm,
        "top_k_neighbors": top_k_neighbors
    }
    
    config_path = os.path.join(artifacts_root, "config.json")
    with open(config_path, "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"✓ Saved global config")
