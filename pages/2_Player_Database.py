# 2_Player_Database.py

"""
🧩 Player Database – Liga MX 2024/25
Displays player-level attributes if available.
Falls back to team-level data when player stats are not provided by the API.
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
from api.client import client
import pandas as pd

# Page configuration
st.set_page_config(
    page_title="Player Database – Liga MX",
    page_icon="🧩",
    layout="wide"
)


# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====
def players_fetch(api_client, competition_id=73, season_id=317, test_mode=False):
    """
    Fetch player data for Liga MX. 
    Falls back to team data if the player endpoint returns empty.

    Args:
        api_client: StatsBomb API client instance
        competition_id: Default = 73 (Liga MX)
        season_id: Default = 317 (2024/25)
        test_mode: If True, loads Premier League sample data
    """
    try:
        # Optional test mode to use Premier League Open Data
        if test_mode:
            print("🧪 Test mode enabled: loading Premier League data instead of Liga MX.")
            return api_client.player_season_stats(competition_id=43, season_id=106)

        # Try fetching players
        players_df = api_client.player_season_stats(
            competition_id=competition_id,
            season_id=season_id
        )

        # Fallback: if empty, fetch teams
        if players_df is None or len(players_df) == 0:
            print("⚠️ No player data found — using team data as fallback.")
            players_df = api_client.team_season_stats(
                competition_id=competition_id,
                season_id=season_id
            )

        return players_df

    except Exception as e:
        print(f"Failed to fetch players: {e}")
        return None


def players_compute_table(raw_df):
    """
    Prepare player/team data for Streamlit display.
    """
    if raw_df is None or len(raw_df) == 0:
        return None

    # Try to identify if this is player-level or team-level data
    if "player_name" in raw_df.columns:
        desired_cols = [
            "player_name", "team_name", "player_position",
            "player_age", "player_height", "player_weight",
            "player_foot", "player_nationality"
        ]
        available_cols = [c for c in desired_cols if c in raw_df.columns]
        table = raw_df[available_cols].copy()
        table = table.rename(columns={
            "player_name": "Name",
            "team_name": "Team",
            "player_position": "Position",
            "player_age": "Age",
            "player_height": "Height (cm)",
            "player_weight": "Weight (kg)",
            "player_foot": "Foot",
            "player_nationality": "Nationality"
        })
    else:
        # Fallback: team-level data
        desired_cols = ["team_name", "competition_name", "season_name", "team_season_matches"]
        available_cols = [c for c in desired_cols if c in raw_df.columns]
        table = raw_df[available_cols].copy()
        table = table.rename(columns={
            "team_name": "Team",
            "competition_name": "Competition",
            "season_name": "Season",
            "team_season_matches": "Matches"
        })

    return table


# ===== UI (STREAMLIT BELOW) =====
st.title("🧩 Player Database – Liga MX 2024/25")
st.markdown("View all players and their attributes. If unavailable, team stats will be shown instead.")

# User option for test mode
test_mode = st.toggle("🧪 Use Premier League (Open Data) for testing", value=False)

# Fetch data
with st.spinner("Loading data from StatsBomb API..."):
    raw_data = players_fetch(client, competition_id=73, season_id=317, test_mode=test_mode)

# Compute table
table = players_compute_table(raw_data)

# Display results
if table is not None:
    st.success(f"✅ Loaded {len(table)} entries")

    # Add filters dynamically
    if "Team" in table.columns:
        col1, col2 = st.columns(2)
        with col1:
            team_filter = st.selectbox(
                "Filter by Team",
                options=["All"] + sorted(table["Team"].dropna().unique().tolist())
            )
        with col2:
            if "Position" in table.columns:
                pos_filter = st.selectbox(
                    "Filter by Position",
                    options=["All"] + sorted(table["Position"].dropna().unique().tolist())
                )
            else:
                pos_filter = "All"

        # Apply filters
        filtered = table.copy()
        if team_filter != "All":
            filtered = filtered[filtered["Team"] == team_filter]
        if pos_filter != "All" and "Position" in filtered.columns:
            filtered = filtered[filtered["Position"] == pos_filter]

        st.dataframe(filtered, use_container_width=True, hide_index=True)
    else:
        st.dataframe(table, use_container_width=True, hide_index=True)

else:
    st.error("❌ No data available")
    st.info("""
    Possible reasons:
    - The Liga MX endpoint for player stats is not enabled  
    - API credentials are fine, but the dataset is restricted  
    - Try the 🧪 'Test mode' toggle above to load Premier League data
    """)

st.markdown("---")
st.caption("*ISAC2025 • Data via StatsBomb API (Hudl)*")
