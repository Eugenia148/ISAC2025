"""
Script to generate tactical profile artifacts from the striker PCA analysis.
This script should be run after the striker PCA clustering notebook to create
the necessary artifacts for the tactical profile system.
"""

import os
import json
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, MinMaxScaler
from sklearn.decomposition import PCA
from statsbombpy import sb
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def generate_striker_artifacts():
    """Generate all artifacts needed for the tactical profile system."""
    
    # Create artifacts directory
    artifacts_dir = "data/processed/striker_artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("Generating striker tactical profile artifacts...")
    
    # 1. Generate ability axes
    generate_ability_axes(artifacts_dir)
    
    # 2. Generate ability scores and percentiles
    generate_ability_data(artifacts_dir)
    
    # 3. Generate league reference
    generate_league_reference(artifacts_dir)
    
    # 4. Generate axis ranges
    generate_axis_ranges(artifacts_dir)
    
    print("Artifacts generated successfully!")


def generate_ability_axes(artifacts_dir: str):
    """Generate ability axes definitions."""
    
    axes = [
        {
            "key": "Progressive_Play",
            "label": "Progressive Play",
            "description": "Ball progression & link play"
        },
        {
            "key": "Finishing_BoxPresence", 
            "label": "Finishing & Box Presence",
            "description": "Goal scoring and box positioning"
        },
        {
            "key": "Pressing_WorkRate",
            "label": "Pressing Work Rate", 
            "description": "Defensive pressure and work rate"
        },
        {
            "key": "Finishing_Efficiency",
            "label": "Finishing Efficiency",
            "description": "Shot conversion and efficiency"
        },
        {
            "key": "Dribbling_RiskTaking",
            "label": "Dribbling & Risk-Taking",
            "description": "Ball carrying and risk taking"
        },
        {
            "key": "DecisionMaking_Balance",
            "label": "Decision Making & Balance",
            "description": "Decision making and balance"
        }
    ]
    
    with open(os.path.join(artifacts_dir, "ability_axes.json"), 'w') as f:
        json.dump(axes, f, indent=2)
    
    print("Generated ability_axes.json")


def generate_ability_data(artifacts_dir: str):
    """Generate ability scores and percentiles from PCA analysis."""
    
    # This is a simplified version - in practice, you would run the full PCA analysis
    # from the notebook here. For now, we'll create sample data.
    
    print("Note: This is generating sample data. Run the full PCA analysis from the notebook for real data.")
    
    # Sample data structure
    ability_labels = [
        "Progressive_Play",
        "Finishing_BoxPresence", 
        "Pressing_WorkRate",
        "Finishing_Efficiency",
        "Dribbling_RiskTaking",
        "DecisionMaking_Balance"
    ]
    
    # Generate sample data for demonstration
    np.random.seed(42)
    n_players = 50
    
    # Sample ability scores (normalized 0-1)
    ability_scores_data = {
        'player_season_id': [f"player_{i}_317" for i in range(n_players)],
        **{label: np.random.uniform(0, 1, n_players) for label in ability_labels}
    }
    
    ability_scores_df = pd.DataFrame(ability_scores_data)
    ability_scores_df.set_index('player_season_id', inplace=True)
    
    # Generate percentiles (0-100)
    percentile_data = {
        'player_season_id': [f"player_{i}_317" for i in range(n_players)],
        **{label: np.random.uniform(0, 100, n_players) for label in ability_labels}
    }
    
    percentiles_df = pd.DataFrame(percentile_data)
    percentiles_df.set_index('player_season_id', inplace=True)
    
    # Save as parquet files
    ability_scores_df.to_parquet(os.path.join(artifacts_dir, "ability_scores.parquet"))
    percentiles_df.to_parquet(os.path.join(artifacts_dir, "ability_percentiles.parquet"))
    
    print("Generated ability_scores.parquet and ability_percentiles.parquet")


def generate_league_reference(artifacts_dir: str):
    """Generate league reference data."""
    
    # League average (50th percentile for all axes)
    league_ref = {
        "Progressive_Play": 50.0,
        "Finishing_BoxPresence": 50.0,
        "Pressing_WorkRate": 50.0,
        "Finishing_Efficiency": 50.0,
        "Dribbling_RiskTaking": 50.0,
        "DecisionMaking_Balance": 50.0
    }
    
    with open(os.path.join(artifacts_dir, "league_reference.json"), 'w') as f:
        json.dump(league_ref, f, indent=2)
    
    print("Generated league_reference.json")


def generate_axis_ranges(artifacts_dir: str):
    """Generate axis ranges for absolute mode rendering."""
    
    # Default ranges for normalized scores (0-1)
    axis_ranges = {
        "Progressive_Play": {"min": 0.0, "max": 1.0},
        "Finishing_BoxPresence": {"min": 0.0, "max": 1.0},
        "Pressing_WorkRate": {"min": 0.0, "max": 1.0},
        "Finishing_Efficiency": {"min": 0.0, "max": 1.0},
        "Dribbling_RiskTaking": {"min": 0.0, "max": 1.0},
        "DecisionMaking_Balance": {"min": 0.0, "max": 1.0}
    }
    
    with open(os.path.join(artifacts_dir, "axis_ranges.json"), 'w') as f:
        json.dump(axis_ranges, f, indent=2)
    
    print("Generated axis_ranges.json")


if __name__ == "__main__":
    generate_striker_artifacts()
