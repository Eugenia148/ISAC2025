#!/usr/bin/env python3
"""
Convert Center Back CSV artifacts to standard parquet format.

This script transforms the center back clustering results from CSV format
to match the standardized parquet structure used by other positions.
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler
from sklearn.preprocessing import normalize

# Season name to ID mapping
SEASON_MAPPING = {
    "2021/2022": 108,
    "2022/2023": 235,
    "2023/2024": 281,
    "2024/2025": 317
}

# Center back ability axes based on ACTUAL PCA loadings analysis
CENTER_BACK_AXES = [
    {
        "key": "Build_Up_Distribution",
        "label": "Build-Up & Distribution",
        "description": "Open play passes, xG buildup, and ball progression",
        "pca_loadings": {
            "PC1": "+0.466 (op_passes_90)",
            "PC1": "+0.388 (xgbuildup_90)", 
            "PC1": "+0.394 (op_xgbuildup_90)"
        }
    },
    {
        "key": "Defensive_Actions",
        "label": "Defensive Actions",
        "description": "Interceptions, tackles, and defensive actions per 90",
        "pca_loadings": {
            "PC2": "+0.479 (interceptions_90)",
            "PC2": "+0.558 (padj_interceptions_90)",
            "PC2": "+0.282 (tackles_90)"
        }
    },
    {
        "key": "Aerial_Dominance",
        "label": "Aerial Dominance",
        "description": "Aerial duels won and aerial success rate",
        "pca_loadings": {
            "PC3": "+0.471 (aerial_wins_90)",
            "PC3": "+0.233 (aerial_ratio)",
            "PC3": "+0.260 (interceptions_90)"
        }
    },
    {
        "key": "Aerial_Clearances",
        "label": "Aerial & Clearances",
        "description": "Aerial duels, clearances, and defensive actions",
        "pca_loadings": {
            "PC4": "+0.435 (aerial_wins_90)",
            "PC4": "+0.423 (clearance_90)",
            "PC4": "+0.352 (defensive_actions_90)"
        }
    },
    {
        "key": "Progressive_Passing",
        "label": "Progressive Passing",
        "description": "Forward passes, long balls, and xG buildup",
        "pca_loadings": {
            "PC5": "+0.427 (forward_pass_proportion)",
            "PC5": "+0.456 (long_ball_ratio)",
            "PC5": "+0.435 (op_xgbuildup_90)"
        }
    },
    {
        "key": "Shot_Blocking_Retention",
        "label": "Shot Blocking & Retention",
        "description": "Shot blocking and ball retention passing",
        "pca_loadings": {
            "PC6": "+0.823 (blocks_per_shot)",
            "PC6": "+0.247 (backward_pass_proportion)",
            "PC6": "+0.073 (defensive_actions_90)"
        }
    }
]

def create_player_season_id(player_id, season_name):
    """Create player_season_id from player_id and season_name."""
    season_id = SEASON_MAPPING.get(season_name)
    if season_id is None:
        raise ValueError(f"Unknown season: {season_name}")
    return f"{player_id}_{season_id}"

def load_center_back_data():
    """Load and process the center back CSV data."""
    print("Loading center back CSV data...")
    
    # Read the CSV file
    csv_path = "notebooks/center_back_clusters_pca_gmm.csv"
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"Center back CSV not found: {csv_path}")
    
    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} center back records")
    
    # Create player_season_id
    df['player_season_id'] = df.apply(
        lambda row: create_player_season_id(row['player_id'], row['season_name']), 
        axis=1
    )
    
    # Extract PC columns as ability scores
    pc_columns = ['PC1', 'PC2', 'PC3', 'PC4', 'PC5', 'PC6']
    ability_columns = [axis['key'] for axis in CENTER_BACK_AXES]
    
    # Map PC columns to ability names
    ability_scores = df[pc_columns].copy()
    ability_scores.columns = ability_columns
    ability_scores.index = df['player_season_id']
    ability_scores.index.name = 'player_season_id'
    
    print(f"Created ability scores with shape: {ability_scores.shape}")
    print(f"Ability columns: {list(ability_scores.columns)}")
    
    return ability_scores, df

def calculate_percentiles(ability_scores):
    """Calculate percentile rankings for each ability."""
    print("Calculating percentiles...")
    
    percentiles = ability_scores.copy()
    for col in percentiles.columns:
        percentiles[col] = percentiles[col].rank(pct=True) * 100
    
    return percentiles

def calculate_l2_normalized(ability_scores):
    """Calculate L2-normalized ability scores."""
    print("Calculating L2-normalized scores...")
    
    # L2 normalize each row (player)
    l2_scores = ability_scores.copy()
    l2_values = normalize(ability_scores.values, norm='l2')
    l2_scores.iloc[:, :] = l2_values
    
    return l2_scores

def calculate_zscore_normalized(ability_scores):
    """Calculate Z-score normalized ability scores."""
    print("Calculating Z-score normalized scores...")
    
    scaler = StandardScaler()
    zscore_values = scaler.fit_transform(ability_scores.values)
    zscore_scores = ability_scores.copy()
    zscore_scores.iloc[:, :] = zscore_values
    
    return zscore_scores

def create_axis_ranges(ability_scores):
    """Create axis ranges for absolute mode rendering."""
    print("Creating axis ranges...")
    
    axis_ranges = {}
    for col in ability_scores.columns:
        axis_ranges[col] = {
            "min": float(ability_scores[col].min()),
            "max": float(ability_scores[col].max())
        }
    
    return axis_ranges

def create_league_reference():
    """Create league reference scores (50th percentile for all axes)."""
    print("Creating league reference...")
    
    league_reference = {}
    for axis in CENTER_BACK_AXES:
        league_reference[axis['key']] = 50.0
    
    return league_reference

def save_artifacts(ability_scores, percentiles, l2_scores, zscore_scores, 
                  axis_ranges, league_reference, output_dir):
    """Save all artifacts to the output directory."""
    print(f"Saving artifacts to {output_dir}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save parquet files
    ability_scores.to_parquet(os.path.join(output_dir, "ability_scores.parquet"))
    percentiles.to_parquet(os.path.join(output_dir, "ability_percentiles.parquet"))
    l2_scores.to_parquet(os.path.join(output_dir, "ability_scores_l2.parquet"))
    zscore_scores.to_parquet(os.path.join(output_dir, "ability_scores_zscore.parquet"))
    
    # Save JSON files
    with open(os.path.join(output_dir, "ability_axes.json"), 'w') as f:
        json.dump(CENTER_BACK_AXES, f, indent=2)
    
    with open(os.path.join(output_dir, "axis_ranges.json"), 'w') as f:
        json.dump(axis_ranges, f, indent=2)
    
    with open(os.path.join(output_dir, "league_reference.json"), 'w') as f:
        json.dump(league_reference, f, indent=2)
    
    print("✅ All artifacts saved successfully!")

def main():
    """Main conversion function."""
    print("🛡️ Converting Center Back artifacts to parquet format...")
    
    try:
        # Load data
        ability_scores, original_df = load_center_back_data()
        
        # Calculate different score types
        percentiles = calculate_percentiles(ability_scores)
        l2_scores = calculate_l2_normalized(ability_scores)
        zscore_scores = calculate_zscore_normalized(ability_scores)
        
        # Create metadata
        axis_ranges = create_axis_ranges(ability_scores)
        league_reference = create_league_reference()
        
        # Save artifacts
        output_dir = "data/processed/center_back_artifacts"
        save_artifacts(ability_scores, percentiles, l2_scores, zscore_scores,
                      axis_ranges, league_reference, output_dir)
        
        # Print summary
        print("\n📊 Conversion Summary:")
        print(f"  • Players: {len(ability_scores)}")
        print(f"  • Abilities: {len(ability_scores.columns)}")
        print(f"  • Output directory: {output_dir}")
        print(f"  • Files created: 7 (4 parquet + 3 JSON)")
        
        # Verify structure
        print("\n🔍 Verification:")
        print(f"  • ability_scores shape: {ability_scores.shape}")
        print(f"  • Index name: {ability_scores.index.name}")
        print(f"  • Sample index: {ability_scores.index[0]}")
        print(f"  • Sample values: {ability_scores.iloc[0].to_dict()}")
        
    except Exception as e:
        print(f"❌ Error during conversion: {e}")
        raise

if __name__ == "__main__":
    main()
