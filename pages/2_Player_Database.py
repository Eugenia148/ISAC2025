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
from core.profiles.service import get_service
from core.performance.service import get_performance_service
from core.roles.service import get_role_service
from core.roles.loader import reset_role_loader
from ui.components.radar import render_tactical_profile_panel
from ui.components.performance_radar import render_performance_profile_panel
from ui.components.player_role_header import render_player_role_section

from ui.components.radar import render_tactical_profile_panel

# Page configuration
st.set_page_config(
    page_title="Player Database – Liga MX",
    page_icon="🧩",
    layout="wide"
)

# Force reload of role loader to get latest cluster names
reset_role_loader()


# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====
def feature_fetch_season(api_client, *, competition_id: int, season_id: int) -> dict | None:
    """
    Fetch both player season stats and player mapping data for a specific competition and season.
    
    Returns:
      {
        'season_stats': list[dict],    # Season Player Stats rows
        'mapping': list[dict],         # Player Mapping rows (same comp/season)
      }
    """
    try:
        # Fetch player season stats
        season_stats = api_client.player_season_stats(
            competition_id=competition_id,
            season_id=season_id
        )
        
        # Fetch player mapping data
        mapping = api_client.player_mapping(
            competition_id=competition_id,
            season_id=season_id
        )
        
        # Fallback: if no player data, try team data
        if season_stats is None or len(season_stats) == 0:
            print("⚠️ No player data found — using team data as fallback.")
            season_stats = api_client.team_season_stats(
                competition_id=competition_id,
                season_id=season_id
            )
            mapping = None  # No mapping data for team-level fallback
        
        return {
            'season_stats': season_stats,
            'mapping': mapping
        }

    except Exception as e:
        print(f"Failed to fetch season data: {e}")
        return None


def feature_compute_rows(payload: dict) -> dict | None:
    """
    Joins Season Player Stats with Player Mapping on player_id.
    Derives goals/assists totals, position display, age, and collects filter options.

    Returns:
      {
        'rows': list[dict],         # final table rows (see columns)
        'teams': list[str],         # unique team_name
        'positions': list[str],     # unique primary_position
        'foots': list[str],         # unique preferred foot values
        'age_min': int, 'age_max': int
      }
    """
    if payload is None or payload.get('season_stats') is None:
        return None
    
    season_stats = payload['season_stats']
    mapping = payload.get('mapping')
    
    if len(season_stats) == 0:
        return None
    
    # Convert to DataFrame for easier processing
    import pandas as pd
    stats_df = pd.DataFrame(season_stats)
    
    # Check if this is player-level or team-level data
    if "player_name" not in stats_df.columns:
        # Team-level fallback - return basic team data
        return {
            'rows': stats_df.to_dict('records'),
            'teams': stats_df['team_name'].unique().tolist() if 'team_name' in stats_df.columns else [],
            'positions': [],
            'foots': [],
            'age_min': 0,
            'age_max': 0
        }
    
    # Player-level data processing
    rows = []
    teams = set()
    positions = set()
    foots = set()
    ages = []
    
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
                    from datetime import datetime
                    birth_dt = datetime.strptime(birth_date, '%Y-%m-%d')
                    # Calculate age as of today
                    today = datetime.now()
                    age = today.year - birth_dt.year - ((today.month, today.day) < (birth_dt.month, birth_dt.day))
                    ages.append(age)
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
        
        # Collect filter options (filter out None values)
        if team_name:
            teams.add(team_name)
        if primary_position:
            positions.add(primary_position)
        if preferred_foot:
            foots.add(preferred_foot)
    
    # Calculate age range
    age_min = min(ages) if ages else 0
    age_max = max(ages) if ages else 0
    
    return {
        'rows': rows,
        'teams': sorted(list(teams)),
        'positions': sorted(list(positions)),
        'foots': sorted(list(foots)),
        'age_min': age_min,
        'age_max': age_max
    }


