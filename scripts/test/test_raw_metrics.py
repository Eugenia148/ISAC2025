#!/usr/bin/env python3
"""Test that raw metrics are included in profiles."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance.service import get_performance_service

def test_raw_metrics():
    """Test raw metrics availability."""
    print("Testing raw metrics in performance profiles...\n")
    
    service = get_performance_service('317')
    profile = service.build_performance_profile(
        '17299', 'Test', 'Team', 'Centre Forward', '2024/25', 1200
    )
    
    axes = profile.get('axes', [])
    
    print(f"Profile contains {len(axes)} axes\n")
    
    for axis in axes:
        label = axis['label']
        metrics = axis['metrics']
        
        print(f"{label}:")
        for m in metrics:
            raw = m.get('raw')
            pct = m.get('percentile')
            raw_str = f"{raw:.2f}" if raw is not None else "None"
            print(f"  {m['label']}: raw={raw_str}, percentile={pct}")
        print()
    
    print("Test complete!")

if __name__ == "__main__":
    test_raw_metrics()
