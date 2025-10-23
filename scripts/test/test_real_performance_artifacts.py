#!/usr/bin/env python3
"""
Test script for the real performance artifacts.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance.service import get_performance_service

def test_real_performance_artifacts():
    """Test the real performance artifacts."""
    print("Testing Real Performance Artifacts...")
    
    # Test for each season
    seasons = {
        "2024/25": "317",
        "2023/24": "281", 
        "2022/23": "235",
        "2021/22": "108"
    }
    
    for season_name, season_id in seasons.items():
        print(f"\nTesting {season_name} (season_id: {season_id})...")
        
        try:
            # Initialize service
            service = get_performance_service(season_id)
            print(f"Service initialized for {season_name}")
            
            # Test building a profile (using a sample player ID)
            # We'll use a generic test since we don't know specific player IDs
            profile = service.build_performance_profile(
                player_id="17299",  # Sample player ID from 2024/25
                player_name="Test Striker",
                team_name="Test Team",
                primary_position="Centre Forward",
                season=season_name,
                minutes=1200
            )
            
            if profile:
                print(f"Profile built successfully for {season_name}")
                print(f"  - Player: {profile['player']['name']}")
                print(f"  - Season: {profile['season']}")
                print(f"  - Axes: {len(profile['axes'])}")
                
                # Show axis scores
                for axis in profile['axes']:
                    print(f"    - {axis['label']}: {axis['score']:.1f}")
            else:
                print(f"No profile data available for {season_name}")
                
        except Exception as e:
            print(f"Error testing {season_name}: {e}")
    
    print("\nReal performance artifacts test completed!")

if __name__ == "__main__":
    test_real_performance_artifacts()
