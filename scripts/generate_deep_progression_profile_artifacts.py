"""
Generate tactical profile artifacts for Deep Progression Unit players.
Creates ability_scores.parquet, ability_percentiles.parquet, axis_ranges.json, and league_reference.json
"""

import pandas as pd
import json
import numpy as np
from pathlib import Path

# Paths
ARTIFACT_DIR = Path("data/processed/deep_progression_artifacts")
PCA_SCORES_FILE = ARTIFACT_DIR / "pca_scores_player_season.csv"

# Ability columns (PC1-PC7)
ABILITY_COLUMNS = [f"PC{i}" for i in range(1, 8)]

def load_pca_scores():
    """Load PCA scores from CSV."""
    df = pd.read_csv(PCA_SCORES_FILE)
    print(f"✓ Loaded {len(df)} player-season records")
    return df

def create_ability_scores_parquet(df):
    """Create ability_scores.parquet with raw PC scores."""
    # Create player_season_id column (format: player_id_season_id)
    df['player_season_id'] = df['player_id'].astype(str) + '_' + df['season_id'].astype(str)
    
    # Select relevant columns and set player_season_id as index
    scores_df = df[['player_season_id', 'player_id', 'season_id'] + ABILITY_COLUMNS].copy()
    scores_df = scores_df.set_index('player_season_id')
    
    # Save to parquet (with index)
    output_path = ARTIFACT_DIR / "ability_scores.parquet"
    scores_df.to_parquet(output_path, index=True)
    print(f"✓ Created ability_scores.parquet ({len(scores_df)} rows)")
    
    return scores_df

def create_ability_percentiles_parquet(df):
    """Create ability_percentiles.parquet with percentile rankings."""
    # Create player_season_id column (format: player_id_season_id)
    df['player_season_id'] = df['player_id'].astype(str) + '_' + df['season_id'].astype(str)
    
    percentiles_df = df[['player_season_id', 'player_id', 'season_id']].copy()
    
    # Calculate percentile for each PC
    for pc in ABILITY_COLUMNS:
        percentiles_df[pc] = df[pc].rank(pct=True) * 100
    
    # Set player_season_id as index
    percentiles_df = percentiles_df.set_index('player_season_id')
    
    # Save to parquet (with index)
    output_path = ARTIFACT_DIR / "ability_percentiles.parquet"
    percentiles_df.to_parquet(output_path, index=True)
    print(f"✓ Created ability_percentiles.parquet ({len(percentiles_df)} rows)")
    
    return percentiles_df

def create_axis_ranges(df):
    """Create axis_ranges.json with min/max for each PC."""
    ranges = {}
    
    for pc in ABILITY_COLUMNS:
        ranges[pc] = {
            "min": float(df[pc].min()),
            "max": float(df[pc].max()),
            "mean": float(df[pc].mean()),
            "std": float(df[pc].std())
        }
    
    # Save to JSON
    output_path = ARTIFACT_DIR / "axis_ranges.json"
    with open(output_path, 'w') as f:
        json.dump(ranges, f, indent=2)
    
    print(f"✓ Created axis_ranges.json")
    return ranges

def create_league_reference(df):
    """Create league_reference.json with league averages."""
    reference = {
        "raw_score_averages": {},
        "metadata": {
            "cohort": "Deep Progression Unit (Full-backs + Midfielders)",
            "n_players": int(len(df)),
            "seasons": sorted(df['season_id'].unique().tolist())
        }
    }
    
    for pc in ABILITY_COLUMNS:
        reference["raw_score_averages"][pc] = float(df[pc].mean())
    
    # Save to JSON
    output_path = ARTIFACT_DIR / "league_reference.json"
    with open(output_path, 'w') as f:
        json.dump(reference, f, indent=2)
    
    print(f"✓ Created league_reference.json")
    return reference

def main():
    """Main execution."""
    print("="*80)
    print("GENERATING DEEP PROGRESSION PROFILE ARTIFACTS")
    print("="*80)
    
    # Load data
    df = load_pca_scores()
    
    # Create artifacts
    print("\n" + "="*80)
    print("CREATING ARTIFACTS")
    print("="*80)
    
    scores_df = create_ability_scores_parquet(df)
    percentiles_df = create_ability_percentiles_parquet(df)
    ranges = create_axis_ranges(df)
    reference = create_league_reference(df)
    
    # Summary
    print("\n" + "="*80)
    print("✅ ARTIFACTS GENERATED SUCCESSFULLY")
    print("="*80)
    print(f"\nGenerated 4 artifacts in: {ARTIFACT_DIR}")
    print("  • ability_scores.parquet")
    print("  • ability_percentiles.parquet")
    print("  • axis_ranges.json")
    print("  • league_reference.json")
    print(f"\nTotal player-seasons: {len(df)}")
    print(f"Seasons: {sorted(df['season_id'].unique().tolist())}")
    print("\n✅ Ready for tactical profile radar charts!")

if __name__ == "__main__":
    main()

