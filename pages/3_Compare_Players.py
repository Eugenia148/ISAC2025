# 3_Compare_Players.py

"""
⚖️ Compare Players – Liga MX
Side-by-side comparison of two players' tactical profiles.
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
from api.client import client
import pandas as pd
from datetime import datetime
from core.profiles.service import get_service
from ui.components.radar import render_tactical_profile_radar

# Page configuration
st.set_page_config(
    page_title="Compare Players – Liga MX",
    page_icon="⚖️",
    layout="wide"
)


# ===== HELPER FUNCTIONS =====

def get_mode_options(position_group: str) -> list:
    """Get available display modes for a position group."""
    if position_group in ["deep_progression", "attacking_mid_winger"]:
        return ["zscore", "l2", "percentile"]
    else:
        return ["percentile", "absolute"]


def get_mode_label(mode: str) -> str:
    """Get display label for a mode."""
    mode_labels = {
        "zscore": "📊 Performance (Percentile Rank)",
        "l2": "🎨 Style (L2-normalized)",
        "percentile": "📈 Raw Percentiles",
        "absolute": "📈 Raw Scores"
    }
    return mode_labels.get(mode, mode)


def render_player_comparison_profile(player_data: dict, player_num: int):
    """
    Render a single player's profile in comparison view.
    
    Args:
        player_data: Dict with player info and stats
        player_num: 1 or 2 (for unique widget keys)
    """
    # Build profile using service
    service = get_service()
    
    # Parse position
    primary_position = player_data['position'].split(' / ')[0] if player_data['position'] else None
    secondary_position = player_data['position'].split(' / ')[1] if ' / ' in player_data['position'] else None
    
    profile = service.build_profile(
        player_id=player_data['player_id'],
        player_name=player_data['player_name'],
        team_name=player_data['team_name'],
        primary_position=primary_position,
        secondary_position=secondary_position,
        season=player_data['season'],
        **player_data['stats']
    )
    
    if not profile:
        st.warning(f"No tactical profile available for {player_data['player_name']}")
        st.caption(f"Position: {player_data['position']}")
        st.info("Tactical profiles are available for Strikers, Deep Progression Unit (Full-backs & Midfielders), and Attacking Midfielders & Wingers.")
        return
    
    # Display player header
    st.markdown(f"### {player_data['player_name']}")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.info(f"🏟️ **{player_data['team_name']}**")
    with col2:
        st.info(f"⚽ **{player_data['position']}**")
    with col3:
        st.info(f"📅 **{player_data['season']}**")
    
    # Stats row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("🎮 Games", player_data['stats']['appearances'])
    with col2:
        st.metric("⏱️ Minutes", f"{int(player_data['stats']['minutes']):,}")
    with col3:
        st.metric("⚽ Goals", player_data['stats']['goals'])
    with col4:
        st.metric("🎯 Assists", player_data['stats']['assists'])
    
    st.divider()
    
    # Mode toggle (with unique key)
    position_group = profile.get("meta", {}).get("position_group", "striker")
    mode_options = get_mode_options(position_group)
    
    # Default mode
    default_mode = "zscore" if position_group in ["deep_progression", "attacking_mid_winger"] else "percentile"
    
    mode = st.radio(
        "Display Mode:",
        options=mode_options,
        format_func=get_mode_label,
        key=f"mode_player_{player_num}",
        horizontal=True,
        index=mode_options.index(default_mode) if default_mode in mode_options else 0
    )
    
    # Render radar
    render_tactical_profile_radar(profile, mode=mode, show_league_average=False)


def fetch_season_data(competition_id: int, season_id: int):
    """Fetch player data for a given season."""
    try:
        # Fetch player season stats
        season_stats = client.player_season_stats(
            competition_id=competition_id,
            season_id=season_id
        )
        
        # Fetch player mapping data
        mapping = client.player_mapping(
            competition_id=competition_id,
            season_id=season_id
        )
        
        # Fallback: if no player data, try team data
        if season_stats is None or len(season_stats) == 0:
            season_stats = client.team_season_stats(
                competition_id=competition_id,
                season_id=season_id
            )
            mapping = None
        
        return {
            'season_stats': season_stats,
            'mapping': mapping
        }
    except Exception as e:
        st.error(f"Error fetching season data: {e}")
        return None


def build_player_rows(payload):
    """Build player rows from season data using robust pandas processing."""
    if payload is None or payload.get('season_stats') is None:
        return []
    
    season_stats = payload['season_stats']
    mapping = payload.get('mapping')
    
    if len(season_stats) == 0:
        return []
    
    # Convert to DataFrame for easier processing
    stats_df = pd.DataFrame(season_stats)
    
    # Check if this is player-level or team-level data
    if "player_name" not in stats_df.columns:
        # Team-level fallback
        return []
    
    # Player-level data processing
    rows = []
    
    # Create mapping lookup if available
    mapping_lookup = {}
    if mapping is not None and len(mapping) > 0:
        try:
            mapping_df = pd.DataFrame(mapping)
            
            for _, row in mapping_df.iterrows():
                player_id = row.get('player_id') or row.get('offline_player_id') or row.get('live_player_id')
                if player_id:
                    mapping_lookup[player_id] = {
                        'preferred_foot': row.get('player_preferred_foot', '—'),
                        'birth_date': row.get('player_birth_date')
                    }
        except Exception as e:
            print(f"Error processing mapping data: {e}")
    
    # Process each player
    for _, player in stats_df.iterrows():
        player_id = player.get('player_id')
        player_name = player.get('player_name', '—')
        team_name = player.get('team_name', '—')
        primary_position = player.get('primary_position', '—')
        secondary_position = player.get('secondary_position', '—')
        minutes = player.get('player_season_minutes', 0)
        appearances = player.get('player_season_appearances', 0)
        goals_90 = player.get('player_season_goals_90', 0)
        assists_90 = player.get('player_season_assists_90', 0)
        
        # Calculate total goals and assists from per-90 stats
        total_goals = round(goals_90 * minutes / 90) if minutes > 0 else 0
        total_assists = round(assists_90 * minutes / 90) if minutes > 0 else 0
        
        # Round minutes to nearest full minute
        minutes = int(round(minutes)) if minutes > 0 else 0
        
        # Position display
        if secondary_position and secondary_position != '—':
            position_display = f"{primary_position} / {secondary_position}"
        else:
            position_display = primary_position
        
        # Get mapping data
        preferred_foot = '—'
        age = '—'
        
        if player_id and player_id in mapping_lookup:
            mapping_data = mapping_lookup[player_id]
            preferred_foot = mapping_data['preferred_foot']
            
            # Calculate age from birth date
            birth_date = mapping_data['birth_date']
            if birth_date:
                try:
                    birth_dt = datetime.strptime(birth_date, '%Y-%m-%d')
                    # Calculate age as of today
                    today = datetime.now()
                    age = today.year - birth_dt.year - ((today.month, today.day) < (birth_dt.month, birth_dt.day))
                except:
                    age = '—'
        
        # Create row
        row = {
            'player_id': player_id,
            'Player': player_name,
            'Team': team_name,
            'Position': position_display,
            'Minutes': minutes,
            'Appearances': appearances,
            'Goals': total_goals,
            'Assists': total_assists,
            'Foot': preferred_foot,
            'Age': age
        }
        
        rows.append(row)
    
    return rows


def render_player_selector(player_num: int, season_filter: str = None):
    """
    Render player selector for player 2.
    
    Args:
        player_num: 2 (for unique widget keys)
        season_filter: Optional season to filter by (defaults to player 1's season)
    """
    st.markdown("### Select Player to Compare")
    
    # Season selector
    season_options = {
        "2024/25": (73, 317),
        "2023/24": (73, 281),
        "2022/23": (73, 235),
        "2021/22": (73, 108)
    }
    
    # Default to player 1's season if provided
    default_season = season_filter if season_filter and season_filter in season_options else "2024/25"
    default_index = list(season_options.keys()).index(default_season)
    
    selected_season = st.selectbox(
        "Select Season",
        options=list(season_options.keys()),
        index=default_index,
        key=f"season_selector_player_{player_num}"
    )
    competition_id, season_id = season_options[selected_season]
    
    # Fetch data
    with st.spinner("Loading player data..."):
        payload = fetch_season_data(competition_id, season_id)
    
    if not payload:
        return None
    
    rows = build_player_rows(payload)
    
    if not rows:
        st.warning("No player data available for this season.")
        return None
    
    # Filters
    st.markdown("#### Filters")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Team filter
        teams = sorted(list(set(r['Team'] for r in rows if r.get('Team') and r['Team'] != '—')))
        selected_team = st.selectbox(
            "Team",
            options=['All'] + teams,
            key=f"team_filter_player_{player_num}"
        )
    
    with col2:
        # Position filter - extract individual positions (primary and secondary)
        positions_set = set()
        for r in rows:
            pos_str = r.get('Position', '')
            if pos_str and pos_str != '—':
                # Split by ' / ' to get individual positions
                for pos in pos_str.split(' / '):
                    pos = pos.strip()
                    if pos:
                        positions_set.add(pos)
        positions = sorted(list(positions_set))
        
        selected_position = st.selectbox(
            "Position",
            options=['All'] + positions,
            key=f"position_filter_player_{player_num}"
        )
    
    # Name search
    name_search = st.text_input(
        "Search by name",
        key=f"name_search_player_{player_num}"
    )
    
    # Apply filters
    filtered_rows = rows
    
    if selected_team != 'All':
        filtered_rows = [r for r in filtered_rows if r['Team'] == selected_team]
    
    if selected_position != 'All':
        # Check if selected position is in either primary or secondary position
        filtered_rows = [r for r in filtered_rows 
                        if r.get('Position') and selected_position in r['Position'].split(' / ')]
    
    if name_search:
        filtered_rows = [r for r in filtered_rows if name_search.lower() in r['Player'].lower()]
    
    st.info(f"Showing {len(filtered_rows)} of {len(rows)} players")
    
    # Display table
    if filtered_rows:
        df = pd.DataFrame(filtered_rows)
        display_df = df.drop(columns=['player_id'], errors='ignore')
        
        selected_rows = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row",
            key=f"player_table_{player_num}"
        )
        
        # Handle selection
        if selected_rows.selection.rows:
            selected_idx = selected_rows.selection.rows[0]
            selected_player = filtered_rows[selected_idx]
            
            # Build player data structure
            player_data = {
                'player_id': selected_player['player_id'],
                'player_name': selected_player['Player'],
                'team_name': selected_player['Team'],
                'position': selected_player['Position'],
                'season': selected_season,
                'stats': {
                    'minutes': selected_player['Minutes'],
                    'appearances': selected_player['Appearances'],
                    'goals': selected_player['Goals'],
                    'assists': selected_player['Assists'],
                    'foot': selected_player['Foot'],
                    'age': selected_player['Age']
                }
            }
            
            return player_data
    
    return None


# ===== MAIN PAGE =====

st.title("⚖️ Compare Players")
st.caption("Side-by-side comparison of tactical profiles")

# Back button and clear selections
col_btn1, col_btn2 = st.columns([1, 3])
with col_btn1:
    if st.button("← Back to Player Database"):
        st.switch_page("pages/2_Player_Database.py")
with col_btn2:
    if 'compare_player_1' in st.session_state or 'compare_player_2' in st.session_state:
        if st.button("🔄 Clear All Selections", type="secondary"):
            if 'compare_player_1' in st.session_state:
                del st.session_state['compare_player_1']
            if 'compare_player_2' in st.session_state:
                del st.session_state['compare_player_2']
            st.rerun()

st.divider()

# Create two columns for side-by-side comparison
col1, col2 = st.columns(2, gap="large")

# LEFT COLUMN: Player 1
with col1:
    st.markdown("## Player 1")
    
    # Check if player 1 is already selected (from database or previous selection)
    if 'compare_player_1' in st.session_state:
        # Option to change selection
        if st.button("🔄 Change Player 1", key="change_player_1"):
            del st.session_state['compare_player_1']
            st.rerun()
        
        st.divider()
        render_player_comparison_profile(st.session_state['compare_player_1'], player_num=1)
    else:
        # Show player selector
        st.info("👈 Select a player to start comparison")
        player_1_data = render_player_selector(
            player_num=1,
            season_filter=None
        )
        
        # If player selected, store in session state
        if player_1_data:
            st.session_state['compare_player_1'] = player_1_data
            st.rerun()

# RIGHT COLUMN: Player 2
with col2:
    st.markdown("## Player 2")
    
    # Only show player 2 selector if player 1 is selected
    if 'compare_player_1' not in st.session_state:
        st.info("👈 Please select Player 1 first")
    else:
        # Check if player 2 is already selected
        if 'compare_player_2' in st.session_state:
            # Option to change selection
            if st.button("🔄 Change Player 2", key="change_player_2"):
                del st.session_state['compare_player_2']
                st.rerun()
            
            st.divider()
            render_player_comparison_profile(st.session_state['compare_player_2'], player_num=2)
        else:
            # Show player selector
            st.info("👈 Select a player to compare")
            player_2_data = render_player_selector(
                player_num=2,
                season_filter=st.session_state['compare_player_1'].get('season')
            )
            
            # If player selected, store in session state
            if player_2_data:
                st.session_state['compare_player_2'] = player_2_data
                st.rerun()

