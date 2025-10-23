"""
Simple test for season-specific functionality.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profiles.loader import get_loader

def test_season_simple():
    """Test season-specific data loading."""
    
    print("=== Testing Season-Specific Data Loading ===")
    
    loader = get_loader()
    loader._load_artifacts_if_needed()
    
    # Test with a known player ID from the data
    test_player_id = "27796"
    
    print(f"Testing with player ID: {test_player_id}")
    
    # Test different seasons
    seasons = ["108", "235", "281", "317"]
    
    for season in seasons:
        print(f"\nSeason {season}:")
        
        # Test ability scores
        ability_scores = loader.get_player_ability_scores(test_player_id, season)
        if ability_scores:
            print(f"  Ability scores: Found {len(ability_scores)} dimensions")
            sample_key = list(ability_scores.keys())[0]
            print(f"  Sample value ({sample_key}): {ability_scores[sample_key]:.3f}")
        else:
            print(f"  Ability scores: Not found")
        
        # Test percentiles
        percentiles = loader.get_player_percentiles(test_player_id, season)
        if percentiles:
            print(f"  Percentiles: Found {len(percentiles)} dimensions")
            sample_key = list(percentiles.keys())[0]
            print(f"  Sample value ({sample_key}): {percentiles[sample_key]:.1f}%")
        else:
            print(f"  Percentiles: Not found")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_season_simple()
