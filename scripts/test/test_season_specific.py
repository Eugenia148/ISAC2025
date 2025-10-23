"""
Test script for season-specific tactical profiles.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profiles.loader import get_loader
from core.profiles.service import get_service

def test_season_specific():
    """Test season-specific tactical profile functionality."""
    
    print("=== Testing Season-Specific Tactical Profiles ===")
    
    # Test with a known player ID
    test_player_id = "27796"  # From the data we saw earlier
    
    print(f"\n1. Testing with player ID: {test_player_id}")
    
    # Get service
    service = get_service()
    
    # Test different seasons
    seasons = ["2021/22", "2022/23", "2023/24", "2024/25"]
    
    for season in seasons:
        print(f"\n2. Testing season: {season}")
        
        profile = service.build_striker_profile(
            player_id=test_player_id,
            player_name="Test Player",
            team_name="Test Team",
            primary_position="Centre Forward",
            season=season
        )
        
        if profile:
            print(f"   Profile found for {season}")
            print(f"   Ability scores: {len(profile['ability_scores'])} dimensions")
            print(f"   Percentiles: {len(profile['percentiles'])} dimensions")
            
            # Show sample values
            if profile['ability_scores']:
                sample_key = list(profile['ability_scores'].keys())[0]
                print(f"   Sample ability score ({sample_key}): {profile['ability_scores'][sample_key]:.3f}")
            if profile['percentiles']:
                sample_key = list(profile['percentiles'].keys())[0]
                print(f"   Sample percentile ({sample_key}): {profile['percentiles'][sample_key]:.1f}%")
        else:
            print(f"   No profile found for {season}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_season_specific()
