"""
Debug script to check player selection and tactical profile data.
"""

import sys
import os
import pandas as pd

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profiles.loader import get_loader
from core.profiles.service import get_service

def debug_player_selection():
    """Debug player selection and tactical profile data."""
    
    print("=== DEBUG: Player Selection and Tactical Profile ===")
    
    # Test with the specific player mentioned
    test_player_name = "Diber Armando Cambindo Abonia"
    test_player_id = "12345"  # This would be the actual player ID from the API
    
    print(f"\n1. Testing with player: {test_player_name}")
    print(f"   Player ID: {test_player_id}")
    
    # Check loader
    print("\n2. Checking loader...")
    loader = get_loader()
    
    # Force load the artifacts
    loader._load_artifacts_if_needed()
    
    # Check what player IDs are available in the data
    try:
        ability_scores = loader._ability_scores
        if ability_scores is not None and not ability_scores.empty:
            print(f"   Available player IDs in ability scores: {list(ability_scores.index)[:5]}...")
            print(f"   Total players in ability scores: {len(ability_scores)}")
        else:
            print("   No ability scores data loaded")
    except Exception as e:
        print(f"   Error loading ability scores: {e}")
    
    try:
        percentiles = loader._percentiles
        if percentiles is not None and not percentiles.empty:
            print(f"   Available player IDs in percentiles: {list(percentiles.index)[:5]}...")
            print(f"   Total players in percentiles: {len(percentiles)}")
        else:
            print("   No percentiles data loaded")
    except Exception as e:
        print(f"   Error loading percentiles: {e}")
    
    # Test service
    print("\n3. Testing service...")
    service = get_service()
    
    # Test striker detection
    print(f"   Is Centre Forward a striker? {service.is_striker('Centre Forward')}")
    print(f"   Is Left Wing a striker? {service.is_striker('Left Wing')}")
    
    # Test profile building
    print(f"\n4. Testing profile building for {test_player_name}...")
    profile = service.build_striker_profile(
        player_id=test_player_id,
        player_name=test_player_name,
        team_name="Test Team",
        primary_position="Centre Forward",
        season="2024/25"
    )
    
    if profile:
        print(f"   Profile built successfully!")
        print(f"   Player: {profile['player_name']}")
        print(f"   Ability scores: {len(profile['ability_scores'])} dimensions")
        print(f"   Percentiles: {len(profile['percentiles'])} dimensions")
    else:
        print(f"   Failed to build profile")
        print(f"   This means the player ID {test_player_id} was not found in the data")
    
    # Test with a known sample player ID
    print(f"\n5. Testing with sample player ID...")
    sample_profile = service.build_striker_profile(
        player_id="player_0_317",
        player_name="Sample Player",
        team_name="Sample Team",
        primary_position="Centre Forward",
        season="2024/25"
    )
    
    if sample_profile:
        print(f"   Sample profile built successfully!")
        print(f"   Player: {sample_profile['player_name']}")
        print(f"   Ability scores: {sample_profile['ability_scores']}")
    else:
        print(f"   Failed to build sample profile")
    
    print("\n=== DEBUG COMPLETE ===")


if __name__ == "__main__":
    debug_player_selection()
