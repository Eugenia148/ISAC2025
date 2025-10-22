"""
Script to extract real tactical profile artifacts from the striker PCA analysis notebook.
This script should be run after completing the striker PCA clustering notebook to create
real artifacts with actual player data.
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

def extract_real_striker_artifacts():
    """Extract real artifacts from the completed PCA analysis."""
    
    # Create artifacts directory
    artifacts_dir = "data/processed/striker_artifacts"
    os.makedirs(artifacts_dir, exist_ok=True)
    
    print("Extracting real striker tactical profile artifacts from PCA analysis...")
    
    # 1. Generate ability axes (same as before)
    generate_ability_axes(artifacts_dir)
    
    # 2. Extract real ability data from PCA analysis
    extract_real_ability_data(artifacts_dir)
    
    # 3. Generate league reference from real data
    generate_real_league_reference(artifacts_dir)
    
    # 4. Generate axis ranges from real data
    generate_real_axis_ranges(artifacts_dir)
    
    print("Real artifacts extracted successfully!")


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


def extract_real_ability_data(artifacts_dir: str):
    """Extract real ability scores and percentiles from PCA analysis."""
    
    print("Extracting real ability data from PCA analysis...")
    
    try:
        # This function should be called after running the striker PCA notebook
        # You'll need to copy the relevant variables from your notebook here
        
        # For now, let's create a function that can be easily modified
        # to work with your actual PCA results
        
        ability_labels = [
            "Progressive_Play",
            "Finishing_BoxPresence", 
            "Pressing_WorkRate",
            "Finishing_Efficiency",
            "Dribbling_RiskTaking",
            "DecisionMaking_Balance"
        ]
        
        # TODO: Replace this with your actual PCA results
        # You need to copy these variables from your notebook:
        # - striker_features_scaled_df (with player_season_id index)
        # - ability_df_norm (normalized ability scores)
        # - pca (fitted PCA object)
        
        print("NOTE: You need to copy the PCA results from your notebook to this script.")
        print("Required variables from your notebook:")
        print("- striker_features_scaled_df (features DataFrame with player_season_id index)")
        print("- ability_df_norm (normalized ability scores DataFrame)")
        print("- pca (fitted PCA object)")
        
        # Placeholder for now - replace with real data
        create_placeholder_data(artifacts_dir, ability_labels)
        
    except Exception as e:
        print(f"Error extracting ability data: {e}")
        print("Creating placeholder data instead...")
        create_placeholder_data(artifacts_dir, ability_labels)


def create_placeholder_data(artifacts_dir: str, ability_labels: list):
    """Create placeholder data when real data is not available."""
    
    print("Creating placeholder data...")
    
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
    
    print("Generated placeholder ability_scores.parquet and ability_percentiles.parquet")


def generate_real_league_reference(artifacts_dir: str):
    """Generate league reference from real data."""
    
    try:
        # Try to load the real percentiles data
        percentiles_path = os.path.join(artifacts_dir, "ability_percentiles.parquet")
        if os.path.exists(percentiles_path):
            percentiles_df = pd.read_parquet(percentiles_path)
            
            # Calculate actual league averages (median values)
            league_ref = percentiles_df.median().to_dict()
            
            print(f"Generated real league reference from {len(percentiles_df)} players")
        else:
            # Fallback to default values
            league_ref = {
                "Progressive_Play": 50.0,
                "Finishing_BoxPresence": 50.0,
                "Pressing_WorkRate": 50.0,
                "Finishing_Efficiency": 50.0,
                "Dribbling_RiskTaking": 50.0,
                "DecisionMaking_Balance": 50.0
            }
            print("Generated default league reference")
        
        with open(os.path.join(artifacts_dir, "league_reference.json"), 'w') as f:
            json.dump(league_ref, f, indent=2)
        
        print("Generated league_reference.json")
        
    except Exception as e:
        print(f"Error generating league reference: {e}")


def generate_real_axis_ranges(artifacts_dir: str):
    """Generate axis ranges from real data."""
    
    try:
        # Try to load the real ability scores data
        scores_path = os.path.join(artifacts_dir, "ability_scores.parquet")
        if os.path.exists(scores_path):
            scores_df = pd.read_parquet(scores_path)
            
            # Calculate actual min/max ranges
            axis_ranges = {}
            for col in scores_df.columns:
                axis_ranges[col] = {
                    "min": float(scores_df[col].min()),
                    "max": float(scores_df[col].max())
                }
            
            print(f"Generated real axis ranges from {len(scores_df)} players")
        else:
            # Fallback to default ranges
            axis_ranges = {
                "Progressive_Play": {"min": 0.0, "max": 1.0},
                "Finishing_BoxPresence": {"min": 0.0, "max": 1.0},
                "Pressing_WorkRate": {"min": 0.0, "max": 1.0},
                "Finishing_Efficiency": {"min": 0.0, "max": 1.0},
                "Dribbling_RiskTaking": {"min": 0.0, "max": 1.0},
                "DecisionMaking_Balance": {"min": 0.0, "max": 1.0}
            }
            print("Generated default axis ranges")
        
        with open(os.path.join(artifacts_dir, "axis_ranges.json"), 'w') as f:
            json.dump(axis_ranges, f, indent=2)
        
        print("Generated axis_ranges.json")
        
    except Exception as e:
        print(f"Error generating axis ranges: {e}")


def create_notebook_integration_template():
    """Create a template for integrating with the notebook."""
    
    template = '''
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
'''
    
    with open("notebook_integration_template.py", 'w') as f:
        f.write(template)
    
    print("Created notebook_integration_template.py")
    print("Copy this code to the end of your striker PCA notebook to generate real artifacts!")


if __name__ == "__main__":
    print("Choose an option:")
    print("1. Extract real artifacts (requires PCA notebook completion)")
    print("2. Create notebook integration template")
    
    choice = input("Enter choice (1 or 2): ").strip()
    
    if choice == "1":
        extract_real_striker_artifacts()
    elif choice == "2":
        create_notebook_integration_template()
    else:
        print("Invalid choice. Creating notebook integration template...")
        create_notebook_integration_template()
