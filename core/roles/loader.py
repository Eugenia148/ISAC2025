"""
Role Artifacts Loader

Loads and caches role-related artifacts including:
- Per-season PCA style vectors and GMM cluster posteriors
- Cluster-to-role mappings and role descriptions
- Multi-season neighbor similarity data

All loaders are memoized for performance.
"""

import os
import json
import pickle
import pandas as pd
from typing import Dict, List, Optional, Any
from pathlib import Path


class RoleLoader:
    """Loads and caches role artifacts with memoization."""
    
    def __init__(self, artifacts_root: str = "data/processed/roles"):
        """Initialize the loader with artifacts root directory."""
        # Use absolute path if relative path doesn't exist
        if not os.path.exists(artifacts_root):
            possible_paths = [
                "C:/Users/carls/OneDrive/Dokumente/Uni/05 Semester/Marketing y Estrategia de Deportes/Projekt/Repo/ISAC2025/data/processed/roles",
                "data/processed/roles",
                "../data/processed/roles"
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    artifacts_root = path
                    break
        
        self.artifacts_root = artifacts_root
        
        # Global (multi-season) caches
        self._cluster_to_role: Optional[Dict[int, str]] = None
        self._role_descriptions: Optional[Dict[str, str]] = None
        self._neighbors_df: Optional[pd.DataFrame] = None
        
        # Per-season caches
        self._season_caches: Dict[int, Dict[str, Any]] = {}
    
    def _load_global_artifacts_if_needed(self) -> None:
        """Load global artifacts if not already loaded."""
        if self._cluster_to_role is None:
            self._load_cluster_to_role()
        if self._role_descriptions is None:
            self._load_role_descriptions()
        if self._neighbors_df is None:
            self._load_neighbors()
    
    def _load_cluster_to_role(self) -> None:
        """Load cluster-to-role mapping."""
        try:
            config_path = os.path.join(self.artifacts_root, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    # Convert string keys to ints
                    self._cluster_to_role = {
                        int(k): v for k, v in config.get("cluster_to_role", {}).items()
                    }
            else:
                # Fallback to hardcoded
                self._cluster_to_role = {
                    0: "Link-Up / Complete Striker",
                    1: "Pressing Striker",
                    2: "Poacher"
                }
        except Exception as e:
            print(f"Error loading cluster-to-role: {e}")
            self._cluster_to_role = {}
    
    def _load_role_descriptions(self) -> None:
        """Load role descriptions."""
        try:
            config_path = os.path.join(self.artifacts_root, "config.json")
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    config = json.load(f)
                    self._role_descriptions = config.get("role_descriptions", {})
            
            if not self._role_descriptions:
                # Fallback: load from first season's file if available
                for season_dir in os.listdir(self.artifacts_root):
                    season_path = os.path.join(self.artifacts_root, season_dir)
                    if os.path.isdir(season_path):
                        role_desc_path = os.path.join(season_path, "role_descriptions.json")
                        if os.path.exists(role_desc_path):
                            with open(role_desc_path, "r") as f:
                                self._role_descriptions = json.load(f)
                                return
            
            if not self._role_descriptions:
                # Hardcoded fallback
                self._role_descriptions = {
                    "Link-Up / Complete Striker": "Connects play, drops in, combines efficiently and contributes to buildup.",
                    "Pressing Striker": "Leads the press, initiates defensive actions and disrupts buildup.",
                    "Poacher": "Focuses on box occupation and finishing, limited link play."
                }
        except Exception as e:
            print(f"Error loading role descriptions: {e}")
            self._role_descriptions = {}
    
    def _load_neighbors(self) -> None:
        """Load multi-season neighbor similarity data."""
        try:
            neighbors_path = os.path.join(self.artifacts_root, "player_neighbors.parquet")
            if os.path.exists(neighbors_path):
                self._neighbors_df = pd.read_parquet(neighbors_path)
            else:
                self._neighbors_df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading neighbors: {e}")
            self._neighbors_df = pd.DataFrame()
    
    def _ensure_season_cache(self, season_id: int) -> None:
        """Load all per-season artifacts if not already cached."""
        if season_id in self._season_caches:
            return
        
        season_dir = os.path.join(self.artifacts_root, str(season_id))
        
        if not os.path.exists(season_dir):
            self._season_caches[season_id] = {
                "style_vectors": pd.DataFrame(),
                "cluster_probs": pd.DataFrame(),
                "error": f"Season directory not found: {season_dir}"
            }
            return
        
        cache = {}
        
        # Load style vectors
        try:
            style_vec_path = os.path.join(season_dir, "player_style_vectors.parquet")
            if os.path.exists(style_vec_path):
                cache["style_vectors"] = pd.read_parquet(style_vec_path)
            else:
                cache["style_vectors"] = pd.DataFrame()
        except Exception as e:
            print(f"Error loading style vectors for season {season_id}: {e}")
            cache["style_vectors"] = pd.DataFrame()
        
        # Load cluster probs
        try:
            cluster_probs_path = os.path.join(season_dir, "player_cluster_probs.parquet")
            if os.path.exists(cluster_probs_path):
                cache["cluster_probs"] = pd.read_parquet(cluster_probs_path)
            else:
                cache["cluster_probs"] = pd.DataFrame()
        except Exception as e:
            print(f"Error loading cluster probs for season {season_id}: {e}")
            cache["cluster_probs"] = pd.DataFrame()
        
        self._season_caches[season_id] = cache
    
    # ===== Public API =====
    
    def load_cluster_to_role(self) -> Dict[int, str]:
        """Get cluster ID → role name mapping."""
        self._load_global_artifacts_if_needed()
        return self._cluster_to_role or {}
    
    def load_role_descriptions(self) -> Dict[str, str]:
        """Get role name → description mapping."""
        self._load_global_artifacts_if_needed()
        return self._role_descriptions or {}
    
    def get_player_style_row(self, player_id: int, season_id: int) -> Optional[Dict]:
        """
        Get style vector row for a player in a season.
        
        Returns:
            {player_id, season_id, minutes, team_id, pca_1..pca_6} or None
        """
        self._ensure_season_cache(season_id)
        
        if season_id not in self._season_caches:
            return None
        
        style_df = self._season_caches[season_id].get("style_vectors", pd.DataFrame())
        
        if style_df.empty:
            return None
        
        try:
            # Try to find by player_id
            row = style_df[style_df["player_id"] == player_id]
            if row.empty:
                # Try as int if player_id is string
                try:
                    row = style_df[style_df["player_id"] == int(player_id)]
                except (ValueError, TypeError):
                    pass
            
            if not row.empty:
                return row.iloc[0].to_dict()
        except Exception as e:
            print(f"Error getting style row for player {player_id} season {season_id}: {e}")
        
        return None
    
    def get_player_cluster_probs(self, player_id: int, season_id: int) -> Optional[Dict]:
        """
        Get cluster posteriors for a player in a season.
        
        Returns:
            {cluster_0: float, cluster_1: float, cluster_2: float, predicted_cluster: int} or None
        """
        self._ensure_season_cache(season_id)
        
        if season_id not in self._season_caches:
            return None
        
        cluster_df = self._season_caches[season_id].get("cluster_probs", pd.DataFrame())
        
        if cluster_df.empty:
            return None
        
        try:
            # Try to find by player_id
            row = cluster_df[cluster_df["player_id"] == player_id]
            if row.empty:
                # Try as int if player_id is string
                try:
                    row = cluster_df[cluster_df["player_id"] == int(player_id)]
                except (ValueError, TypeError):
                    pass
            
            if not row.empty:
                data = row.iloc[0].to_dict()
                # Extract only cluster probabilities and prediction
                result = {}
                for i in range(3):  # 3 clusters
                    key = f"cluster_{i}"
                    if key in data:
                        result[key] = float(data[key])
                if "predicted_cluster" in data:
                    result["predicted_cluster"] = int(data["predicted_cluster"])
                return result if result else None
        except Exception as e:
            print(f"Error getting cluster probs for player {player_id} season {season_id}: {e}")
        
        return None
    
    def get_neighbors(self, player_id: int, season_id: int, top_k: int = 5) -> List[Dict]:
        """
        Get top-K similar players (all seasons) excluding (player_id, season_id) itself.
        
        Returns:
            [{neighbor_player_id, neighbor_season_id, cosine_sim}, ...] sorted by similarity desc
        """
        self._load_global_artifacts_if_needed()
        
        if self._neighbors_df is None or self._neighbors_df.empty:
            return []
        
        try:
            # Find neighbors for this (player_id, season_id)
            neighbors = self._neighbors_df[
                (self._neighbors_df["anchor_player_id"] == player_id) &
                (self._neighbors_df["anchor_season_id"] == season_id)
            ].head(top_k)
            
            result = []
            for _, row in neighbors.iterrows():
                result.append({
                    "neighbor_player_id": int(row["neighbor_player_id"]),
                    "neighbor_season_id": int(row["neighbor_season_id"]),
                    "cosine_sim": float(row["cosine_sim"])
                })
            
            return result
        except Exception as e:
            print(f"Error getting neighbors for player {player_id} season {season_id}: {e}")
            return []
    
    def minutes_threshold(self) -> int:
        """Get the minutes threshold used in artifact generation."""
        return 500
    
    def clear_cache(self) -> None:
        """Clear all caches to force reload from disk."""
        self._cluster_to_role = None
        self._role_descriptions = None
        self._neighbors_df = None
        self._season_caches = {}


# Global singleton
_loader_instance: Optional[RoleLoader] = None


def get_role_loader() -> RoleLoader:
    """Get the global role loader instance (singleton)."""
    global _loader_instance
    if _loader_instance is None:
        _loader_instance = RoleLoader()
    return _loader_instance


def reset_role_loader() -> None:
    """Reset the global role loader singleton."""
    global _loader_instance
    if _loader_instance is not None:
        _loader_instance.clear_cache()
    _loader_instance = None
