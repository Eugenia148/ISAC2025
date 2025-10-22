# Add this code to the end of your striker PCA clustering notebook
# to generate real artifacts:

import os
import json
import pandas as pd
import numpy as np

def generate_tactical_profile_artifacts():
    """Generate artifacts from the completed PCA analysis."""
    
    # Create artifacts directory
    artifacts_dir = "data/processed/striker_artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("Generating tactical profile artifacts from PCA analysis...")
    
    # 1. Generate ability axes
    axes = [
        {"key": "Progressive_Play", "label": "Progressive Play", "description": "Ball progression & link play"},
        {"key": "Finishing_BoxPresence", "label": "Finishing & Box Presence", "description": "Goal scoring and box positioning"},
        {"key": "Pressing_WorkRate", "label": "Pressing Work Rate", "description": "Defensive pressure and work rate"},
        {"key": "Finishing_Efficiency", "label": "Finishing Efficiency", "description": "Shot conversion and efficiency"},
        {"key": "Dribbling_RiskTaking", "label": "Dribbling & Risk-Taking", "description": "Ball carrying and risk taking"},
        {"key": "DecisionMaking_Balance", "label": "Decision Making & Balance", "description": "Decision making and balance"}
    ]
    
    with open(os.path.join(artifacts_dir, "ability_axes.json"), 'w') as f:
        json.dump(axes, f, indent=2)
    
    # 2. Save ability scores (normalized)
    ability_scores_df = ability_df_norm.copy()
    ability_scores_df.to_parquet(os.path.join(artifacts_dir, "ability_scores.parquet"))
    
    # 3. Calculate percentiles
    percentiles_data = {}
    for col in ability_df_norm.columns:
        percentiles_data[col] = ability_df_norm[col].rank(pct=True) * 100
    
    percentiles_df = pd.DataFrame(percentiles_data, index=ability_df_norm.index)
    percentiles_df.to_parquet(os.path.join(artifacts_dir, "ability_percentiles.parquet"))
    
    # 4. Generate league reference (median values)
    league_ref = percentiles_df.median().to_dict()
    with open(os.path.join(artifacts_dir, "league_reference.json"), 'w') as f:
        json.dump(league_ref, f, indent=2)
    
    # 5. Generate axis ranges
    axis_ranges = {}
    for col in ability_df_norm.columns:
        axis_ranges[col] = {
            "min": float(ability_df_norm[col].min()),
            "max": float(ability_df_norm[col].max())
        }
    
    with open(os.path.join(artifacts_dir, "axis_ranges.json"), 'w') as f:
        json.dump(axis_ranges, f, indent=2)
    
    print(f"Generated artifacts for {len(ability_df_norm)} strikers")
    print("Artifacts saved to:", artifacts_dir)

# Run the function
generate_tactical_profile_artifacts()
