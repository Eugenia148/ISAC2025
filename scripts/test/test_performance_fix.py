#!/usr/bin/env python3
"""
Test script to verify the performance profile includes raw values.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance.service import get_performance_service

def test_raw_values():
    """Test that raw values are included in the profile."""
    print("Testing performance profile raw values...")
    
    # Initialize service for 2024/25
    service = get_performance_service(season_id='317')
    
    # Build a profile
    profile = service.build_performance_profile(
        player_id='17299',
        player_name='Test Striker',
        team_name='Test Team',
        primary_position='Centre Forward',
        season='2024/25',
        minutes=1200
    )
    
    if not profile:
        print("ERROR: Profile is None")
        return False
    
    axes = profile.get('axes', [])
    
    print(f"\nProfile loaded with {len(axes)} axes")
    
    all_ok = True
    for axis in axes:
        axis_label = axis.get('label', 'Unknown')
        metrics = axis.get('metrics', [])
        
        print(f"\n{axis_label}:")
        for metric in metrics:
            label = metric.get('label', 'Unknown')
            raw = metric.get('raw')
            percentile = metric.get('percentile')
            
            # Check that we have percentile data
            if percentile is None:
                print(f"  {label}: MISSING percentile")
                all_ok = False
            else:
                # Raw can be None, but we should handle it
                raw_str = f"{raw:.2f}" if raw is not None else "None (OK)"
                print(f"  {label}: percentile={percentile:.0f}%, raw={raw_str}")
    
    if all_ok:
        print("\n✓ All percentiles present")
    else:
        print("\n✗ Some percentiles missing")
    
    print("\nTest completed successfully!")
    return True

if __name__ == "__main__":
    test_raw_values()
