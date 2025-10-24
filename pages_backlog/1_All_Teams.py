"""
All Teams Page - Display all teams from Liga MX
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
from api.client import client

# Page configuration
st.set_page_config(
    page_title="All Teams - Liga MX",
    page_icon="📋",
    layout="wide"
)


# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====

def teams_fetch(api_client, competition_id=73, season_id=317):
    """
    Fetch team season stats from API.
    
    Args:
        api_client: The StatsBomb API client instance
        competition_id: Competition ID (default: 73 for Liga MX)
        season_id: Season ID (default: 317 for 2024/2025)
        
    Returns:
        DataFrame | None: Raw team stats data or None if unavailable
    """
    try:
        teams_df = api_client.team_season_stats(
            competition_id=competition_id, 
            season_id=season_id
        )
        return teams_df
    except Exception as e:
        print(f"Failed to fetch teams: {e}")
        return None


def teams_compute_table(raw_df):
    """
    Compute UI-ready table from raw team stats.
    
    Args:
        raw_df: Raw DataFrame from API or None
        
    Returns:
        list[dict] | None: List of dicts with Team, Matches, Competition, Season
                          or None if no data
    """
    if raw_df is None or len(raw_df) == 0:
        return None
    
    try:
        # Select and rename columns for display
        display_columns = ['team_name', 'team_season_matches', 'competition_name', 'season_name']
        available_columns = [col for col in display_columns if col in raw_df.columns]
        
        if not available_columns:
            return None
        
        # Create table data
        table_data = raw_df[available_columns].copy()
        table_data = table_data.rename(columns={
            'team_name': 'Team',
            'team_season_matches': 'Matches',
            'competition_name': 'Competition',
            'season_name': 'Season'
        })
        
        return table_data
    except Exception as e:
        print(f"Failed to compute table: {e}")
        return None


def teams_compute_stats(raw_df):
    """
    Compute summary statistics from raw team data.
    
    Args:
        raw_df: Raw DataFrame from API or None
        
    Returns:
        dict | None: Dict with 'total_teams', 'avg_matches', 'total_matches'
                    or None if no data
    """
    if raw_df is None or len(raw_df) == 0:
        return None
    
    try:
        stats = {
            'total_teams': len(raw_df),
            'avg_matches': raw_df['team_season_matches'].mean() if 'team_season_matches' in raw_df.columns else None,
            'total_matches': int(raw_df['team_season_matches'].sum()) if 'team_season_matches' in raw_df.columns else None
        }
        return stats
    except Exception as e:
        print(f"Failed to compute stats: {e}")
        return None


# ===== UI (STREAMLIT ONLY BELOW) =====

# Page header
st.title("📋 All Teams - Liga MX 2024/2025")
st.markdown("View all teams in Liga MX with their season statistics")

# Fetch data
st.markdown("---")
st.subheader("⚽ Teams")

with st.spinner("Loading teams data..."):
    raw_teams = teams_fetch(client, competition_id=73, season_id=317)

# Compute table and stats
table_data = teams_compute_table(raw_teams)
stats = teams_compute_stats(raw_teams)

# Display results
if table_data is not None:
    st.success(f"✅ Found {len(table_data)} teams")
    
    # Display table
    st.dataframe(
        table_data,
        use_container_width=True,
        hide_index=True
    )
    
    # Display stats
    if stats:
        st.markdown("---")
        st.subheader("📊 Quick Stats")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric("Total Teams", stats['total_teams'])
        
        with col2:
            if stats['avg_matches'] is not None:
                st.metric("Avg Matches/Team", f"{stats['avg_matches']:.1f}")
            else:
                st.metric("Avg Matches/Team", "N/A")
        
        with col3:
            if stats['total_matches'] is not None:
                st.metric("Total Matches", stats['total_matches'])
            else:
                st.metric("Total Matches", "N/A")

else:
    st.error("❌ **no data available**")
    st.info("""
    No team data found for Liga MX 2024/2025.
    
    This could mean:
    - API credentials issue
    - Data not available for this season
    - Network connection problem
    """)

# Footer
st.markdown("---")
st.caption("*Data from StatsBomb API • Use sidebar to navigate*")
