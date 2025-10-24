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
from sklearn.metrics.pairwise import euclidean_distances

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
    
    # Add metadata columns for player info lookup
    ability_scores['player_name'] = df['player_name']
    ability_scores['team_name'] = df['team_name'] 
    ability_scores['primary_position'] = df['primary_position']
    
    ability_scores.index = df['player_season_id']
    ability_scores.index.name = 'player_season_id'
    
    print(f"Created ability scores with shape: {ability_scores.shape}")
    print(f"Ability columns: {list(ability_scores.columns)}")
    
    return ability_scores, df

def calculate_percentiles(ability_scores):
    """Calculate percentile rankings for each ability."""
    print("Calculating percentiles...")
    
    # Calculate percentiles only for ability columns (not metadata)
    ability_columns = [axis['key'] for axis in CENTER_BACK_AXES]
    percentiles = ability_scores[ability_columns].copy()
    
    for col in percentiles.columns:
        percentiles[col] = percentiles[col].rank(pct=True) * 100
    
    # Add metadata columns back
    percentiles['player_name'] = ability_scores['player_name']
    percentiles['team_name'] = ability_scores['team_name']
    percentiles['primary_position'] = ability_scores['primary_position']
    
    return percentiles

def calculate_l2_normalized(ability_scores):
    """Calculate L2-normalized ability scores."""
    print("Calculating L2-normalized scores...")
    
    # L2 normalize only ability columns (not metadata)
    ability_columns = [axis['key'] for axis in CENTER_BACK_AXES]
    ability_data = ability_scores[ability_columns].values
    
    # L2 normalize each row (player)
    l2_normalized = normalize(ability_data, norm='l2')
    
    # Create DataFrame
    l2_scores = pd.DataFrame(l2_normalized, 
                             columns=ability_columns,
                             index=ability_scores.index)
    
    # Add metadata columns back
    l2_scores['player_name'] = ability_scores['player_name']
    l2_scores['team_name'] = ability_scores['team_name']
    l2_scores['primary_position'] = ability_scores['primary_position']
    
    return l2_scores

def calculate_zscore_normalized(ability_scores):
    """Calculate Z-score normalized ability scores."""
    print("Calculating Z-score normalized scores...")
    
    # Z-score normalize only ability columns (not metadata)
    ability_columns = [axis['key'] for axis in CENTER_BACK_AXES]
    ability_data = ability_scores[ability_columns].values
    
    scaler = StandardScaler()
    zscore_values = scaler.fit_transform(ability_data)
    
    # Create DataFrame
    zscore_scores = pd.DataFrame(zscore_values, 
                                 columns=ability_columns,
                                 index=ability_scores.index)
    
    # Add metadata columns back
    zscore_scores['player_name'] = ability_scores['player_name']
    zscore_scores['team_name'] = ability_scores['team_name']
    zscore_scores['primary_position'] = ability_scores['primary_position']
    
    return zscore_scores

def create_axis_ranges(ability_scores):
    """Create axis ranges for absolute mode rendering."""
    print("Creating axis ranges...")
    
    axis_ranges = {}
    # Only calculate ranges for ability columns (not metadata)
    ability_columns = [axis['key'] for axis in CENTER_BACK_AXES]
    
    for col in ability_columns:
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

def generate_neighbors_file(l2_scores, output_dir, top_k=10):
    """Generate player_neighbors.parquet for similar players functionality."""
    print("Generating neighbors file...")
    
    # Extract ability columns (not PC columns)
    ability_cols = [axis['key'] for axis in CENTER_BACK_AXES]
    vectors = l2_scores[ability_cols].values
    player_season_ids = l2_scores.index.tolist()
    
    print(f"Computing Euclidean distances for {len(player_season_ids)} players...")
    
    # Compute pairwise Euclidean distance
    distance_matrix = euclidean_distances(vectors)
    
    # Build neighbor records
    neighbor_records = []
    
    for i, anchor_id in enumerate(player_season_ids):
        # Get distances to all other players
        distances = distance_matrix[i]
        
        # Create list of (distance, player_id) pairs
        distance_pairs = [(dist, player_season_ids[j]) for j, dist in enumerate(distances)]
        
        # Sort by distance (ascending) and take top_k+1 (including self)
        distance_pairs.sort(key=lambda x: x[0])
        top_neighbors = distance_pairs[1:top_k+1]  # Exclude self (distance=0)
        
        # Add neighbor records
        for rank, (distance, neighbor_id) in enumerate(top_neighbors, 1):
            # Convert distance to similarity (0-1)
            # Euclidean distance on L2-normalized vectors ranges from 0 to ~2
            # Convert to similarity: similarity = (2 - distance) / 2
            max_distance = 2.0  # Approximate max for L2-normalized vectors
            similarity = max(0, (max_distance - distance) / max_distance)
            similarity = round(similarity, 3)  # Round to 3 decimal places
            
            neighbor_records.append({
                'anchor_player_season_id': anchor_id,
                'neighbor_player_season_id': neighbor_id,
                'euclidean_distance': distance,
                'similarity': similarity,
                'rank': rank
            })
    
    # Create DataFrame
    neighbors_df = pd.DataFrame(neighbor_records)
    
    # Save to parquet
    neighbors_path = os.path.join(output_dir, "player_neighbors.parquet")
    neighbors_df.to_parquet(neighbors_path, index=False)
    
    print(f"✅ Generated {len(neighbors_df)} neighbor records for {len(player_season_ids)} players")
    print(f"✅ Saved to: {neighbors_path}")
    
    return neighbors_df

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
    
    # Generate and save neighbors file
    generate_neighbors_file(l2_scores, output_dir)
    
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
