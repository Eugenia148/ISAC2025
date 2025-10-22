"""
Script to fix the league reference data to include both percentile and raw score averages.
"""

import os
import json
import pandas as pd
import numpy as np

def fix_league_reference():
    """Fix league reference to include both percentile and raw score averages."""
    
    artifacts_dir = "data/processed/striker_artifacts"
    if not os.path.exists(artifacts_dir):
        artifacts_dir = "C:/Users/carls/OneDrive/Dokumente/Uni/05 Semester/Marketing y Estrategia de Deportes/Projekt/Repo/ISAC2025/data/processed/striker_artifacts"
    
    print("Fixing league reference data...")
    
    try:
        # Load the ability scores (raw scores)
        scores_df = pd.read_parquet(os.path.join(artifacts_dir, "ability_scores.parquet"))
        print(f"Loaded {len(scores_df)} players with ability scores")
        
        # Load the percentiles
        percentiles_df = pd.read_parquet(os.path.join(artifacts_dir, "ability_percentiles.parquet"))
        print(f"Loaded {len(percentiles_df)} players with percentiles")
        
        # Calculate median raw scores (for absolute mode)
        raw_score_averages = scores_df.median().to_dict()
        print("Raw score averages:", raw_score_averages)
        
        # Calculate median percentiles (for percentile mode)
        percentile_averages = percentiles_df.median().to_dict()
        print("Percentile averages:", percentile_averages)
        
        # Create new league reference structure
        league_reference = {
            "percentile_averages": percentile_averages,
            "raw_score_averages": raw_score_averages
        }
        
        # Save the updated league reference
        with open(os.path.join(artifacts_dir, "league_reference.json"), 'w') as f:
            json.dump(league_reference, f, indent=2)
        
        print("Updated league_reference.json with both percentile and raw score averages")
        
        # Also update the radar component to handle this new structure
        print("\nYou'll need to update the radar component to use the new structure:")
        print("- For percentiles: league_ref['percentile_averages']")
        print("- For raw scores: league_ref['raw_score_averages']")
        
    except Exception as e:
        print(f"Error fixing league reference: {e}")

if __name__ == "__main__":
    fix_league_reference()
