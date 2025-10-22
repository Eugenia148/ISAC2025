#!/usr/bin/env python3
"""
Generate Performance Output artifacts for striker analysis.

This script creates performance metrics artifacts including:
- 5 performance axes with 20 total metrics
- Percentiles and raw values for all metrics
- Axis scores (averaged percentiles per axis)
- Benchmarks (median and p80)
- Min/max ranges for absolute view scaling
"""

import os
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path

# Configuration
MINUTES_THRESHOLD = 600
SEASON = "2024/25"
SEASON_ID = "317"

def create_performance_axes() -> List[Dict[str, Any]]:
    """Define the 5 performance axes and their metrics."""
    return [
        {
            "key": "finishing_output",
            "label": "Finishing Output",
            "description": "Goal scoring and finishing quality",
            "metrics": [
                "touches_box_90",
                "np_xg_90", 
                "np_xg_per_shot",
                "finishing_quality"
            ]
        },
        {
            "key": "chance_creation",
            "label": "Chance Creation",
            "description": "Creating scoring opportunities",
            "metrics": [
                "xa_90",
                "key_passes_90",
                "obv_pass_90",
                "xa_per_shot_assist"
            ]
        },
        {
            "key": "ball_progression_link_play",
            "label": "Ball Progression & Link Play",
            "description": "Ball progression and link-up play",
            "metrics": [
                "deep_progressions_90",
                "passing_ratio",
                "dribble_ratio",
                "obv_dribble_carry_90"
            ]
        },
        {
            "key": "defensive_work_rate",
            "label": "Defensive Work Rate",
            "description": "Defensive contributions and work rate",
            "metrics": [
                "defensive_actions_90",
                "tackles_interceptions_90",
                "aerial_ratio"
            ]
        },
        {
            "key": "overall_impact",
            "label": "Overall Impact",
            "description": "Overall performance and impact",
            "metrics": [
                "npxgxa_90",
                "obv_90",
                "positive_outcome_score"
            ]
        }
    ]

def create_sample_performance_data() -> pd.DataFrame:
    """Create sample performance data for 50 Liga MX strikers."""
    np.random.seed(42)
    
    # Generate sample data for 50 strikers
    n_players = 50
    player_ids = [f"player_{i:03d}" for i in range(1, n_players + 1)]
    
    # Sample data with realistic ranges
    data = {
        'player_id': player_ids,
        'minutes': np.random.randint(600, 3000, n_players),
        
        # Finishing Output metrics
        'touches_box_90': np.random.normal(4.5, 1.5, n_players).clip(0),
        'np_xg_90': np.random.normal(0.35, 0.15, n_players).clip(0),
        'np_xg_per_shot': np.random.normal(0.12, 0.05, n_players).clip(0),
        'np_psxg_90': np.random.normal(0.38, 0.16, n_players).clip(0),
        
        # Chance Creation metrics
        'xa_90': np.random.normal(0.08, 0.04, n_players).clip(0),
        'key_passes_90': np.random.normal(1.2, 0.6, n_players).clip(0),
        'obv_pass_90': np.random.normal(0.15, 0.08, n_players).clip(0),
        
        # Ball Progression & Link Play metrics
        'deep_progressions_90': np.random.normal(3.2, 1.2, n_players).clip(0),
        'passing_ratio': np.random.normal(0.75, 0.15, n_players).clip(0, 1),
        'dribble_ratio': np.random.normal(0.25, 0.15, n_players).clip(0, 1),
        'obv_dribble_carry_90': np.random.normal(0.12, 0.06, n_players).clip(0),
        
        # Defensive Work Rate metrics
        'defensive_actions_90': np.random.normal(8.5, 3.0, n_players).clip(0),
        'tackles_interceptions_90': np.random.normal(2.8, 1.2, n_players).clip(0),
        'aerial_ratio': np.random.normal(0.45, 0.2, n_players).clip(0, 1),
        
        # Overall Impact metrics
        'npxgxa_90': np.random.normal(0.43, 0.18, n_players).clip(0),
        'obv_90': np.random.normal(0.35, 0.15, n_players).clip(0),
        'positive_outcome_score': np.random.normal(0.28, 0.12, n_players).clip(0)
    }
    
    df = pd.DataFrame(data)
    
    # Calculate derived metrics
    df['finishing_quality'] = df['np_psxg_90'] - df['np_xg_90']
    df['xa_per_shot_assist'] = df['xa_90'] / df['key_passes_90'].replace(0, np.nan)
    
    # Clean up derived metrics
    df['finishing_quality'] = df['finishing_quality'].fillna(0)
    df['xa_per_shot_assist'] = df['xa_per_shot_assist'].fillna(0)
    
    return df

