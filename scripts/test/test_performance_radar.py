#!/usr/bin/env python3
"""
Test script for the Performance Output radar implementation.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance.service import get_performance_service
from core.performance.loader import PerformanceLoader

def test_performance_service():
    """Test the performance service functionality."""
    print("Testing Performance Service...")
    
    # Test service initialization
    service = get_performance_service()
    print("Service initialized successfully")
    
    # Test loader
    loader = service.loader
    print(f"Loader initialized with artifacts_dir: {loader.artifacts_dir}")
    
    # Test artifacts loading
    if loader.is_loaded():
        print("Artifacts loaded successfully")
        
        # Test axes
        axes = loader.get_axes()
        print(f"Found {len(axes)} performance axes:")
        for axis in axes:
            print(f"  - {axis['label']} ({axis['key']})")
        
        # Test sample player
        sample_player_id = "player_001"
        metric_data = loader.get_player_metric_row(sample_player_id)
        axis_scores = loader.get_player_axis_scores(sample_player_id)
        
        if metric_data:
            print(f"Found metric data for {sample_player_id}: {len(metric_data)} metrics")
        else:
            print(f"No metric data found for {sample_player_id}")
        
        if axis_scores:
            print(f"Found axis scores for {sample_player_id}: {len(axis_scores)} axes")
        else:
            print(f"No axis scores found for {sample_player_id}")
        
        # Test building performance profile
        profile = service.build_performance_profile(
            player_id=sample_player_id,
            player_name="Test Striker",
            team_name="Test Team",
            primary_position="Centre Forward",
            season="2024/25",
            minutes=1200
        )
        
        if profile:
            print("Performance profile built successfully")
            print(f"  - Player: {profile['player']['name']}")
            print(f"  - Team: {profile['player']['team']}")
            print(f"  - Season: {profile['season']}")
            print(f"  - Axes: {len(profile['axes'])}")
            
            for axis in profile['axes']:
                print(f"    - {axis['label']}: {axis['score']:.1f}")
        else:
            print("Failed to build performance profile")
        
        # Test benchmarks
        benchmarks = loader.get_benchmarks("touches_box_90")
        if benchmarks:
            print(f"Found benchmarks for touches_box_90: {benchmarks}")
        else:
            print("No benchmarks found for touches_box_90")
        
        # Test minmax
        minmax = loader.get_minmax("touches_box_90")
        if minmax:
            print(f"Found minmax for touches_box_90: {minmax}")
        else:
            print("No minmax found for touches_box_90")
        
    else:
        print("Artifacts not loaded")
    
    print("\nPerformance Service test completed!")

if __name__ == "__main__":
    test_performance_service()
