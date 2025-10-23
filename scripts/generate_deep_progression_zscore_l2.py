"""
Generate Z-score and L2-normalized scores for Deep Progression Unit tactical profiles.

This script:
1. Loads raw PCA scores
2. Computes Z-score parameters (mean/std per season)
3. Computes L2-normalized vectors (row-wise, unit length)
4. Saves zscore_params.json, ability_scores_zscore.parquet, ability_scores_l2.parquet
"""

import pandas as pd
import numpy as np
from pathlib import Path
import json

# Configuration
PCA_SCORES_FILE = Path("data/processed/deep_progression_artifacts/pca_scores_player_season.csv")
ARTIFACT_DIR = Path("data/processed/deep_progression_artifacts")
ABILITY_COLUMNS = [f"PC{i}" for i in range(1, 8)]

# Z-score capping (for visualization readability)
Z_CAP_MIN = -2.5
Z_CAP_MAX = 2.5

def load_pca_scores():
    """Load PCA scores from CSV."""
    df = pd.read_csv(PCA_SCORES_FILE)
    print(f"✓ Loaded {len(df)} player-season records")
    return df

def compute_zscore_params(df):
    """
    Compute Z-score parameters (mean and std) per season for each PC.
    
    Returns:
        dict: {season_id: {PC1: {mean, std}, PC2: {...}, ...}}
    """
    zscore_params = {}
    
    for season_id in sorted(df['season_id'].unique()):
        season_df = df[df['season_id'] == season_id]
        season_params = {}
        
        for pc in ABILITY_COLUMNS:
            season_params[pc] = {
                "mean": float(season_df[pc].mean()),
                "std": float(season_df[pc].std())
            }
        
        zscore_params[int(season_id)] = season_params
        print(f"  ✓ Season {season_id}: computed params for {len(ABILITY_COLUMNS)} PCs")
    
    return zscore_params

def compute_zscore_normalized(df, zscore_params):
    """
    Apply Z-score normalization per season and add capping.
    
    Returns:
        DataFrame with player_season_id as index and Z-score columns
    """
    df_zscore = df.copy()
    
    # Create player_season_id
    df_zscore['player_season_id'] = df_zscore['player_id'].astype(str) + '_' + df_zscore['season_id'].astype(str)
    
    # Apply Z-score normalization per season
    for season_id in df_zscore['season_id'].unique():
        season_mask = df_zscore['season_id'] == season_id
        params = zscore_params[int(season_id)]
        
        for pc in ABILITY_COLUMNS:
            mean = params[pc]['mean']
            std = params[pc]['std']
            
            # Z-score: (x - mean) / std
            if std > 0:
                df_zscore.loc[season_mask, pc] = (df_zscore.loc[season_mask, pc] - mean) / std
            else:
                df_zscore.loc[season_mask, pc] = 0.0
    
    # Cap Z-scores for visualization readability
    for pc in ABILITY_COLUMNS:
        df_zscore[pc] = df_zscore[pc].clip(lower=Z_CAP_MIN, upper=Z_CAP_MAX)
    
    # Select relevant columns and set index
    result_df = df_zscore[['player_season_id', 'player_id', 'season_id'] + ABILITY_COLUMNS].copy()
    result_df = result_df.set_index('player_season_id')
    
    print(f"✓ Computed Z-score normalized data ({len(result_df)} rows, capped to [{Z_CAP_MIN}, {Z_CAP_MAX}])")
    return result_df

def compute_l2_normalized(df):
    """
    Apply L2 (row-wise) normalization to make unit-length 7D vectors.
    
    Returns:
        DataFrame with player_season_id as index and L2-normalized columns
    """
    df_l2 = df.copy()
    
    # Create player_season_id
    df_l2['player_season_id'] = df_l2['player_id'].astype(str) + '_' + df_l2['season_id'].astype(str)
    
    # Extract ability matrix
    ability_matrix = df_l2[ABILITY_COLUMNS].values
    
    # Compute L2 norm for each row
    norms = np.linalg.norm(ability_matrix, axis=1, keepdims=True)
    
    # Avoid division by zero
    norms[norms == 0] = 1.0
    
    # Normalize
    ability_matrix_l2 = ability_matrix / norms
    
    # Replace in dataframe
    for i, pc in enumerate(ABILITY_COLUMNS):
        df_l2[pc] = ability_matrix_l2[:, i]
    
    # Select relevant columns and set index
    result_df = df_l2[['player_season_id', 'player_id', 'season_id'] + ABILITY_COLUMNS].copy()
    result_df = result_df.set_index('player_season_id')
    
    print(f"✓ Computed L2-normalized data ({len(result_df)} rows)")
    return result_df

def save_artifacts(zscore_params, df_zscore, df_l2):
    """Save all artifacts."""
    # 1. Z-score parameters
    zscore_params_path = ARTIFACT_DIR / "zscore_params.json"
    with open(zscore_params_path, 'w') as f:
        json.dump({
            "z_cap_min": Z_CAP_MIN,
            "z_cap_max": Z_CAP_MAX,
            "seasons": zscore_params
        }, f, indent=2)
    print(f"✓ Saved Z-score parameters: {zscore_params_path}")
    
    # 2. Z-score normalized scores
    zscore_path = ARTIFACT_DIR / "ability_scores_zscore.parquet"
    df_zscore.to_parquet(zscore_path, index=True)
    print(f"✓ Saved Z-score abilities: {zscore_path}")
    
    # 3. L2-normalized scores
    l2_path = ARTIFACT_DIR / "ability_scores_l2.parquet"
    df_l2.to_parquet(l2_path, index=True)
    print(f"✓ Saved L2-normalized abilities: {l2_path}")

def main():
    print("=" * 80)
    print("GENERATING DEEP PROGRESSION Z-SCORE & L2 ARTIFACTS")
    print("=" * 80)
    
    # Load data
    df = load_pca_scores()
    
    # Compute Z-score parameters (per season)
    print("\n" + "=" * 80)
    print("COMPUTING Z-SCORE PARAMETERS (PER SEASON)")
    print("=" * 80)
    zscore_params = compute_zscore_params(df)
    
    # Compute Z-score normalized data
    print("\n" + "=" * 80)
    print("COMPUTING Z-SCORE NORMALIZED DATA")
    print("=" * 80)
    df_zscore = compute_zscore_normalized(df, zscore_params)
    
    # Compute L2-normalized data
    print("\n" + "=" * 80)
    print("COMPUTING L2-NORMALIZED DATA")
    print("=" * 80)
    df_l2 = compute_l2_normalized(df)
    
    # Save artifacts
    print("\n" + "=" * 80)
    print("SAVING ARTIFACTS")
    print("=" * 80)
    save_artifacts(zscore_params, df_zscore, df_l2)
    
    print("\n" + "=" * 80)
    print("✅ ARTIFACTS GENERATED SUCCESSFULLY")
    print("=" * 80)
    print(f"\nGenerated 3 artifacts in: {ARTIFACT_DIR}")
    print("  • zscore_params.json")
    print("  • ability_scores_zscore.parquet")
    print("  • ability_scores_l2.parquet")
    print(f"\nTotal player-seasons: {len(df)}")
    print(f"Seasons: {sorted(df['season_id'].unique())}")
    print(f"Z-score capping: [{Z_CAP_MIN}, {Z_CAP_MAX}]")
    print("\n✅ Ready for Z-score and L2 tactical profile radars!")

if __name__ == "__main__":
    main()

