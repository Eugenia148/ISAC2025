"""
Performance artifacts loader for striker performance analysis.

This module loads and caches performance metrics artifacts including:
- Performance axes definitions
- Performance percentiles and raw values
- Axis scores (averaged percentiles per axis)
- Benchmarks (median and p80)
- Min/max ranges for absolute view scaling
"""

import os
import json
import pandas as pd
from typing import Dict, List, Any, Optional
from pathlib import Path


class PerformanceLoader:
    """Loads and caches performance artifacts."""
    
    def __init__(self, artifacts_dir: str = "data/processed/performance_artifacts", season_id: str = None):
        """Initialize the loader with artifacts directory."""
        # If season_id is provided, use season-specific directory
        if season_id:
            artifacts_dir = f"data/processed/performance_artifacts_{season_id}"
        
        # Use absolute path if relative path doesn't exist
        if not os.path.exists(artifacts_dir):
            # Try to find the correct path
            possible_paths = [
                f"C:/Users/carls/OneDrive/Dokumente/Uni/05 Semester/Marketing y Estrategia de Deportes/Projekt/Repo/ISAC2025/{artifacts_dir}",
                artifacts_dir,
                f"../{artifacts_dir}"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    artifacts_dir = path
                    break
        
        self.artifacts_dir = artifacts_dir
        self._axes: Optional[List[Dict[str, Any]]] = None
        self._percentiles: Optional[pd.DataFrame] = None
        self._raw_metrics: Optional[pd.DataFrame] = None
        self._axis_scores: Optional[pd.DataFrame] = None
        self._benchmarks: Optional[Dict[str, Dict[str, float]]] = None
        self._minmax: Optional[Dict[str, Dict[str, float]]] = None
        self._config: Optional[Dict[str, Any]] = None

    def _load_artifacts_if_needed(self) -> None:
        """Load artifacts if not already loaded."""
        if self._axes is None:
            self._load_axes()
        if self._percentiles is None:
            self._load_percentiles()
        if self._raw_metrics is None:
            self._load_raw_metrics()
        if self._axis_scores is None:
            self._load_axis_scores()
        if self._benchmarks is None:
            self._load_benchmarks()
        if self._minmax is None:
            self._load_minmax()
        if self._config is None:
            self._load_config()

    def _load_axes(self) -> None:
        """Load performance axes definition."""
        try:
            with open(os.path.join(self.artifacts_dir, "performance_axes.json"), "r") as f:
                self._axes = json.load(f)
        except Exception as e:
            print(f"Error loading performance axes: {e}")
            self._axes = []

    def _load_percentiles(self) -> None:
        """Load performance percentiles data."""
        try:
            self._percentiles = pd.read_parquet(
                os.path.join(self.artifacts_dir, "performance_percentiles.parquet")
            )
        except Exception as e:
            print(f"Error loading performance percentiles: {e}")
            self._percentiles = pd.DataFrame()

    def _load_raw_metrics(self) -> None:
        """Load raw metrics data."""
        try:
            self._raw_metrics = pd.read_parquet(
                os.path.join(self.artifacts_dir, "performance_raw_metrics.parquet")
            )
        except Exception as e:
            # Raw metrics file may not exist, which is OK
            self._raw_metrics = pd.DataFrame()

    def _load_axis_scores(self) -> None:
        """Load performance axis scores data."""
        try:
            self._axis_scores = pd.read_parquet(
                os.path.join(self.artifacts_dir, "performance_axis_scores.parquet")
            )
        except Exception as e:
            print(f"Error loading performance axis scores: {e}")
            self._axis_scores = pd.DataFrame()

    def _load_benchmarks(self) -> None:
        """Load performance benchmarks data."""
        try:
            with open(os.path.join(self.artifacts_dir, "performance_benchmarks.json"), "r") as f:
                self._benchmarks = json.load(f)
        except Exception as e:
            print(f"Error loading performance benchmarks: {e}")
            self._benchmarks = {}

    def _load_minmax(self) -> None:
        """Load performance min/max ranges data."""
        try:
            with open(os.path.join(self.artifacts_dir, "performance_minmax.json"), "r") as f:
                self._minmax = json.load(f)
        except Exception as e:
            print(f"Error loading performance min/max: {e}")
            self._minmax = {}

    def _load_config(self) -> None:
        """Load performance configuration data."""
        try:
            with open(os.path.join(self.artifacts_dir, "performance_config.json"), "r") as f:
                self._config = json.load(f)
        except Exception as e:
            print(f"Error loading performance config: {e}")
            self._config = {}

    def get_axes(self) -> List[Dict[str, Any]]:
        """Get performance axes definitions."""
        self._load_artifacts_if_needed()
        return self._axes or []

    def get_player_metric_row(self, player_id: str) -> Optional[Dict[str, Dict[str, float]]]:
        """Get raw and percentile values for all metrics for a specific player."""
        self._load_artifacts_if_needed()
        
        if self._percentiles.empty:
            return None
            
        try:
            # Find player data - try both string and integer conversion
            player_data = None
            
            # Try as string first
            if player_id in self._percentiles['player_id'].values:
                player_data = self._percentiles[self._percentiles['player_id'] == player_id].iloc[0]
            # Try as integer
            elif int(player_id) in self._percentiles['player_id'].values:
                player_data = self._percentiles[self._percentiles['player_id'] == int(player_id)].iloc[0]
            
            if player_data is not None:
                result = {}
                for col in self._percentiles.columns:
                    if col != 'player_id' and col.endswith('_percentile'):
                        metric_key = col.replace('_percentile', '')
                        result[metric_key] = {
                            'percentile': float(player_data[col]) if pd.notna(player_data[col]) else None
                        }
                return result
            return None
        except Exception as e:
            print(f"Error getting metric row for player {player_id}: {e}")
            return None

    def get_player_raw_metrics(self, player_id: str) -> Optional[Dict[str, float]]:
        """Get raw metrics for a specific player."""
        self._load_artifacts_if_needed()
        
        if self._raw_metrics.empty:
            return None
            
        try:
            # Find player data - try both string and integer conversion
            player_data = None
            
            # Try as string first
            if player_id in self._raw_metrics['player_id'].values:
                player_data = self._raw_metrics[self._raw_metrics['player_id'] == player_id].iloc[0]
            # Try as integer
            elif int(player_id) in self._raw_metrics['player_id'].values:
                player_data = self._raw_metrics[self._raw_metrics['player_id'] == int(player_id)].iloc[0]
            
            if player_data is not None:
                result = {}
                for col in self._raw_metrics.columns:
                    if col != 'player_id':
                        result[col] = float(player_data[col]) if pd.notna(player_data[col]) else 0.0
                return result
            return None
        except Exception as e:
            print(f"Error getting raw metrics for player {player_id}: {e}")
            return None

    def get_player_axis_scores(self, player_id: str) -> Optional[Dict[str, float]]:
        """Get axis scores for a specific player."""
        self._load_artifacts_if_needed()
        
        if self._axis_scores.empty:
            return None
            
        try:
            # Find player data - try both string and integer conversion
            player_data = None
            
            # Try as string first
            if player_id in self._axis_scores['player_id'].values:
                player_data = self._axis_scores[self._axis_scores['player_id'] == player_id].iloc[0]
            # Try as integer
            elif int(player_id) in self._axis_scores['player_id'].values:
                player_data = self._axis_scores[self._axis_scores['player_id'] == int(player_id)].iloc[0]
            
            if player_data is not None:
                result = {}
                for col in self._axis_scores.columns:
                    if col != 'player_id' and col.endswith('_score'):
                        axis_key = col.replace('_score', '')
                        result[axis_key] = float(player_data[col]) if pd.notna(player_data[col]) else 0.0
                return result
            return None
        except Exception as e:
            print(f"Error getting axis scores for player {player_id}: {e}")
            return None

    def get_benchmarks(self, metric_key: str) -> Optional[Dict[str, float]]:
        """Get benchmarks (median and p80) for a specific metric."""
        self._load_artifacts_if_needed()
        return self._benchmarks.get(metric_key)

    def get_minutes_threshold(self) -> int:
        """Get the minutes threshold for analysis."""
        self._load_artifacts_if_needed()
        return self._config.get('minutes_threshold', 600)

    def get_season(self) -> str:
        """Get the season for analysis."""
        self._load_artifacts_if_needed()
        return self._config.get('season', '2024/25')

    def get_minmax(self, metric_key: str) -> Optional[Dict[str, float]]:
        """Get min/max range for a specific metric."""
        self._load_artifacts_if_needed()
        return self._minmax.get(metric_key)

    def get_all_metrics(self) -> List[str]:
        """Get list of all available metrics."""
        self._load_artifacts_if_needed()
        metrics = []
        for axis in self._axes or []:
            metrics.extend(axis.get('metrics', []))
        return metrics

    def get_axis_metrics(self, axis_key: str) -> List[str]:
        """Get metrics for a specific axis."""
        self._load_artifacts_if_needed()
        for axis in self._axes or []:
            if axis.get('key') == axis_key:
                return axis.get('metrics', [])
        return []

    def is_loaded(self) -> bool:
        """Check if artifacts are loaded."""
        return (
            self._axes is not None and
            self._percentiles is not None and
            self._axis_scores is not None and
            self._benchmarks is not None and
            self._minmax is not None and
            self._config is not None
        )
