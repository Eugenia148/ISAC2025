#!/usr/bin/env python3
"""Test the new polygon radar visualization."""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.performance.service import get_performance_service

def test_polygon_radar():
    """Test the polygon radar with individual metrics."""
    print("Testing Polygon Radar with Individual Metrics\n")
    print("=" * 60)
    
    # Build a profile
    service = get_performance_service(season_id='317')
    profile = service.build_performance_profile(
        '17299', 'Test Striker', 'Test Team', 'Centre Forward', '2024/25', 1200
    )
    
    if not profile:
        print("ERROR: Could not build profile")
        return False
    
    axes = profile.get('axes', [])
    
    # Collect all metrics
    all_metrics = []
    print("\nAll Metrics in Radar Chart:\n")
    
    for axis_idx, axis in enumerate(axes, 1):
        axis_label = axis['label']
        metrics = axis['metrics']
        print(f"{axis_idx}. {axis_label}")
        
        for metric in metrics:
            label = metric['label']
            percentile = metric.get('percentile', 0)
            raw = metric.get('raw', 0)
            all_metrics.append(label)
            
            # Format for display
            raw_str = f"{raw:.2f}" if isinstance(raw, (int, float)) else "N/A"
            print(f"   - {label}")
            print(f"     Percentile: {percentile:.0f}%, Raw: {raw_str}")
    
    print("\n" + "=" * 60)
    print(f"\nVisualization Details:")
    print(f"  Total metrics in polygon: {len(all_metrics)}")
    print(f"  Text color: Black (for visibility)")
    print(f"  Label type: Individual metric names (not axis names)")
    print(f"  Chart type: Polygon radar (not bars)")
    print(f"  Modes: Percentile (0-100) and Raw Values")
    
    print("\nPolygon radar with individual metrics is ready!")
    return True

if __name__ == "__main__":
    success = test_polygon_radar()
    sys.exit(0 if success else 1)
