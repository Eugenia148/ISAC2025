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
                    # Store player_id in session state for navigation
                    st.session_state['compare_player_id'] = player_id
                    st.session_state['compare_player_name'] = player_name
                    st.info("🚧 Player Compare page coming soon! Player ID stored in session state.")
            
            # Show tactical profile if available
            # Show tactical profile if available
            if st.session_state.get('selected_player_id') == player_id:
                st.divider()
            
                # Get tactical profile service
                service = get_service()
            
                # Parse position
                primary_position = position.split(' / ')[0] if position else None
                secondary_position = position.split(' / ')[1] if ' / ' in position else None
            
                # ===== Detectar tipo de jugador manualmente =====
                striker_positions = {
                    "Centre Forward", "Left Centre Forward", "Right Centre Forward"
                }
                defender_positions = {
                    "Centre Back", "Left Centre Back", "Right Centre Back"
                }
            
                if primary_position in striker_positions or secondary_position in striker_positions:
                    position_group = "striker"
                elif primary_position in defender_positions or secondary_position in defender_positions:
                    position_group = "defender"
                else:
                    position_group = None
            
                # ====== STRIKERS (ya existente, no tocar) ======
                if position_group == "striker":
                    # Extract season ID for role service
                    season_id_map = {
                        "2024/25": 317,
                        "2023/24": 281,
                        "2022/23": 235,
                        "2021/22": 108
                    }
                    season_id = season_id_map.get(selected_season, 317)
            
                    tab1, tab2 = st.tabs(["🎯 Tactical Profile", "📊 Performance Profile"])
            
                    with tab1:
                        role_service = get_role_service()
                        role_data = role_service.get_player_role(player_id, season_id)
            
                        profile = service.build_striker_profile(
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
                        
                            # Draw the radar chart for defenders
                            render_tactical_profile_panel(profile)
                        
                            # Add interpretation text below
                            st.markdown("---")
                            st.markdown("### 📘 Interpretation of Principal Components (PCs)")
                        
                            st.markdown("""
                            - ⚙️ **PC1 – Build-Up & Ball Progression**  
                              Represents the involvement of the center-back in buildup play and ball progression.  
                              High values = comfort in possession, passing participation, and offensive contribution.
                        
                            - 🛡️ **PC2 – Defensive Interventions & Aggressiveness**  
                              Captures defensive activity and aggressiveness in duels and anticipation.
                        
                            - 🪂 **PC3 – Defensive Duels & Aerial Engagement**  
                              Measures duel intensity and aerial strength. High values = 1v1 dominance and aerial defense.
                        
                            - 🧱 **PC4 – Defensive Solidity & Clearances**  
                              Reflects reactive defensive style. High values = frequent clearances and blocks.
                        
                            - 📈 **PC5 – Distribution Style & Direction**  
                              Indicates type and direction of passes from the back. Differentiates safe vs. vertical distributors.
                        
                            - 🧍 **PC6 – Defensive Coverage & Risk Management**  
                              Evaluates the balance between defensive security and offensive involvement.
                              High values = solid coverage and low-risk play.
                            """)

                        if profile and role_data:
                            profile['role_data'] = role_data
            
                        if profile:
                            render_tactical_profile_panel(profile)
                        else:
                            st.warning(f"⚠️ No tactical profile data available for {player_name}.")
            
                    with tab2:
                        performance_service = get_performance_service()
                        season_id_perf = performance_service._extract_season_id(selected_season)
                        performance_service = get_performance_service(season_id=season_id_perf)
            
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
                            render_performance_profile_panel(performance_profile)
                        else:
                            st.warning(f"⚠️ No performance profile data available for {player_name}.")
            
                    st.markdown("---")
                    with st.expander("⭐ Most Similar Strikers (all seasons)"):
                        player_id_int = int(player_id) if player_id else None
                        if player_id_int:
                            similar_players = role_service.get_similar_players(player_id_int, season_id, k=5)
                        else:
                            similar_players = []
            
                        if similar_players:
                            season_id_to_display = {317: "24/25", 281: "23/24", 235: "22/23", 108: "21/22"}
                            table_data = []
                            for neighbor in similar_players:
                                neighbor_name = neighbor.get("player_name", f"Player {neighbor['player_id']}")
                                neighbor_role = neighbor.get("role", "Unknown")
                                neighbor_season_id = neighbor.get("season_id", 317)
                                neighbor_season = season_id_to_display.get(neighbor_season_id, str(neighbor_season_id))
                                similarity = neighbor.get("similarity", 0)
                                table_data.append({
                                    "Player": neighbor_name,
                                    "Season": neighbor_season,
                                    "Role": neighbor_role,
                                    "Similarity": f"{similarity*100:.0f}%"
                                })
                            import pandas as pd
                            df_similar = pd.DataFrame(table_data)
                            st.dataframe(df_similar, use_container_width=True, hide_index=True)
                            st.caption("Similarity scores are cosine similarity (0-100%) on 6D playing style vectors.")
                        else:
                            st.warning(f"No similar strikers found for {player_name}.")
            
                # ====== DEFENDERS (new block) ======
                elif position_group == "defender":
                    tab1, tab2 = st.tabs(["🛡️ Tactical Profile", "📊 Info"])

                    with tab1:
                        import pandas as pd
                        import plotly.graph_objects as go
                        from pathlib import Path
                
                        # === Load defender profile data ===
                        csv_path = Path(__file__).resolve().parents[1] / "core" / "data" / "defenders_profiles.csv"
                        if not csv_path.exists():
                            st.warning("⚠️ defenders_profiles.csv not found. Generate the file from the defenders notebook.")
                        else:
                            df = pd.read_csv(csv_path)
                            match = df.loc[df["player_name"].str.lower() == player_name.lower()]
                
                            if match.empty:
                                st.warning(f"⚠️ {player_name} not found in defenders_profiles.csv.")
                            else:
                                row = match.iloc[0]
                
                            # Build standardized profile for layout
                                profile = {
                                    "player_name": player_name,
                                    "team_name": team_name,
                                    "position": "Centre Back",
                                    "season": selected_season,
                                    "stats": {
                                        "minutes": minutes,
                                        "appearances": appearances,
                                        "goals": goals,
                                        "assists": assists,
                                        "foot": foot,
                                        "age": age
                                    }
                                }
                
                            # === Render same layout cards (Team, Position, Stats...) ===
                                render_tactical_profile_panel(profile)
                
                            # === Defensive radar (PC1–PC6) ===
                                pc_values = [
                                    float(row["PC1"]),
                                    float(row["PC2"]),
                                    float(row["PC3"]),
                                    float(row["PC4"]),
                                    float(row["PC5"]),
                                    float(row["PC6"])
                                ]
                                pc_labels = ["PC1", "PC2", "PC3", "PC4", "PC5", "PC6"]
                
                            # Close loop
                                pc_values += [pc_values[0]]
                                pc_labels += [pc_labels[0]]
                    
                                fig = go.Figure()
                                fig.add_trace(go.Scatterpolar(
                                    r=pc_values,
                                    theta=pc_labels,
                                    fill="toself",
                                    name=player_name,
                                    line_color="#1f77b4",
                                    fillcolor="rgba(31, 119, 180, 0.3)"
                                ))
                    
                                fig.update_layout(
                                    polar=dict(
                                        radialaxis=dict(visible=True, range=[0, 1], gridcolor="gray", gridwidth=0.5),
                                        angularaxis=dict(tickfont=dict(size=12))
                                    ),
                                    showlegend=True,
                                    template="plotly_dark",
                                    width=600,
                                    height=600,
                                    margin=dict(l=40, r=40, t=40, b=40)
                                )
                    
                                st.markdown(f"### 🛡️ Defensive Style — {player_name} (PC1–PC6)")
                                st.plotly_chart(fig, use_container_width=True)
                    
                                # === Interpretation text ===
                                st.markdown("---")
                                st.markdown("### 📘 Interpretation of Principal Components (PCs)")
                                st.markdown("""
**⚙️ PC1 – Build-Up & Ball Progression**  
Represents the center-back’s involvement in buildup play and ball progression.  
High values = comfort in possession, active participation in passing sequences, and offensive contribution.  

**🛡️ PC2 – Defensive Interventions & Aggressiveness**  
Captures defensive activity and aggressiveness.  
High values = proactive defenders who intercept passes and win duels.  

**🪂 PC3 – Defensive Duels & Aerial Engagement**  
Measures duel intensity, especially in aerial challenges.  
High values = dominant center-backs in 1v1 and aerial play.  

**🧱 PC4 – Defensive Solidity & Clearances**  
Reflects a reactive, safety-first defensive style prioritizing clearances and blocks.  
High values = low-block or safety-oriented defenders.  

**📈 PC5 – Distribution Style & Direction**  
Describes the type and direction of passing.  
Differentiates between safe lateral passers and vertical distributors.  

**🧍 PC6 – Defensive Coverage & Risk Management**  
Represents the balance between defensive security and ball progression.  
High values = solid defensive coverage and low-risk decision-making.
            """)


                    with tab2:
                        st.info("📊 Performance Profile only available for strikers.")
                        st.write(f"**{player_name}** plays as **{position}** – Defensive Unit.")

                else:
                    st.info(f"ℹ️ Tactical profiles are currently only available for Strikers and Center Backs. {player_name} plays as {primary_position}.")


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