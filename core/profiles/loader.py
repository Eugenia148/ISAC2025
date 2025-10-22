"""
Tactical Profile Loader
Loads PCA artifacts and provides data access for striker tactical profiles.
"""

import os
import json
import pickle
import pandas as pd
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class Axis:
    """Represents a tactical ability axis."""
    key: str
    label: str
    description: str


class TacticalProfileLoader:
    """Loads and caches tactical profile artifacts."""
    
    def __init__(self, artifacts_dir: str = "data/processed/striker_artifacts"):
        """Initialize the loader with artifacts directory."""
        # Use absolute path if relative path doesn't exist
        if not os.path.exists(artifacts_dir):
            # Try to find the correct path
            possible_paths = [
                "C:/Users/carls/OneDrive/Dokumente/Uni/05 Semester/Marketing y Estrategia de Deportes/Projekt/Repo/ISAC2025/data/processed/striker_artifacts",
                "data/processed/striker_artifacts",
                "../data/processed/striker_artifacts"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    artifacts_dir = path
                    break
        
        self.artifacts_dir = artifacts_dir
        self._axes: Optional[List[Axis]] = None
        self._ability_scores: Optional[pd.DataFrame] = None
        self._percentiles: Optional[pd.DataFrame] = None
        self._league_reference: Optional[Dict[str, float]] = None
        self._axis_ranges: Optional[Dict[str, Dict[str, float]]] = None
        
    def _load_artifacts_if_needed(self):
        """Lazy load artifacts on first access."""
        if self._axes is None:
            self._load_axes()
        if self._ability_scores is None:
            self._load_ability_scores()
        if self._percentiles is None:
            self._load_percentiles()
        if self._league_reference is None:
            self._load_league_reference()
        if self._axis_ranges is None:
            self._load_axis_ranges()
    
    def _load_axes(self):
        """Load ability axes definitions."""
        try:
            axes_path = os.path.join(self.artifacts_dir, "ability_axes.json")
            if os.path.exists(axes_path):
                with open(axes_path, 'r') as f:
                    axes_data = json.load(f)
                self._axes = [Axis(**axis) for axis in axes_data]
            else:
                # Fallback to hardcoded axes from notebook
                self._axes = [
                    Axis("Progressive_Play", "Progressive Play", "Ball progression & link play"),
                    Axis("Finishing_BoxPresence", "Finishing & Box Presence", "Goal scoring and box positioning"),
                    Axis("Pressing_WorkRate", "Pressing Work Rate", "Defensive pressure and work rate"),
                    Axis("Finishing_Efficiency", "Finishing Efficiency", "Shot conversion and efficiency"),
                    Axis("Dribbling_RiskTaking", "Dribbling & Risk-Taking", "Ball carrying and risk taking"),
                    Axis("DecisionMaking_Balance", "Decision Making & Balance", "Decision making and balance")
                ]
        except Exception as e:
            print(f"Error loading axes: {e}")
            self._axes = []
    
    def _load_ability_scores(self):
        """Load ability scores data."""
        try:
            scores_path = os.path.join(self.artifacts_dir, "ability_scores.parquet")
            if os.path.exists(scores_path):
                self._ability_scores = pd.read_parquet(scores_path)
            else:
                # Create empty DataFrame with expected structure
                self._ability_scores = pd.DataFrame()
        except Exception as e:
            print(f"Error loading ability scores: {e}")
            self._ability_scores = pd.DataFrame()
    
    def _load_percentiles(self):
        """Load percentile data."""
        try:
            percentiles_path = os.path.join(self.artifacts_dir, "ability_percentiles.parquet")
            if os.path.exists(percentiles_path):
                self._percentiles = pd.read_parquet(percentiles_path)
            else:
                # Create empty DataFrame with expected structure
                self._percentiles = pd.DataFrame()
        except Exception as e:
            print(f"Error loading percentiles: {e}")
            self._percentiles = pd.DataFrame()
    
    def _load_league_reference(self):
        """Load league reference data."""
        try:
            ref_path = os.path.join(self.artifacts_dir, "league_reference.json")
            if os.path.exists(ref_path):
                with open(ref_path, 'r') as f:
                    self._league_reference = json.load(f)
            else:
                # Default league average (50th percentile for all axes)
                self._league_reference = {
                    "Progressive_Play": 50.0,
                    "Finishing_BoxPresence": 50.0,
                    "Pressing_WorkRate": 50.0,
                    "Finishing_Efficiency": 50.0,
                    "Dribbling_RiskTaking": 50.0,
                    "DecisionMaking_Balance": 50.0
                }
        except Exception as e:
            print(f"Error loading league reference: {e}")
            self._league_reference = {}
    
    def _load_axis_ranges(self):
        """Load axis ranges for absolute mode rendering."""
        try:
            ranges_path = os.path.join(self.artifacts_dir, "axis_ranges.json")
            if os.path.exists(ranges_path):
                with open(ranges_path, 'r') as f:
                    self._axis_ranges = json.load(f)
            else:
                # Default ranges based on normalized scores (0-1)
                self._axis_ranges = {
                    "Progressive_Play": {"min": 0.0, "max": 1.0},
                    "Finishing_BoxPresence": {"min": 0.0, "max": 1.0},
                    "Pressing_WorkRate": {"min": 0.0, "max": 1.0},
                    "Finishing_Efficiency": {"min": 0.0, "max": 1.0},
                    "Dribbling_RiskTaking": {"min": 0.0, "max": 1.0},
                    "DecisionMaking_Balance": {"min": 0.0, "max": 1.0}
                }
        except Exception as e:
            print(f"Error loading axis ranges: {e}")
            self._axis_ranges = {}
    
    def get_axes(self) -> List[Axis]:
        """Get the ability axes definitions."""
        self._load_artifacts_if_needed()
        return self._axes or []
    
    def get_player_ability_scores(self, player_id: str, season_id: str = None) -> Optional[Dict[str, float]]:
        """Get ability scores for a specific player and season."""
        self._load_artifacts_if_needed()
        
        if self._ability_scores.empty:
            return None
            
        try:
            # Try to find player by player_season_id or player_id
            player_data = None
            
            if season_id:
                # Look for specific player_season_id
                player_season_id = f"{player_id}_{season_id}"
                if player_season_id in self._ability_scores.index:
                    player_data = self._ability_scores.loc[player_season_id]
            else:
                # First try player_season_id format
                if player_id in self._ability_scores.index:
                    player_data = self._ability_scores.loc[player_id]
                else:
                    # Try to find by extracting player_id from player_season_id
                    for idx in self._ability_scores.index:
                        if str(idx).startswith(str(player_id) + '_'):
                            player_data = self._ability_scores.loc[idx]
                            break
            
            if player_data is not None:
                return player_data.to_dict()
            return None
        except Exception as e:
            print(f"Error getting ability scores for player {player_id} season {season_id}: {e}")
            return None
    
    def get_player_percentiles(self, player_id: str, season_id: str = None) -> Optional[Dict[str, float]]:
        """Get percentile scores for a specific player and season."""
        self._load_artifacts_if_needed()
        
        if self._percentiles.empty:
            return None
            
        try:
            # Try to find player by player_season_id or player_id
            player_data = None
            
            if season_id:
                # Look for specific player_season_id
                player_season_id = f"{player_id}_{season_id}"
                if player_season_id in self._percentiles.index:
                    player_data = self._percentiles.loc[player_season_id]
            else:
                # First try player_season_id format
                if player_id in self._percentiles.index:
                    player_data = self._percentiles.loc[player_id]
                else:
                    # Try to find by extracting player_id from player_season_id
                    for idx in self._percentiles.index:
                        if str(idx).startswith(str(player_id) + '_'):
                            player_data = self._percentiles.loc[idx]
                            break
            
            if player_data is not None:
                return player_data.to_dict()
            return None
        except Exception as e:
            print(f"Error getting percentiles for player {player_id} season {season_id}: {e}")
            return None
    
    def get_league_reference(self) -> Optional[Dict[str, float]]:
        """Get league reference scores."""
        self._load_artifacts_if_needed()
        return self._league_reference
    
    def get_axis_ranges(self) -> Optional[Dict[str, Dict[str, float]]]:
        """Get axis ranges for absolute mode rendering."""
        self._load_artifacts_if_needed()
        return self._axis_ranges


# Global loader instance
_loader_instance: Optional[TacticalProfileLoader] = None


def get_loader() -> TacticalProfileLoader:
    """Get the global loader instance."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = TacticalProfileLoader()
    return _loader_instance
