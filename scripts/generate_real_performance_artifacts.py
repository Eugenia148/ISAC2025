#!/usr/bin/env python3
"""
Generate Performance Output artifacts with real data from StatsBomb API.

This script creates performance metrics artifacts using actual player season stats
from multiple seasons, including:
- 5 performance axes with 18 total metrics
- Percentiles and raw values for all metrics
- Axis scores (averaged percentiles per axis)
- Benchmarks (median and p80)
- Min/max ranges for absolute view scaling
"""

import os
import sys
import json
import pandas as pd
import numpy as np
from typing import Dict, List, Any, Optional
from pathlib import Path

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.client import StatsBombClient

# Configuration
MINUTES_THRESHOLD = 600
COMPETITION_ID = 73  # Liga MX
SEASONS = {
    "2024/25": "317",
    "2023/24": "281", 
    "2022/23": "235",
    "2021/22": "108"
}

def create_performance_axes() -> List[Dict[str, Any]]:
    """Define the 5 performance axes and their metrics."""
    return [
        {
            "key": "finishing_output",
            "label": "Finishing Output",
            " harnessing": "Goal scoring and finishing quality",
            "metrics": [
                "touches_inside_box_90",
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
                "tackles_and_interceptions_90",
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

def is_striker(position: str) -> bool:
    """Check if a player is a striker based on position."""
    striker_positions = {
        'Centre Forward', 'Left Centre Forward', 'Right Centre Forward'
    }
    return position in striker_positions

def extract_performance_metrics(df: pd.DataFrame) -> pd.DataFrame:
    """Extract and calculate performance metrics from player season stats."""
    
    # Create a copy to avoid modifying original
    metrics_df = df.copy()
    
    # Calculate derived metrics
    metrics_df['finishing_quality'] = metrics_df['player_season_np_psxg_90'] - metrics_df['player_season_np_xg_90']
    
    # Calculate xA per shot assist (handle division by zero)
    metrics_df['xa_per_shot_assist'] = np.where(
        metrics_df['player_season_key_passes_90'] > 0,
        metrics_df['player_season_xa_90'] / metrics_df['player_season_key_passes_90'],
        np.nan
    )
    
    # Rename columns to match our metric names
    column_mapping = {
        'player_season_touches_inside_box_90': 'touches_inside_box_90',
        'player_season_np_xg_90': 'np_xg_90',
        'player_season_np_xg_per_shot': 'np_xg_per_shot',
        'player_season_xa_90': 'xa_90',
        'player_season_key_passes_90': 'key_passes_90',
        'player_season_obv_pass_90': 'obv_pass_90',
        'player_season_deep_progressions_90': 'deep_progressions_90',
        'player_season_passing_ratio': 'passing_ratio',
        'player_season_dribble_ratio': 'dribble_ratio',
        'player_season_obv_dribble_carry_90': 'obv_dribble_carry_90',
        'player_season_defensive_actions_90': 'defensive_actions_90',
        'player_season_tackles_and_interceptions_90': 'tackles_and_interceptions_90',
        'player_season_aerial_ratio': 'aerial_ratio',
        'player_season_npxgxa_90': 'npxgxa_90',
        'player_season_obv_90': 'obv_90',
        'player_season_positive_outcome_score': 'positive_outcome_score'
    }
    
    # Rename columns
    for old_col, new_col in column_mapping.items():
        if old_col in metrics_df.columns:
            metrics_df[new_col] = metrics_df[old_col]
    
    return metrics_df

def calculate_percentiles(df: pd.DataFrame, metrics: List[str]) -> pd.DataFrame:
    """Calculate percentiles for all metrics."""
    percentiles_df = df[['player_id', 'season_id']].copy()
    
    for metric in metrics:
        if metric in df.columns:
            # Calculate percentiles, handling NaN values
            percentiles_df[f'{metric}_percentile'] = df[metric].rank(pct=True, na_option='keep') * 100
    
    return percentiles_df

def calculate_axis_scores(df: pd.DataFrame, axes: List[Dict[str, Any]]) -> pd.DataFrame:
    """Calculate axis scores as average of metric percentiles."""
    axis_scores_df = df[['player_id', 'season_id']].copy()
    
    for axis in axes:
        axis_key = axis['key']
        metrics = axis['metrics']
        
        # Get percentile columns for this axis
        percentile_cols = [f'{metric}_percentile' for metric in metrics if f'{metric}_percentile' in df.columns]
        
        if percentile_cols:
            # Calculate average percentile for this axis, excluding NaN values
            axis_scores_df[f'{axis_key}_score'] = df[percentile_cols].mean(axis=1, skipna=True)
        else:
            axis_scores_df[f'{axis_key}_score'] = 0
    
    return axis_scores_df

def calculate_benchmarks(df: pd.DataFrame, metrics: List[str]) -> Dict[str, Dict[str, float]]:
    """Calculate median and p80 benchmarks for each metric."""
    benchmarks = {}
    
    for metric in metrics:
        if metric in df.columns:
            # Remove NaN values for benchmark calculation
            valid_values = df[metric].dropna()
            if len(valid_values) > 0:
                benchmarks[metric] = {
                    'median': float(valid_values.median()),
                    'p80': float(valid_values.quantile(0.8))
                }
    
    return benchmarks

def calculate_minmax(df: pd.DataFrame, metrics: List[str]) -> Dict[str, Dict[str, float]]:
    """Calculate min/max ranges for absolute view scaling."""
    minmax = {}
    
    for metric in metrics:
        if metric in df.columns:
            # Remove NaN values for min/max calculation
            valid_values = df[metric].dropna()
            if len(valid_values) > 0:
                minmax[metric] = {
                    'min': float(valid_values.min()),
                    'max': float(valid_values.max())
                }
    
    return minmax

def generate_performance_artifacts_for_season(client: StatsBombClient, season_name: str, season_id: str) -> bool:
    """Generate performance artifacts for a specific season."""
    
    print(f"Generating Performance Output artifacts for {season_name}...")
    
    try:
        # Fetch player season stats
        player_stats = client.player_season_stats(competition_id=COMPETITION_ID, season_id=int(season_id))
        
        if player_stats is None or len(player_stats) == 0:
            print(f"No player stats found for {season_name}")
            return False
        
        print(f"Fetched {len(player_stats)} player records for {season_name}")
        
        # Filter for strikers with sufficient minutes
        striker_mask = (
            player_stats['primary_position'].apply(is_striker) &
            (player_stats['player_season_minutes'] >= MINUTES_THRESHOLD)
        )
        
        striker_stats = player_stats[striker_mask].copy()
        
        if len(striker_stats) == 0:
            print(f"No strikers found with >= {MINUTES_THRESHOLD} minutes for {season_name}")
            return False
        
        print(f"Found {len(striker_stats)} strikers with >= {MINUTES_THRESHOLD} minutes")
        
        # Add season_id to the data
        striker_stats = striker_stats.copy()
        striker_stats['season_id'] = season_id
        
        # Extract performance metrics
        metrics_df = extract_performance_metrics(striker_stats)
        
        # Define axes and get all metrics
        axes = create_performance_axes()
        all_metrics = []
        for axis in axes:
            all_metrics.extend(axis['metrics'])
        
        # Calculate percentiles
        percentiles_df = calculate_percentiles(metrics_df, all_metrics)
        
        # Calculate axis scores
        axis_scores_df = calculate_axis_scores(percentiles_df, axes)
        
        # Calculate benchmarks
        benchmarks = calculate_benchmarks(metrics_df, all_metrics)
        
        # Calculate min/max
        minmax = calculate_minmax(metrics_df, all_metrics)
        
        # Create output directory
        output_dir = Path(f"data/processed/performance_artifacts_{season_id}")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        # Save artifacts
        print(f"Generated artifacts for {len(striker_stats)} strikers in {season_name}")
        
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
            "season": season_name,
            "season_id": season_id,
            "competition_id": COMPETITION_ID,
            "generated_at": "2025-01-27",
            "striker_count": len(striker_stats)
        }
        with open(output_dir / "performance_config.json", "w") as f:
            json.dump(config, f, indent=2)
        
        # 7. Raw metrics data (for debugging)
        metrics_df[['player_id', 'season_id'] + all_metrics].to_parquet(
            output_dir / "performance_raw_metrics.parquet", index=False
        )
        
        print(f"Artifacts saved to: {output_dir}")
        print(f"Generated {len(axes)} performance axes with {len(all_metrics)} total metrics")
        
        return True
        
    except Exception as e:
        print(f"Error generating artifacts for {season_name}: {e}")
        return False

def generate_all_performance_artifacts():
    """Generate performance artifacts for all seasons."""
    print("Generating Performance Output artifacts with real data...")
    
    # Initialize API client
    client = StatsBombClient()
    
    if not client.has_credentials:
        print("Warning: No API credentials found. Using open data only.")
    
    success_count = 0
    total_seasons = len(SEASONS)
    
    for season_name, season_id in SEASONS.items():
        if generate_performance_artifacts_for_season(client, season_name, season_id):
            success_count += 1
        print()  # Add spacing between seasons
    
    print(f"Completed: {success_count}/{total_seasons} seasons processed successfully")
    
    if success_count > 0:
        print("\nTo use these artifacts, update the PerformanceLoader to look for season-specific directories:")
        print("data/processed/performance_artifacts_<season_id>/")
    
    return success_count > 0

if __name__ == "__main__":
    generate_all_performance_artifacts()
