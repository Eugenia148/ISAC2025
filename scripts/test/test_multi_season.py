"""
Test season-specific functionality with a multi-season player.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profiles.service import get_service

def test_multi_season_player():
    """Test with a player who has data for multiple seasons."""
    
    print("=== Testing Multi-Season Player ===")
    
    # Test with player 20041 who has data for all 4 seasons
    test_player_id = "20041"
    
    print(f"Testing with player ID: {test_player_id}")
    print("This player has data for all 4 seasons: 2021/22, 2022/23, 2023/24, 2024/25")
    
    # Get service
    service = get_service()
    
    # Test different seasons
    seasons = ["2021/22", "2022/23", "2023/24", "2024/25"]
    
    for season in seasons:
        print(f"\n--- Season: {season} ---")
        
        profile = service.build_striker_profile(
            player_id=test_player_id,
            player_name="Test Player",
            team_name="Test Team",
            primary_position="Centre Forward",
            season=season
        )
        
        if profile:
            print(f"Profile found for {season}")
            print(f"Ability scores: {len(profile['ability_scores'])} dimensions")
            print(f"Percentiles: {len(profile['percentiles'])} dimensions")
            
            # Show sample values
            if profile['ability_scores']:
                sample_key = list(profile['ability_scores'].keys())[0]
                print(f"Sample ability score ({sample_key}): {profile['ability_scores'][sample_key]:.3f}")
            if profile['percentiles']:
                sample_key = list(profile['percentiles'].keys())[0]
                print(f"Sample percentile ({sample_key}): {profile['percentiles'][sample_key]:.1f}%")
        else:
            print(f"No profile found for {season}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_multi_season_player()
