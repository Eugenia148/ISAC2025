"""
Test script for the tactical profile system.
"""

import sys
import os

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.profiles.loader import get_loader
from core.profiles.service import get_service


def test_tactical_profile_system():
    """Test the tactical profile system components."""
    
    print("Testing Tactical Profile System...")
    
    # Test loader
    print("\n1. Testing Loader...")
    loader = get_loader()
    
    axes = loader.get_axes()
    print(f"   - Loaded {len(axes)} ability axes")
    for axis in axes:
        print(f"     * {axis.key}: {axis.label}")
    
    # Test ability scores
    ability_scores = loader.get_player_ability_scores("player_0_317")
    print(f"   - Sample ability scores: {ability_scores}")
    
    # Test percentiles
    percentiles = loader.get_player_percentiles("player_0_317")
    print(f"   - Sample percentiles: {percentiles}")
    
    # Test league reference
    league_ref = loader.get_league_reference()
    print(f"   - League reference: {league_ref}")
    
    # Test service
    print("\n2. Testing Service...")
    service = get_service()
    
    # Test striker detection
    print(f"   - Is Centre Forward a striker? {service.is_striker('Centre Forward')}")
    print(f"   - Is Left Wing a striker? {service.is_striker('Left Wing')}")
    
    # Test profile building
    profile = service.build_striker_profile(
        player_id="player_0_317",
        player_name="Test Striker",
        team_name="Test Team",
        primary_position="Centre Forward",
        season="2024/25"
    )
    
    if profile:
        print(f"   - Built profile for: {profile['player_name']}")
        print(f"   - Profile has {len(profile['ability_scores'])} ability scores")
        print(f"   - Profile has {len(profile['percentiles'])} percentiles")
    else:
        print("   - Failed to build profile")
    
    print("\nTactical Profile System test completed!")


if __name__ == "__main__":
    test_tactical_profile_system()
