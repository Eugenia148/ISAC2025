# ==========================================
# config.py
# Centralized configuration for API credentials and connections
# ==========================================

import os
from dotenv import load_dotenv
from statsbombpy import sb
import warnings

# Load environment variables from .env file
load_dotenv()

class StatsBombConfig:
    """Centralized configuration for StatsBomb API access."""
    
    def __init__(self):
        """Initialize StatsBomb configuration with credentials from environment variables."""
        # Load credentials with fallback to different naming conventions
        self.username = (
            os.getenv('SB_USERNAME') or 
            os.getenv('STATSBOMB_USER') or 
            os.getenv('STATSBOMB_USERNAME')
        )
        self.password = (
            os.getenv('SB_PASSWORD') or 
            os.getenv('STATSBOMB_PASS') or 
            os.getenv('STATSBOMB_PASSWORD')
        )
        
        # Check if credentials are available
        self.has_credentials = bool(self.username and self.password)
        
        if self.has_credentials:
            print("StatsBomb API credentials loaded successfully")
            print(f"   Username: {self.username[:3]}***")
        else:
            print("No StatsBomb credentials found - using open data access only")
    
    def get_client(self):
        """Get the StatsBomb client."""
        return sb
    
    def has_premium_access(self):
        """Check if premium access credentials are available."""
        return self.has_credentials

# Global instance for easy importing
statsbomb_config = StatsBombConfig()

# Convenience function to get the StatsBomb client
def get_statsbomb_client():
    """
    Get a StatsBomb client.
    
    Returns:
        statsbombpy.sb: StatsBomb client
        
    Example:
        from src.config import get_statsbomb_client
        
        sb = get_statsbomb_client()
        competitions = sb.competitions()
    """
    return statsbomb_config.get_client()

# Convenience function to check if premium access is available
def is_premium_access():
    """
    Check if premium access credentials are available.
    
    Returns:
        bool: True if credentials are available, False otherwise
    """
    return statsbomb_config.has_premium_access()

# Print configuration status on import
if __name__ == "__main__":
    print(f"Premium Access Available: {statsbomb_config.has_premium_access()}")
