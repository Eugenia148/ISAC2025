#!/usr/bin/env python3
"""
Test script for the new radial bar performance visualization.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ui.components.performance_radar import AXIS_CONFIG

def test_visualization_config():
    """Test the visualization configuration."""
    print("Testing radial bar visualization configuration...")
    
    print("\n=== Axis Configuration ===")
    for key, config in AXIS_CONFIG.items():
        print(f"\n{config['label']} (order {config['order']})")
        print(f"  Colors: {config['colors']}")
    
    print("\n=== Angle Calculation ===")
    # Each axis gets 72 degrees (360/5)
    for i in range(5):
        axis_angle = i * 72
        print(f"Axis {i}: {axis_angle}°")
    
    print("\n=== Metric Angle Offsets ===")
    for i, metric in enumerate(["Metric 1", "Metric 2", "Metric 3", "Metric 4"]):
        offsets = [-6, 0, 6, 12]
        if i < len(offsets):
            print(f"{metric}: {offsets[i]}°")
    
    print("\n=== Test Result ===")
    print("All configuration parameters loaded successfully!")
    print("\nVisualization features:")
    print("  - 5 axes with color-coded sectors")
    print("  - 2-4 metric bars per axis with angular offsets")
    print("  - Dotted benchmark rays (median, p80)")
    print("  - Value pills at bar tips")
    print("  - Concentric grid rings at 20%, 40%, 60%, 80%, 100%")
    print("  - Axis titles positioned outside the rim")
    print("  - Minutes warning badge for <600' players")

if __name__ == "__main__":
    test_visualization_config()
