"""
Performance service for building striker performance profiles.

This module orchestrates the building of performance profiles by combining
data from the performance loader with player identity information.
"""

from typing import Dict, List, Any, Optional
from .loader import PerformanceLoader


class PerformanceService:
    """Service for building performance profiles."""
    
    def __init__(self, loader: PerformanceLoader = None, season_id: str = None):
        """Initialize the service with a performance loader."""
        self.season_id = season_id
        self.loader = loader or PerformanceLoader(season_id=season_id)
    
    def build_performance_profile(
        self, 
        player_id: str, 
        player_name: str = None,
        team_name: str = None,
        primary_position: str = None,
        secondary_position: str = None,
        season: str = "2024/25",
        minutes: int = 0
    ) -> Optional[Dict[str, Any]]:
        """
        Build a striker performance profile payload.
        
        Args:
            player_id: Player identifier
            player_name: Player name
            team_name: Team name
            primary_position: Primary position
            secondary_position: Secondary position
            season: Season string
            minutes: Minutes played
            
        Returns:
            Performance profile payload or None if not found
        """
        # Check if player is a striker
        if primary_position and not self.is_striker(primary_position, secondary_position):
            return None
        
        # Get performance data
        metric_data = self.loader.get_player_metric_row(player_id)
        axis_scores = self.loader.get_player_axis_scores(player_id)
        raw_metrics = self.loader.get_player_raw_metrics(player_id)
        
        # If no data found, return None
        if not metric_data and not axis_scores:
            return None
        
        # Get axes definitions
        axes_def = self.loader.get_axes()
        
        # Build axes with metrics
        axes = []
        for axis_def in axes_def:
            axis_key = axis_def['key']
            axis_score = axis_scores.get(axis_key, 0.0) if axis_scores else 0.0
            
            # Get metrics for this axis
            metrics = []
            for metric_key in axis_def['metrics']:
                metric_data_item = metric_data.get(metric_key, {}) if metric_data else {}
                benchmarks = self.loader.get_benchmarks(metric_key)
                
                # Get raw metric value
                raw_value = raw_metrics.get(metric_key) if raw_metrics else None
                
                # Get metric label (simplified for now)
                metric_label = self._get_metric_label(metric_key)
                
                metrics.append({
                    'key': metric_key,
                    'label': metric_label,
                    'raw': raw_value,
                    'percentile': metric_data_item.get('percentile'),
                    'benchmarks': benchmarks or {}
                })
            
            axes.append({
                'key': axis_key,
                'label': axis_def['label'],
                'score': axis_score,
                'metrics': metrics
            })
        
        # Build performance profile payload
        profile = {
            "player": {
                "id": player_id,
                "name": player_name or "Unknown Player",
                "team": team_name or "Unknown Team",
                "minutes": minutes
            },
            "season": season,
            "axes": axes,
            "notes": f"Percentiles relative to Liga MX strikers (≥{self.loader.get_minutes_threshold()}'), {season}",
            "minutes_threshold": self.loader.get_minutes_threshold(),
            "meta": {
                "data_version": "v1",
                "computed_at": "2025-01-27",
                "is_striker": True
            }
        }
        
        return profile
    
    def is_striker(self, primary_position: str, secondary_position: str = None) -> bool:
        """Check if a player is a striker based on position."""
        striker_positions = {
            'Centre Forward', 'Left Centre Forward', 'Right Centre Forward'
        }
        
        if primary_position in striker_positions:
            return True
        
        if secondary_position and secondary_position in striker_positions:
            return True
        
        return False
    
    def _extract_season_id(self, season: str) -> Optional[str]:
        """Extract season ID from season string."""
        season_mapping = {
            "2024/25": "317",
            "2023/24": "281", 
            "2022/23": "235",
            "2021/22": "108"
        }
        return season_mapping.get(season)
    
    def _get_metric_label(self, metric_key: str) -> str:
        """Get human-readable label for a metric key."""
        label_mapping = {
            'touches_box_90': 'Touches in Box /90',
            'np_xg_90': 'NP xG /90',
            'np_xg_per_shot': 'xG / Shot',
            'finishing_quality': 'PS xG – xG',
            'xa_90': 'xA /90',
            'key_passes_90': 'Key Passes /90',
            'obv_pass_90': 'OBV Pass /90',
            'xa_per_shot_assist': 'xA / Key Pass',
            'deep_progressions_90': 'Deep Progressions /90',
            'passing_ratio': 'Passing Ratio',
            'dribble_ratio': 'Dribble Ratio',
            'obv_dribble_carry_90': 'OBV Dribble /90',
            'defensive_actions_90': 'Defensive Actions /90',
            'tackles_interceptions_90': 'Tackles & Interceptions /90',
            'aerial_ratio': 'Aerial Ratio',
            'npxgxa_90': 'NP xG + xA /90',
            'obv_90': 'OBV /90',
            'positive_outcome_score': 'Positive Outcome Score'
        }
        
        return label_mapping.get(metric_key, metric_key.replace('_', ' ').title())


def get_performance_service(season_id: str = None) -> PerformanceService:
    """Get a performance service instance."""
    return PerformanceService(season_id=season_id)