def calculate_percentiles(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Calculate percentiles for all metrics."""
    percentiles_df = df[['player_id']].copy()
    
    for metric in metrics:
        if metric in df.columns:
            percentiles_df[f'{metric}_percentile'] = df[metric].rank(pct=True) * 100
    
    return percentiles_df

def calculate_axis_scores(df: pd.DataFrame, axes: List[Dict[str, Any]]) -> pd.DataFrame:
    """Calculate axis scores as average of metric percentiles."""
    axis_scores_df = df[['player_id']].copy()
    
    for axis in axes:
        axis_key = axis['key']
        metrics = axis['metrics']
        
        # Get percentile columns for this axis
        percentile_cols = [f'{metric}_percentile' for metric in metrics if f'{metric}_percentile' in df.columns]
        
        if percentile_cols:
            # Calculate average percentile for this axis
            axis_scores_df[f'{axis_key}_score'] = df[percentile_cols].mean(axis=1)
        else:
            axis_scores_df[f'{axis_key}_score'] = 0
    
    return axis_scores_df

def calculate_benchmarks(df: pd.DataFrame, metrics: List[str]) -> Dict[str, Dict[str, float]]:
    """Calculate median and p80 benchmarks for each metric."""
    benchmarks = {}
    
    for metric in metrics:
        if metric in df.columns:
            benchmarks[metric] = {
                'median': float(df[metric].median()),
                'p80': float(df[metric].quantile(0.8))
            }
    
    return benchmarks

def calculate_minmax(df: pd.DataFrame, metrics: List[str]) -> Dict[str, Dict[str, float]]:
    """Calculate min/max ranges for absolute view scaling."""
    minmax = {}
    
    for metric in metrics:
        if metric in df.columns:
            minmax[metric] = {
                'min': float(df[metric].min()),
                'max': float(df[metric].max())
            }
    
    return minmax

def generate_performance_artifacts():
    """Generate all performance artifacts."""
    print("Generating Performance Output artifacts...")
    
    # Create output directory
    output_dir = Path("data/processed/performance_artifacts")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Define axes
    axes = create_performance_axes()
    
    # Create sample data
    df = create_sample_performance_data()
    
    # Get all metrics
    all_metrics = []
    for axis in axes:
        all_metrics.extend(axis['metrics'])
    
    # Calculate percentiles
    percentiles_df = calculate_percentiles(df, all_metrics)
    
    # Calculate axis scores
    axis_scores_df = calculate_axis_scores(percentiles_df, axes)
    
    # Calculate benchmarks
    benchmarks = calculate_benchmarks(df, all_metrics)
    
    # Calculate min/max
    minmax = calculate_minmax(df, all_metrics)
    
    # Save artifacts
    print(f"Generated artifacts for {len(df)} strikers")
    
    # 1. Performance axes definition
    with open(output_dir / "performance_axes.json", "w") as f:
        json.dump(axes, f, indent=2)
    
    # 2. Performance percentiles
    percentiles_df.to_parquet(output_dir / "performance_percentiles.parquet", index=False)
    
    # 3. Performance axis scores
    axis_scores_df.to_parquet(output_dir / "performance_axis_scores.parquet", index=False)
    
    # 4. Performance benchmarks
    with open(output_dir / "performance_benchmarks.json", "w") as f:
        json.dump(benchmarks, f, indent=2)
    
    # 5. Performance min/max ranges
    with open(output_dir / "performance_minmax.json", "w") as f:
        json.dump(minmax, f, indent=2)
    
    # 6. Configuration
    config = {
        "minutes_threshold": MINUTES_THRESHOLD,
        "season": SEASON,
        "season_id": SEASON_ID,
        "generated_at": "2025-01-27"
    }
    with open(output_dir / "performance_config.json", "w") as f:
        json.dump(config, f, indent=2)
    
    print(f"Artifacts saved to: {output_dir}")
    print(f"Generated {len(axes)} performance axes with {len(all_metrics)} total metrics")

if __name__ == "__main__":
    generate_performance_artifacts()
