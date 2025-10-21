"""
⚽ Striker Profiles – Liga MX 2024/25
Analyze offensive players: goals, xG, assists, and other key metrics.
"""

# ===== IMPORTS & CONFIG =====
import streamlit as st
from api.client import client
import pandas as pd
import plotly.express as px

# Streamlit page setup
st.set_page_config(
    page_title="Striker Profiles – Liga MX",
    page_icon="⚽",
    layout="wide"
)


# ===== BUSINESS LOGIC =====
def fetch_strikers(api_client, competition_id=73, season_id=317, test_mode=False):
    """
    Fetch player-level data and filter strikers (ST, CF, LW, RW).
    Falls back to demo data if API returns empty.
    """
    try:
        if test_mode:
            print("🧪 Using Premier League Open Data for testing.")
            df = api_client.player_season_stats(competition_id=43, season_id=106)
        else:
            df = api_client.player_season_stats(competition_id=competition_id, season_id=season_id)

        if df is None or len(df) == 0:
            print("⚠️ No data from API — using demo fallback.")
            return demo_strikers()

        # Filter strikers by position if column exists
        if "player_position" in df.columns:
            df = df[df["player_position"].isin(["ST", "CF", "LW", "RW", "FW"])]

        # Keep only relevant columns if available
        keep_cols = [
            "player_name", "team_name", "player_position",
            "player_season_goals_90", "player_season_xa_90", 
            "player_season_np_xg_90", "player_season_np_shots_90",
            "player_season_key_passes_90", "player_season_minutes"
        ]
        df = df[[c for c in keep_cols if c in df.columns]].copy()

        # Rename for readability
        df = df.rename(columns={
            "player_name": "Name",
            "team_name": "Team",
            "player_position": "Position",
            "player_season_goals_90": "Goals/90",
            "player_season_xa_90": "xA/90",
            "player_season_np_xg_90": "xG/90",
            "player_season_np_shots_90": "Shots/90",
            "player_season_key_passes_90": "Key Passes/90",
            "player_season_minutes": "Minutes"
        })

        # Basic filter for valid players
        df = df[df["Minutes"] > 200] if "Minutes" in df.columns else df

        return df.reset_index(drop=True)

    except Exception as e:
        print(f"Error loading striker data: {e}")
        return demo_strikers()


def demo_strikers():
    """Fallback demo dataset if API fails."""
    demo = pd.DataFrame({
        "Name": ["Henry Martín", "Jonathan Rodríguez", "Julián Quiñones", "Uriel Antuna", "Rogelio Funes Mori"],
        "Team": ["América", "América", "América", "Cruz Azul", "Monterrey"],
        "Position": ["ST", "LW", "CF", "RW", "ST"],
        "Goals/90": [0.65, 0.42, 0.55, 0.38, 0.47],
        "xG/90": [0.63, 0.48, 0.52, 0.41, 0.44],
        "xA/90": [0.18, 0.21, 0.22, 0.27, 0.16],
        "Shots/90": [3.8, 3.1, 3.5, 2.9, 3.2],
        "Key Passes/90": [0.9, 1.0, 0.7, 1.2, 0.8],
        "Minutes": [1900, 1750, 2000, 1800, 1600]
    })
    return demo


# ===== UI (STREAMLIT) =====
st.title("⚽ Striker Profiles – Liga MX 2024/25")
st.markdown("Explore key offensive metrics (goals, xG, assists, key passes) for forwards in Liga MX.")

# Switch for test mode
test_mode = st.toggle("🧪 Use Premier League (Open Data) for testing", value=False)

# Fetch and process
with st.spinner("Loading striker data..."):
    strikers = fetch_strikers(client, competition_id=73, season_id=317, test_mode=test_mode)

if strikers is not None and len(strikers) > 0:
    st.success(f"✅ Loaded {len(strikers)} strikers")

    # Filters
    col1, col2 = st.columns(2)
    with col1:
        team_filter = st.selectbox("Filter by Team", ["All"] + sorted(strikers["Team"].dropna().unique().tolist()))
    with col2:
        metric = st.selectbox("Select Ranking Metric", ["Goals/90", "xG/90", "xA/90", "Shots/90", "Key Passes/90"])

    filtered = strikers.copy()
    if team_filter != "All":
        filtered = filtered[filtered["Team"] == team_filter]

    # Ranking table
    top = filtered.sort_values(by=metric, ascending=False).head(20)
    st.subheader(f"🏅 Top Strikers by {metric}")
    st.dataframe(top, use_container_width=True, hide_index=True)

    # Plot
    if len(top) > 0:
        fig = px.bar(
            top,
            x="Name",
            y=metric,
            color="Team",
            text=metric,
            title=f"Top 20 Players by {metric}",
            height=500
        )
        fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
        fig.update_layout(xaxis_title="", yaxis_title=metric, showlegend=True)
        st.plotly_chart(fig, use_container_width=True)

else:
    st.error("❌ No striker data available.")
    st.info("Try enabling 🧪 test mode or check API access.")

st.markdown("---")
st.caption("*ISAC2025 • Data via StatsBomb API (Hudl)*")
