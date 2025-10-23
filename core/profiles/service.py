"""
Tactical Profile Service
Builds striker profile payloads for the UI.
"""

from typing import Dict, Optional, Any
from .loader import get_loader, TacticalProfileLoader


class TacticalProfileService:
    """Service for building tactical profile payloads."""
    
    def __init__(self, loader: Optional[TacticalProfileLoader] = None):
        """Initialize the service with a loader."""
        self.loader = loader or get_loader()
        
        # Striker position mappings
        self.striker_positions = {
            'Centre Forward',
            'Left Centre Forward', 
            'Right Centre Forward'
        }
    
    def is_striker(self, primary_position: str, secondary_position: Optional[str] = None) -> bool:
        """Check if a player is a striker based on position."""
        return (primary_position in self.striker_positions or 
                (secondary_position and secondary_position in self.striker_positions))
    
    def build_striker_profile(
        self, 
        player_id: str, 
        player_name: str = None,
        team_name: str = None,
        primary_position: str = None,
        secondary_position: str = None,
        season: str = "2024/25",
        # Additional stats
        minutes: int = 0,
        appearances: int = 0,
        goals: int = 0,
        assists: int = 0,
        foot: str = "—",
        age: str = "—"
    ) -> Optional[Dict[str, Any]]:
        """
        Build a striker tactical profile payload.
        
        Args:
            player_id: Player identifier
            player_name: Player name (optional)
            team_name: Team name (optional)
            primary_position: Primary position (optional)
            secondary_position: Secondary position (optional)
            season: Season identifier (optional)
            
        Returns:
            Profile payload dict or None if player not found or not a striker
        """
        # Check if player is a striker
        if primary_position and not self.is_striker(primary_position, secondary_position):
            return None
        
        # Get ability scores and percentiles for the specific season
        season_id = self._extract_season_id(season)
        ability_scores = self.loader.get_player_ability_scores(player_id, season_id)
        percentiles = self.loader.get_player_percentiles(player_id, season_id)
        
        # If no data found, return None
        if not ability_scores and not percentiles:
            return None
        
        # Get league reference
        league_reference = self.loader.get_league_reference()
        
        # Build profile payload
        profile = {
            "player_id": player_id,
            "player_name": player_name or "Unknown Player",
            "team_name": team_name or "Unknown Team",
            "position": self._format_position(primary_position, secondary_position),
            "season": season,
            "ability_scores": ability_scores or {},
            "percentiles": percentiles or {},
            "league_reference": league_reference or {},
            # Additional stats
            "stats": {
                "minutes": minutes,
                "appearances": appearances,
                "goals": goals,
                "assists": assists,
                "foot": foot,
                "age": age
            },
            "meta": {
                "data_version": "v1",
                "computed_at": "2025-10-21",
                "is_striker": True
            }
        }
        
        return profile
    
    def _format_position(self, primary_position: Optional[str], secondary_position: Optional[str]) -> str:
        """Format position display string."""
        if not primary_position:
            return "Striker"
        
        if secondary_position and secondary_position != primary_position:
            return f"{primary_position} / {secondary_position}"
        else:
            return primary_position
    
    def _extract_season_id(self, season: str) -> Optional[str]:
        """Extract season ID from season string."""
        season_mapping = {
            "2024/25": "317",
            "2023/24": "281", 
            "2022/23": "235",
            "2021/22": "108"
        }
        return season_mapping.get(season)
    
    def get_profile_summary(self, player_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a summary of a player's tactical profile without full details.
        Useful for quick checks and validation.
        """
        ability_scores = self.loader.get_player_ability_scores(player_id)
        percentiles = self.loader.get_player_percentiles(player_id)
        
        if not ability_scores and not percentiles:
            return None
        
        # Calculate overall percentile average
        if percentiles:
            avg_percentile = sum(percentiles.values()) / len(percentiles)
        else:
            avg_percentile = None
        
        return {
            "player_id": player_id,
            "has_data": True,
            "avg_percentile": avg_percentile,
            "ability_count": len(ability_scores) if ability_scores else 0,
            "percentile_count": len(percentiles) if percentiles else 0
        }


# Global service instance
_service_instance: Optional[TacticalProfileService] = None


def get_service() -> TacticalProfileService:
    """Get the global service instance."""
    global _service_instance
    if _service_instance is None:
        _service_instance = TacticalProfileService()
    return _service_instance