def feature_filter_rows(
    rows: list[dict],
    *,
    q: str,
    teams: list[str],
    positions: list[str],
    foots: list[str],
    age_range: tuple[int, int],
    min_minutes: int
) -> list[dict]:
    """Applies all filters. Keep fast and pure (no streamlit here)."""
    if not rows:
        return []
    
    filtered = rows.copy()
    
    # Search filter (case-insensitive substring match on Player name)
    if q:
        filtered = [row for row in filtered if q.lower() in row.get('Player', '').lower()]
    
    # Team filter
    if teams:
        filtered = [row for row in filtered if row.get('Team') in teams]
    
    # Position filter
    if positions:
        filtered = [row for row in filtered 
                   if row.get('Position') and 
                   row.get('Position', '').split(' / ')[0] in positions]
    
    # Foot filter
    if foots:
        filtered = [row for row in filtered if row.get('Foot') in foots]
    
    # Age range filter
    if age_range[0] > 0 or age_range[1] < 100:
        filtered = [row for row in filtered 
                   if row.get('Age') != '—' and 
                   age_range[0] <= row.get('Age', 0) <= age_range[1]]
    
    # Minutes filter
    if min_minutes > 0:
        filtered = [row for row in filtered if row.get('Minutes', 0) >= min_minutes]
    
    # Sort by Player name (A-Z), then by Minutes (desc)
    filtered.sort(key=lambda x: (x.get('Player', ''), -x.get('Minutes', 0)))
    
    return filtered


# ===== UI (STREAMLIT BELOW) =====
st.title("🧩 Player Database – Liga MX 2024/25")
st.markdown("View all players and their attributes. If unavailable, team stats will be shown instead.")

# Season selection
col1, col2 = st.columns([3, 1])
with col1:
    season_options = {
        "2024/25": (73, 317),
        "2023/24": (73, 281),
        "2022/23": (73, 235),
        "2021/22": (73, 108)
    }
    selected_season = st.selectbox(
        "Select Season",
        options=list(season_options.keys()),
        index=0
    )
    competition_id, season_id = season_options[selected_season]

with col2:
    refresh_clicked = st.button("🔄 Refresh", type="primary")

# Cache key for session state
cache_key = f"player_data_{competition_id}_{season_id}"

# Fetch data if not cached or refresh requested
if cache_key not in st.session_state or refresh_clicked:
    with st.spinner("Loading data from StatsBomb API..."):
        raw_data = feature_fetch_season(client, competition_id=competition_id, season_id=season_id)
        if raw_data:
            computed_data = feature_compute_rows(raw_data)
            st.session_state[cache_key] = computed_data
        else:
            st.session_state[cache_key] = None

# Get cached data
computed_data = st.session_state.get(cache_key)

