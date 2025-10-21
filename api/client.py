"""
StatsBomb API Client
Centralized API client that handles authentication and provides clean methods for data access.
"""

import os
from typing import Optional, Dict, List
from dotenv import load_dotenv
from statsbombpy import sb
import warnings
import requests
from requests.auth import HTTPBasicAuth

# Load environment variables once
load_dotenv()

class StatsBombClient:
    """Centralized StatsBomb API client with authentication."""
    
    def __init__(self):
        """Initialize the client with credentials."""
        self.username = os.getenv('SB_USERNAME')
        self.password = os.getenv('SB_PASSWORD')
        self.has_credentials = bool(self.username and self.password)
        
        if self.has_credentials:
            print(f"StatsBomb client initialized with credentials: {self.username[:3]}***")
        else:
            print("StatsBomb client initialized without credentials (open data only)")
    
    def _get_creds(self) -> Optional[Dict[str, str]]:
        """Get credentials if available."""
        if self.has_credentials:
            return {'user': self.username, 'passwd': self.password}
        return None
    
    def competitions(self):
        """Get all available competitions."""
        try:
            creds = self._get_creds()
            if creds:
                return sb.competitions(creds=creds)
            else:
                return sb.competitions()
        except Exception as e:
            print(f"Error fetching competitions: {e}")
            return None
    
    def team_season_stats(self, competition_id: int, season_id: int):
        """Get team season statistics for a specific competition and season."""
        try:
            creds = self._get_creds()
            if creds:
                return sb.team_season_stats(competition_id=competition_id, season_id=season_id, creds=creds)
            else:
                return sb.team_season_stats(competition_id=competition_id, season_id=season_id)
        except Exception as e:
            print(f"Error fetching team season stats: {e}")
            return None
    
    def matches(self, competition_id: int, season_id: int):
        """Get matches for a specific competition and season."""
        try:
            creds = self._get_creds()
            if creds:
                return sb.matches(competition_id=competition_id, season_id=season_id, creds=creds)
            else:
                return sb.matches(competition_id=competition_id, season_id=season_id)
        except Exception as e:
            print(f"Error fetching matches: {e}")
            return None
    
    def player_season_stats(self, competition_id: int, season_id: int):
        """Get player season statistics for a specific competition and season."""
        try:
            creds = self._get_creds()
            if creds:
                return sb.player_season_stats(competition_id=competition_id, season_id=season_id, creds=creds)
            else:
                return sb.player_season_stats(competition_id=competition_id, season_id=season_id)
        except Exception as e:
            print(f"Error fetching player season stats: {e}")
            return None
    
    def player_mapping(self, competition_id: int, season_id: int):
        """Get player mapping data for a specific competition and season via direct API call."""
        try:
            # API endpoint for player mapping
            url = "https://data.statsbomb.com/api/v1/player-mapping"
            
            # Query parameters
            params = {
                'competition-id': competition_id,
                'season-id': season_id
            }
            
            # Make request with or without credentials
            if self.has_credentials:
                auth = HTTPBasicAuth(self.username, self.password)
                response = requests.get(url, params=params, auth=auth)
            else:
                response = requests.get(url, params=params)
            
            # Check if request was successful
            if response.status_code == 200:
                return response.json()
            else:
                print(f"Player mapping API request failed with status {response.status_code}")
                return None
                
        except Exception as e:
            print(f"Error fetching player mapping: {e}")
            return None
    
    def get_status(self) -> Dict[str, any]:
        """Get API connection status."""
        try:
            competitions = self.competitions()
            if competitions is not None and len(competitions) > 0:
                return {
                    "ok": True,
                    "message": f"Connected (Premium: {'Yes' if self.has_credentials else 'No'})",
                    "premium_access": self.has_credentials,
                    "competitions_count": len(competitions)
                }
            else:
                return {"ok": False, "message": "No data returned"}
        except Exception as e:
            return {"ok": False, "message": f"Connection failed: {str(e)}"}

# Global client instance
client = StatsBombClient()

# Convenience functions for easy importing
def get_competitions():
    """Get all competitions."""
    return client.competitions()

def get_team_season_stats(competition_id: int, season_id: int):
    """Get team season stats."""
    return client.team_season_stats(competition_id, season_id)

def get_matches(competition_id: int, season_id: int):
    """Get matches."""
    return client.matches(competition_id, season_id)

def get_player_season_stats(competition_id: int, season_id: int):
    """Get player season stats."""
    return client.player_season_stats(competition_id, season_id)

def get_player_mapping(competition_id: int, season_id: int):
    """Get player mapping data."""
    return client.player_mapping(competition_id, season_id)

def get_status():
    """Get API status."""
    return client.get_status()