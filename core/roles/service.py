"""
Role Service

Business logic for:
- Role assignment with confidence detection (hybrid vs primary)
- Similar players retrieval with role info
"""

from typing import Dict, List, Optional, Any
from .loader import get_role_loader


class RoleService:
    """Service for role assignment and similarity queries."""
    
    def __init__(self, loader=None):
        """Initialize with a loader (defaults to global singleton)."""
        self.loader = loader or get_role_loader()
    
    def get_player_role(self, player_id: int, season_id: int) -> Optional[Dict[str, Any]]:
        """
        Get role assignment for a player in a season.
        
        Returns:
            {
                "role": "Link-Up / Complete Striker" | "Pressing Striker" | "Poacher",
                "is_hybrid": bool,                    # True if max posterior < 0.60
                "confidence": float,                  # max posterior in [0, 1]
                "top_roles": [{"role": str, "prob": float}, ...],  # top 2-3 roles
                "tooltip": str                        # role description
            }
        """
        # Get cluster probabilities
        cluster_probs = self.loader.get_player_cluster_probs(player_id, season_id)
        if not cluster_probs:
            return None
        
        # Extract posteriors
        posteriors = {}
        for i in range(3):  # 3 clusters
            key = f"cluster_{i}"
            if key in cluster_probs:
                posteriors[i] = cluster_probs[key]
        
        if not posteriors:
            return None
        
        # Get cluster-to-role mapping
        cluster_to_role = self.loader.load_cluster_to_role()
        role_descriptions = self.loader.load_role_descriptions()
        
        # Find primary role (cluster with max posterior)
        primary_cluster = max(posteriors.keys(), key=lambda k: posteriors[k])
        max_prob = posteriors[primary_cluster]
        primary_role = cluster_to_role.get(primary_cluster, "Unknown")
        
        # Determine if hybrid (max posterior < 0.60)
        is_hybrid = max_prob < 0.60
        
        # Build top_roles list
        sorted_clusters = sorted(posteriors.items(), key=lambda x: x[1], reverse=True)
        top_roles = []
        for cluster_id, prob in sorted_clusters[:2]:  # Top 2
            role_name = cluster_to_role.get(cluster_id, "Unknown")
            top_roles.append({"role": role_name, "prob": round(prob, 3)})
        
        # Get tooltip
        tooltip = role_descriptions.get(primary_role, "")
        
        return {
            "role": primary_role,
            "is_hybrid": is_hybrid,
            "confidence": round(max_prob, 3),
            "top_roles": top_roles,
            "tooltip": tooltip
        }
    
    def get_similar_players(self, player_id: int, season_id: int, k: int = 5) -> List[Dict[str, Any]]:
        """
        Get top-k most similar strikers across all seasons.
        
        Returns:
            [{
                "player_id": int,
                "season_id": int,
                "similarity": int,          # 0..100, round(100 * cosine_sim)
                "role": str,                # role for neighbor_season_id
                "confidence": float,        # role confidence for neighbor
                "player_name": str,         # (optional, if available)
                "team_id": int              # (optional, if available)
            }, ...]
        """
        # Get neighbors
        neighbors = self.loader.get_neighbors(player_id, season_id, top_k=k)
        
        result = []
        for neighbor in neighbors:
            neighbor_player_id = neighbor["neighbor_player_id"]
            neighbor_season_id = neighbor["neighbor_season_id"]
            cosine_sim = neighbor["cosine_sim"]
            
            # Get neighbor's role
            neighbor_role = self.get_player_role(neighbor_player_id, neighbor_season_id)
            
            if neighbor_role:
                similarity_pct = round(100 * cosine_sim)
                
                # Try to get player metadata if available
                style_row = self.loader.get_player_style_row(neighbor_player_id, neighbor_season_id)
                player_name = style_row.get("player_name", f"Player {neighbor_player_id}") if style_row else f"Player {neighbor_player_id}"
                team_id = style_row.get("team_id") if style_row else None
                
                result.append({
                    "player_id": neighbor_player_id,
                    "season_id": neighbor_season_id,
                    "similarity": similarity_pct,
                    "role": neighbor_role["role"],
                    "confidence": neighbor_role["confidence"],
                    "player_name": player_name,
                    "team_id": team_id
                })
        
        return result
    
    def is_valid_data(self, player_id: int, season_id: int) -> bool:
        """Check if player has valid role data for the season."""
        cluster_probs = self.loader.get_player_cluster_probs(player_id, season_id)
        return cluster_probs is not None and len(cluster_probs) > 0


def get_role_service(loader=None) -> RoleService:
    """Get a role service instance."""
    return RoleService(loader=loader)