# Display results
if computed_data is not None and computed_data.get('rows'):
    rows = computed_data['rows']
    st.success(f"✅ Loaded {len(rows)} players")
    
    # Filters section
    st.subheader("🔍 Filters")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Search filter
        search_query = st.text_input("🔍 Search Player", placeholder="Enter player name...")
        
        # Team filter
        selected_teams = st.multiselect(
            "🏟️ Teams",
            options=computed_data.get('teams', []),
            default=[]
        )
    
    with col2:
        # Position filter
        selected_positions = st.multiselect(
            "⚽ Positions",
            options=computed_data.get('positions', []),
            default=[]
        )
        
        # Foot filter
        selected_foots = st.multiselect(
            "🦶 Preferred Foot",
            options=computed_data.get('foots', []),
            default=[]
        )
    
    with col3:
        # Age range filter
        # Minutes filter
        max_minutes = int(max([row.get('Minutes', 0) for row in rows])) if rows else 0
        
        if max_minutes > 0:
            min_minutes = st.slider(
                "⏱️ Min Minutes",
                min_value=0,
                max_value=max_minutes,
                value=0,
                step=1
            )
        else:
            st.info("No minute data available.")
            min_minutes = 0

        age_min, age_max = computed_data.get('age_min', 0), computed_data.get('age_max', 0)
        if age_min > 0 and age_max > 0:
            age_range = st.slider(
                "👤 Age Range",
                min_value=age_min,
                max_value=age_max,
                value=(age_min, age_max)
            )
        else:
            age_range = (0, 100)
    
    # Apply filters
    filtered_rows = feature_filter_rows(
        rows,
        q=search_query,
        teams=selected_teams,
        positions=selected_positions,
        foots=selected_foots,
        age_range=age_range,
        min_minutes=min_minutes
    )
    
    st.info(f"Showing {len(filtered_rows)} of {len(rows)} players")
    
    # Display table
    if filtered_rows:
        # Convert to DataFrame for display
        import pandas as pd
        df = pd.DataFrame(filtered_rows)
        
        # Remove player_id from display
        display_df = df.drop(columns=['player_id'], errors='ignore')
        
        # Display table with selection
        selected_rows = st.dataframe(
            display_df,
            use_container_width=True,
            hide_index=True,
            on_select="rerun",
            selection_mode="single-row"
        )
        
        # Row actions
        if selected_rows.selection.rows:
            selected_idx = selected_rows.selection.rows[0]
            selected_player = filtered_rows[selected_idx]
            player_id = selected_player.get('player_id')
            player_name = selected_player.get('Player')
            team_name = selected_player.get('Team')
            position = selected_player.get('Position')
            minutes = selected_player.get('Minutes', 0)
            appearances = selected_player.get('Appearances', 0)
            goals = selected_player.get('Goals', 0)
            assists = selected_player.get('Assists', 0)
            foot = selected_player.get('Foot', '—')
            age = selected_player.get('Age', '—')
            
            st.subheader(f"Actions for {player_name}")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("📊 View Tactical Profile", type="primary"):
                    # Store player_id in session state for navigation
                    st.session_state['selected_player_id'] = player_id
                    st.session_state['selected_player_name'] = player_name
                    st.session_state['selected_player_team'] = team_name
                    st.session_state['selected_player_position'] = position
            
            with col2:
                if st.button("⚖️ Compare Players", type="secondary"):
                    # Store player 1 data in session state
                    st.session_state['compare_player_1'] = {
                        'player_id': player_id,
                        'player_name': player_name,
                        'team_name': team_name,
                        'position': position,
                        'season': selected_season,
                        'stats': {
                            'minutes': minutes,
                            'appearances': appearances,
                            'goals': goals,
                            'assists': assists,
                            'foot': foot,
                            'age': age
                        }
                    }
                    # Navigate to comparison page
                    st.switch_page("pages/3_Compare_Players.py")
            
            # Show tactical profile if available
            # Show tactical profile if available
            if st.session_state.get('selected_player_id') == player_id:
                st.divider()
            
                # Get tactical profile service
                service = get_service()
                
                # Parse position
                primary_position = position.split(' / ')[0] if position else None
                secondary_position = position.split(' / ')[1] if ' / ' in position else None
                
                # Determine position group
                position_group = service.get_position_group(primary_position, secondary_position)
                
                if position_group:
                    # Extract season ID for role service
                    season_id_map = {
                        "2024/25": 317,
                        "2023/24": 281,
                        "2022/23": 235,
                        "2021/22": 108
                    }
                    season_id = season_id_map.get(selected_season, 317)
                    
                    # Create tabs (Performance Profile only for strikers)
                    if position_group == "striker":
                        tab1, tab2 = st.tabs(["🎯 Tactical Profile", "📊 Performance Profile"])
                    else:
                        tab1, tab2 = st.tabs(["🎯 Tactical Profile", "📊 Info"])
                    
                    with tab1:
                        # Build unified profile (automatically detects position group)
                        profile = service.build_profile(
                            player_id=str(player_id),
                            player_name=player_name,
                            team_name=team_name,
                            primary_position=primary_position,
                            secondary_position=secondary_position,
                            season=selected_season,
                            minutes=minutes,
                            appearances=appearances,
                            goals=goals,
                            assists=assists,
                            foot=foot,
                            age=age
                        )
            
                        # =========================
                        # 📊 BLOCK FOR DEFENDERS
                        # =========================
                        if position_group == "center_back":
                            profile = {
                                "player_name": player_name,
                                "team_name": team_name,
                                "PC1": row["PC1"],
                                "PC2": row["PC2"],
                                "PC3": row["PC3"],
                                "PC4": row["PC4"],
                                "PC5": row["PC5"],
                                "PC6": row["PC6"],
                                "stats": {
                                    "minutes": minutes,
                                    "appearances": appearances,
                                    "goals": goals,
                                    "assists": assists,
                                    "foot": foot,
                                    "age": age
                                }
                            }
                        
                        # Add role data for strikers
                        if position_group == "striker" and profile:
                            role_service = get_role_service()
                            role_data = role_service.get_player_role(player_id, season_id)
                            if role_data:
                                profile['role_data'] = role_data
                        
                        if profile:
                            # Render tactical profile panel (works for both strikers and Deep Progression)
                            render_tactical_profile_panel(profile)
                            
                            # Add info about position group
                            if position_group == "deep_progression":
                                st.caption(
                                    "📝 **Note:** Percentiles relative to Liga MX Deep Progression Unit players (Full-backs & Midfielders), all seasons. "
                                    "Data computed from PCA analysis (7 tactical dimensions)."
                                )
                            elif position_group == "attacking_mid_winger":
                                st.caption(
                                    "📝 **Note:** Percentiles relative to Liga MX Attacking Midfielders & Wingers, all seasons. "
                                    "Data computed from PCA analysis (7 tactical dimensions): Chance Creation, Ball Progression, Width & Crossing, "
                                    "Defensive Work Rate, Finishing Efficiency, Risk & Verticality, Dribbling Threat."
                                )
                        else:
                            st.warning(f"⚠️ No tactical profile data available for {player_name}.")
            
                    with tab2:
                        # Performance profile only for strikers
                        if position_group == "striker":
                            # Get performance profile service with season-specific loader
                            performance_service = get_performance_service()
                            season_id_perf = performance_service._extract_season_id(selected_season)
                            
                            # Re-initialize service with season-specific loader
                            performance_service = get_performance_service(season_id=season_id_perf)
                            
                            # Build performance profile for the selected season
                            performance_profile = performance_service.build_performance_profile(
                                player_id=str(player_id),
                                player_name=player_name,
                                team_name=team_name,
                                primary_position=primary_position,
                                secondary_position=secondary_position,
                                season=selected_season,
                                minutes=minutes
                            )
                            
                            if performance_profile:
                                # Render performance profile panel
                                render_performance_profile_panel(performance_profile)
                            else:
                                st.warning(f"⚠️ No performance profile data available for {player_name}. Player may not have sufficient data for analysis.")
                        else:
                            # Non-striker info tab
                            st.info("📊 Performance Profile is currently only available for strikers.")
                            st.write(f"**{player_name}** plays as **{position}** - part of the Deep Progression Unit.")
                            st.write("View the Tactical Profile tab for detailed analysis of their 7-dimensional ability profile.")
                    
                    # Show similar players in expandable section
                    if position_group in ["striker", "deep_progression", "attacking_mid_winger", "center_back"]:
                        st.markdown("---")
                        
                        # Dynamic title and labels
                        group_labels = {
                            "striker": "Strikers",
                            "deep_progression": "Deep Progression Players",
                            "attacking_mid_winger": "Attacking Midfielders & Wingers",
                            "center_back": "Center Backs"
                        }
                        title = f"⭐ Most Similar {group_labels[position_group]} (all seasons)"
                        
                        with st.expander(title):
                            # Ensure player_id is available
                            if not player_id:
                                st.warning("Player ID not available")
                            else:
                                if position_group == "striker":
                                    # Use role service (includes role column, uses cosine similarity)
                                    player_id_int = int(player_id) if player_id else None
                                    if player_id_int:
                                        similar_players = role_service.get_similar_players(player_id_int, season_id, k=5)
                                    else:
                                        similar_players = []
                                    
                                    if similar_players:
                                        # Table with Role column
                                        table_data = []
                                        season_id_to_display = {317: "24/25", 281: "23/24", 235: "22/23", 108: "21/22"}
                                        
                                        for neighbor in similar_players:
                                            table_data.append({
                                                "Player": neighbor.get("player_name", f"Player {neighbor['player_id']}"),
                                                "Season": season_id_to_display.get(neighbor.get("season_id", 317), ""),
                                                "Role": neighbor.get("role", "Unknown"),
                                                "Similarity": f"{neighbor.get('similarity', 0)}%"
                                            })
                                        
                                        df_similar = pd.DataFrame(table_data)
                                        st.dataframe(df_similar, use_container_width=True, hide_index=True)
                                        st.caption("Similarity based on 6D playing style vectors (cosine similarity).")
                                    else:
                                        st.warning(f"No similar strikers found for {player_name}.")
                                
                                else:
                                    # Use profile service (no role column, uses Euclidean distance)
                                    # Construct player_season_id from player_id and season_id
                                    player_season_id = f"{player_id}_{season_id}"
                                    similar_players = service.get_similar_players(
                                        player_season_id=player_season_id,
                                        position_group=position_group,
                                        k=5
                                    )
                                    
                                    if similar_players:
                                        # Table with Player, Team, Position, Season, Similarity columns
                                        table_data = []
                                        for neighbor in similar_players:
                                            table_data.append({
                                                "Player": neighbor.get("player_name", neighbor.get("player_season_id")),
                                                "Team": neighbor.get("team", "—"),
                                                "Position": neighbor.get("position", "—"),
                                                "Season": neighbor.get("season", ""),
                                                "Similarity": f"{neighbor.get('similarity', 0)}%"
                                            })
                                        
                                        df_similar = pd.DataFrame(table_data)
                                        st.dataframe(
                                            df_similar,
                                            use_container_width=True,
                                            hide_index=True,
                                            column_config={
                                                "Player": st.column_config.TextColumn("Player"),
                                                "Team": st.column_config.TextColumn("Team"),
                                                "Position": st.column_config.TextColumn("Position"),
                                                "Season": st.column_config.TextColumn("Season"),
                                                "Similarity": st.column_config.TextColumn("Similarity")
                                            }
                                        )
                                        
                                        # Center backs have 6 dimensions, others have 7
                                        n_dimensions = 6 if position_group == "center_back" else 7
                                        st.caption(
                                            f"Style similarity based on {n_dimensions}D L2-normalized ability vectors "
                                            f"(Euclidean distance). Span across all seasons in dataset."
                                        )
                                    else:
                                        st.warning(f"No similar players found for {player_name}.")
                else:
                    st.info(f"ℹ️ Tactical profiles are available for Strikers, Deep Progression Unit players (Full-backs & Midfielders), Attacking Midfielders & Wingers, and Center Backs. {player_name} plays as {primary_position}, which is not currently supported.")
    else:
        st.warning("No players match the current filters.")

else:
    st.error("❌ No data available")
    st.info("""
    Possible reasons:
    - The Liga MX endpoint for player stats is not enabled  
    - API credentials are fine, but the dataset is restricted  
    - Network connection issues
    """)

st.markdown("---")
st.caption("*ISAC2025 • Data via StatsBomb API (Hudl)*")