"""
Scatter Plots Page - Interactive Player Discovery
Discover unique combinations of player skillsets.
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api.client import client
import io
import base64

# --- UI label mapping (display name shown to users) ---
DISPLAY_NAME_MAP = {
    "passes_completed": "Passes Completed",
    "progressive_passes": "Progressive Passes",
    "dribbles_succeeded": "Successful Dribbles",
    "duels_won": "Duels Won",
    "ball_recoveries": "Ball Recoveries",
    "carries": "Carries",
    "carry_length": "Carry Distance",
    "carry_success_pct": "Carry Success %",
    "challenge_ratio": "Challenges Won %",
    "clearances": "Clearances",
    "conversion_pct": "Shot Conversion %",
    "deep_completions": "Deep Completions",
    "obv_total": "OBV (Total Contribution)",
    "aggressive_actions": "Aggressive Actions",
    "backward_pass_ratio": "Backward Pass Ratio",
    "forward_pass_ratio": "Forward Pass Ratio",
    "box_cross_ratio": "Crosses into Box %",
    "change_in_passing_ratio": "Change in Pass Direction %",
    "counterpressure_regains": "Counterpress Recoveries",
    "op_assists": "Open-Play Assists",
    "sp_assists": "Set-Piece Assists",
    "sp_key_passes": "Set-Piece Key Passes",
    "sp_passes_into_box": "Set-Piece Passes into Box",
    "sp_xa": "Set-Piece xA",
    "through_balls": "Through Balls",
    "touches_in_box": "Touches in Box",
    "unpressured_long_balls": "Unpressured Long Balls",
    "shot_on_target_ratio": "Shots on Target %",
    "shot_touch_ratio": "Shots per Touch",
    "save_ratio": "Save %",
    "obv_pass": "OBV (Passing)",
    "obv_shot": "OBV (Shooting)",
    # per90 variants
    "goals_per90": "Goals per 90",
    "assists_per90": "Assists per 90",
    "shots_per90": "Shots per 90",
    "xG_per90": "xG per 90",
    "xA_per90": "xA per 90",
    "passes_completed_per90": "Passes Completed per 90",
    "progressive_passes_per90": "Progressive Passes per 90",
    "dribbles_succeeded_per90": "Dribbles per 90",
    "duels_won_per90": "Duels Won per 90",
}

# Build reverse map for lookups when the user selects a display label
KEY_BY_DISPLAY = {v: k for k, v in DISPLAY_NAME_MAP.items()}

def to_display_name(key: str) -> str:
    # default to the key itself if not present in mapping
    return DISPLAY_NAME_MAP.get(key, key)

def to_key(display: str) -> str:
    # default to the display itself if not present (when display==key)
    return KEY_BY_DISPLAY.get(display, display)

# Page configuration
st.set_page_config(
    page_title="Scatter Plots - Player Analysis",
    page_icon="📊",
    layout="wide"
)


# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====
def feature_fetch_player_data(api_client, *, competition_id: int, season_id: int):
    """
    Fetch player season statistics and build a comprehensive dataset.
    
    Returns:
        DataFrame | None: Player data with all metrics and per90 calculations
    """
    try:
        # Fetch player season stats
        season_stats = api_client.player_season_stats(
            competition_id=competition_id,
            season_id=season_id
        )
        
        # Fetch player mapping data for additional info
        mapping = api_client.player_mapping(
            competition_id=competition_id,
            season_id=season_id
        )
        
        if season_stats is None or len(season_stats) == 0:
            print("⚠️ No player data found — trying team data as fallback.")
            season_stats = api_client.team_season_stats(
                competition_id=competition_id,
                season_id=season_id
            )
            if season_stats is None:
                return None
        
        # Convert to DataFrame
        df = pd.DataFrame(season_stats)
        
        if len(df) == 0:
            return None
        
        # Fix stat name mapping based on StatsBomb API v4.0.0/v5.0.0
        df.rename(columns={
            "player_season_np_shots_90": "shots",
            "player_season_np_xg_90": "xG",
            "player_season_op_passes_90": "passes_completed",
            "player_season_deep_progressions_90": "progressive_passes",
            "player_season_aerial_wins_90": "duels_won"
        }, inplace=True)
        
        # Map API fields → friendly aliases for new Season v4 stats
        RENAME_MAP = {
            # New, safe Season v4 stats (do not overlap with existing UI)
            "player_season_aerial_wins_90": "aerial_wins",
            "player_season_ball_recoveries_90": "ball_recoveries",
            "player_season_carries_90": "carries",
            "player_season_carry_length": "carry_length",
            "player_season_carry_ratio": "carry_success_pct",
            "player_season_challenge_ratio": "challenge_ratio",
            "player_season_clearance_90": "clearances",
            "player_season_conversion_ratio": "conversion_pct",
            "player_season_deep_completions_90": "deep_completions",
            "player_season_obv_90": "obv_total",
        }
        
        # Add additional 20 Season v4 stats
        RENAME_MAP.update({
            "player_season_aggressive_actions_90": "aggressive_actions",
            "player_season_backward_pass_proportion": "backward_pass_ratio",
            "player_season_blocks_per_shot": "blocks_per_shot",
            "player_season_box_cross_ratio": "box_cross_ratio",
            "player_season_change_in_passing_ratio": "change_in_passing_ratio",
            "player_season_counterpressure_regains_90": "counterpressure_regains",
            "player_season_op_assists_90": "op_assists",
            "player_season_sp_assists_90": "sp_assists",
            "player_season_sp_key_passes_90": "sp_key_passes",
            "player_season_sp_passes_into_box_90": "sp_passes_into_box",
            "player_season_sp_xa_90": "sp_xa",
            "player_season_through_balls_90": "through_balls",
            "player_season_touches_inside_box_90": "touches_in_box",
            "player_season_turnovers_90": "turnovers",
            "player_season_unpressured_long_balls_90": "unpressured_long_balls",
            "player_season_red_cards_90": "red_cards",
            "player_season_second_yellow_cards_90": "second_yellows",
            "player_season_shot_on_target_ratio": "shot_on_target_ratio",
            "player_season_shot_touch_ratio": "shot_touch_ratio",
            "player_season_save_ratio": "save_ratio",
        })
        
        # Add pass direction ratio metrics
        RENAME_MAP.update({
            "player_season_forward_pass_proportion": "forward_pass_ratio",
            "player_season_lateral_pass_proportion": "lateral_pass_ratio",
        })
        
        # Add OBV component metrics
        RENAME_MAP.update({
            "player_season_obv_pass_90": "obv_pass",
            "player_season_obv_carry_90": "obv_carry",
            "player_season_obv_shot_90": "obv_shot",
            "player_season_obv_defense_90": "obv_defense",
            "player_season_obv_duel_90": "obv_duel",
            "player_season_obv_set_play_90": "obv_setplay",
            "player_season_obv_dribble_90": "obv_dribble",
            "player_season_obv_cross_90": "obv_cross",
            "player_season_obv_reception_90": "obv_reception",
            "player_season_obv_turnover_90": "obv_turnover",
        })
        
        # Apply rename only for keys that exist in df
        df.rename(columns={k: v for k, v in RENAME_MAP.items() if k in df.columns}, inplace=True)
        
        # Check if this is player-level data
        if "player_name" not in df.columns:
            # Team-level fallback - create basic structure
            df['player_name'] = df.get('team_name', 'Unknown Team')
            df['player_id'] = df.get('team_id', 0)
            df['primary_position'] = 'Team'
        
        # Ensure we have the required columns with defaults
        required_columns = {
            'player_id': 0,
            'player_name': 'Unknown',
            'team_name': 'Unknown',
            'primary_position': 'Unknown',
            'player_season_minutes': 0,
            'player_season_goals_90': 0,
            'player_season_assists_90': 0,
            'player_season_xa_90': 0,
            'player_season_dribbles_90': 0,
            # Add the corrected field names
            'shots': 0,
            'xG': 0,
            'passes_completed': 0,
            'progressive_passes': 0,
            'duels_won': 0
        }
        
        for col, default_val in required_columns.items():
            if col not in df.columns:
                df[col] = default_val
        
        # Calculate total metrics from per90 stats
        minutes = df['player_season_minutes']
        df['goals'] = (df['player_season_goals_90'] * minutes / 90).round(2)
        df['assists'] = (df['player_season_assists_90'] * minutes / 90).round(2)
        df['xA'] = (df['player_season_xa_90'] * minutes / 90).round(2)
        df['dribbles_succeeded'] = (df['player_season_dribbles_90'] * minutes / 90).round(2)
        
        # For the corrected fields, calculate totals from per90 values
        if 'shots' in df.columns:
            df['shots'] = (df['shots'] * minutes / 90).round(2)
        if 'xG' in df.columns:
            df['xG'] = (df['xG'] * minutes / 90).round(2)
        if 'passes_completed' in df.columns:
            df['passes_completed'] = (df['passes_completed'] * minutes / 90).round(2)
        if 'progressive_passes' in df.columns:
            df['progressive_passes'] = (df['progressive_passes'] * minutes / 90).round(2)
        if 'duels_won' in df.columns:
            df['duels_won'] = (df['duels_won'] * minutes / 90).round(2)
        
        # Create per90 metrics for applicable columns (exclude new Season v4 metrics as they're already per90)
        per90_metrics = ['goals', 'assists', 'shots', 'xG', 'xA', 'passes_completed', 
                         'progressive_passes', 'dribbles_succeeded', 'duels_won']
        
        for metric in per90_metrics:
            if metric in df.columns:
                # Calculate per90 from total values
                df[f"{metric}_per90"] = (90 * df[metric] / minutes).round(2)
                # Handle division by zero
                df[f"{metric}_per90"] = df[f"{metric}_per90"].fillna(0)
        
        # Rename columns for consistency
        df = df.rename(columns={
            'player_season_minutes': 'minutes_played',
            'primary_position': 'position'
        })
        
        # Filter out players with no minutes
        df = df[df['minutes_played'] > 0].copy()
        
        return df
        
    except Exception as e:
        print(f"Failed to fetch player data: {e}")
        return None


def feature_get_available_metrics(df):
    """
    Get list of available metrics for dropdowns, excluding non-numeric columns.
    
    Returns:
        dict: Available metrics organized by category
    """
    if df is None or len(df) == 0:
        return {'basic': [], 'per90': []}
    
    # Define metric categories
    BASE_METRICS = ['goals', 'assists', 'shots', 'xG', 'xA', 'passes_completed', 
                    'progressive_passes', 'dribbles_succeeded', 'duels_won', 'minutes_played']
    
    # New Season v4 metrics
    NEW_METRICS = [
        "aerial_wins",
        "ball_recoveries",
        "carries",
        "carry_length",
        "carry_success_pct",
        "challenge_ratio",
        "clearances",
        "conversion_pct",
        "deep_completions",
        "obv_total",
        # Additional 20 Season v4 stats
        "aggressive_actions",
        "backward_pass_ratio",
        "blocks_per_shot",
        "box_cross_ratio",
        "change_in_passing_ratio",
        "counterpressure_regains",
        "op_assists",
        "sp_assists",
        "sp_key_passes",
        "sp_passes_into_box",
        "sp_xa",
        "through_balls",
        "touches_in_box",
        "turnovers",
        "unpressured_long_balls",
        "red_cards",
        "second_yellows",
        "shot_on_target_ratio",
        "shot_touch_ratio",
        "save_ratio",
        # Pass direction ratio metrics
        "forward_pass_ratio",
        "lateral_pass_ratio",
        # OBV component metrics
        "obv_pass",
        "obv_carry",
        "obv_shot",
        "obv_defense",
        "obv_duel",
        "obv_setplay",
        "obv_dribble",
        "obv_cross",
        "obv_reception",
        "obv_turnover",
    ]
    
    # Combine all candidates
    ALL_CANDIDATES = BASE_METRICS + NEW_METRICS
    
    # Filter to only include metrics that exist in the dataframe
    available_metrics = [m for m in ALL_CANDIDATES if m in df.columns]
    
    per90_metrics = [col for col in df.columns if col.endswith('_per90')]
    available_per90 = [col for col in per90_metrics if col in df.columns]
    
    return {
        'basic': available_metrics,
        'per90': available_per90,
        'all': available_metrics + available_per90
    }


def feature_filter_data(df, positions, min_minutes):
    """
    Filter the dataset based on user selections.
    
    Returns:
        DataFrame: Filtered dataset
    """
    if df is None or len(df) == 0:
        return df
    
    filtered_df = df.copy()
    
    # Position filter
    if positions and 'position' in filtered_df.columns:
        filtered_df = filtered_df[filtered_df['position'].isin(positions)]
    
    # Minutes filter
    if min_minutes > 0:
        filtered_df = filtered_df[filtered_df['minutes_played'] >= min_minutes]
    
    return filtered_df


def feature_create_scatter_plot(df, x_var, y_var, color_var, colorscale, show_labels):
    """
    Create interactive scatter plot using Plotly.
    
    Returns:
        plotly.graph_objects.Figure: Interactive scatter plot
    """
    if df is None or len(df) == 0:
        return None
    
    # Validate variables exist in dataframe
    if x_var not in df.columns or y_var not in df.columns or color_var not in df.columns:
        return None
    
    # Create the scatter plot
    fig = px.scatter(
        df,
        x=x_var,
        y=y_var,
        color=color_var,
        color_continuous_scale=colorscale,
        hover_name="player_name",
        hover_data={
            "team_name": True,
            "minutes_played": True,
            "goals": True,
            "shots": True,
            "xA": True,
            "position": True
        },
        height=700,
        title=f"{to_display_name(y_var)} vs {to_display_name(x_var)} (colored by {to_display_name(color_var)})",
        labels={
            x_var: to_display_name(x_var), 
            y_var: to_display_name(y_var), 
            color_var: to_display_name(color_var)
        }
    )
    
    # Add median reference lines
    x_median = df[x_var].median()
    y_median = df[y_var].median()
    
    fig.add_vline(x=x_median, line_dash="dash", line_color="red", 
                  annotation_text=f"Median {to_display_name(x_var)}: {x_median:.2f}")
    fig.add_hline(y=y_median, line_dash="dash", line_color="red", 
                  annotation_text=f"Median {to_display_name(y_var)}: {y_median:.2f}")
    
    # Add player labels if requested
    if show_labels:
        fig.update_traces(
            text=df['player_name'],
            textposition='top center',
            mode='markers+text'
        )
    
    # Update layout
    fig.update_layout(
        xaxis_title=x_var,
        yaxis_title=y_var,
        showlegend=True,
        hovermode='closest'
    )
    
    return fig


# ===== UI (STREAMLIT BELOW) =====
st.title("📊 Scatter Plots - Player Analysis")
st.markdown("Interactive scatter plots of players using real data from Hudl/StatsBomb API")

# Season selection
st.markdown("---")
st.subheader("⚙️ Settings")

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
cache_key = f"scatter_data_{competition_id}_{season_id}"

# Fetch data if not cached or refresh requested
if cache_key not in st.session_state or refresh_clicked:
    with st.spinner("Loading player data from StatsBomb API..."):
        raw_data = feature_fetch_player_data(client, competition_id=competition_id, season_id=season_id)
        if raw_data is not None:
            st.session_state[cache_key] = raw_data
        else:
            st.session_state[cache_key] = None

# Get cached data
player_data = st.session_state.get(cache_key)

# Display results
if player_data is not None and len(player_data) > 0:
    st.success(f"✅ Loaded {len(player_data)} players")
    
    # Get available metrics
    available_metrics = feature_get_available_metrics(player_data)
    
    # Plot controls
    st.markdown("---")
    st.subheader("📈 Plot Configuration")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Position filter
        positions = []
        if 'position' in player_data.columns:
            unique_positions = player_data['position'].unique()
            positions = st.multiselect(
                "⚽ Positions",
                options=unique_positions,
                default=unique_positions.tolist() if len(unique_positions) <= 4 else []
            )
        
        # X-axis variable
        available_metrics_list = available_metrics['all']
        display_options = [to_display_name(k) for k in available_metrics_list]
        display_options = sorted(display_options)  # nice UI ordering
        
        default_x_key = 'xA'
        default_y_key = 'duels_won'
        default_color_key = 'minutes_played'
        
        x_display = st.selectbox(
            "X-axis Variable",
            options=display_options,
            index=display_options.index(to_display_name(default_x_key)) if to_display_name(default_x_key) in display_options else 0
        )
    
    with col2:
        # Y-axis variable
        y_display = st.selectbox(
            "Y-axis Variable",
            options=display_options,
            index=display_options.index(to_display_name(default_y_key)) if to_display_name(default_y_key) in display_options else 1
        )
        
        # Color variable
        color_display = st.selectbox(
            "Color Variable",
            options=display_options,
            index=display_options.index(to_display_name(default_color_key)) if to_display_name(default_color_key) in display_options else 2
        )
        
        # Map selected display labels back to internal metric keys
        x_var = to_key(x_display)
        y_var = to_key(y_display)
        color_var = to_key(color_display)
    
    with col3:
        # Colorscale
        colorscale = st.selectbox(
            "Colorscale",
            options=['RdYlGn', 'Viridis', 'Blues', 'Plasma'],
            index=0
        )
        
        # Minimum minutes
        max_minutes = int(player_data['minutes_played'].max()) if 'minutes_played' in player_data.columns else 0
        min_minutes = st.slider(
            "Minimum Minutes",
            min_value=0,
            max_value=max_minutes,
            value=900,
            step=50
        )
    
    # Show labels option
    show_labels = st.checkbox("Show Player Labels", value=False)
    
    # Update plot button
    update_plot = st.button("📊 Update Plot", type="primary")
    
    if update_plot:
        # Filter data
        filtered_data = feature_filter_data(player_data, positions, min_minutes)
        
        if len(filtered_data) == 0:
            st.warning("No players match your filters. Try reducing the minimum minutes or selecting more positions.")
        else:
            st.info(f"Showing {len(filtered_data)} players")
            
            # Check if selected metrics exist in the dataframe
            missing = [c for c in [x_var, y_var, color_var] if c not in filtered_data.columns]
            if missing:
                st.warning(f"Selected metric(s) not available in data: {', '.join(missing)}")
            else:
                # Create scatter plot
                fig = feature_create_scatter_plot(
                    filtered_data, x_var, y_var, color_var, colorscale, show_labels
                )
            
            if fig:
                st.plotly_chart(fig, width="stretch")
                
                # Table and downloads section
                st.markdown("---")
                st.subheader("📋 Player Data")
                
                # Display table
                display_df = filtered_data[['player_name', 'team_name', 'position', 'minutes_played', 
                                          'goals', 'shots', 'xA', 'duels_won']].copy()
                st.dataframe(display_df, use_container_width=True, hide_index=True)
                
                # Download buttons
                col1, col2 = st.columns(2)
                
                with col1:
                    # CSV download
                    csv = filtered_data.to_csv(index=False)
                    st.download_button(
                        label="📥 Download CSV",
                        data=csv,
                        file_name=f"player_data_{selected_season.replace('/', '_')}.csv",
                        mime="text/csv"
                    )
                
                with col2:
                    # PNG download
                    try:
                        # Try to export as PNG using kaleido
                        img_bytes = fig.to_image(format="png", width=1200, height=700)
                        st.download_button(
                            label="📥 Download PNG",
                            data=img_bytes,
                            file_name=f"scatter_plot_{selected_season.replace('/', '_')}.png",
                            mime="image/png"
                        )
                    except Exception as e:
                        st.info("💡 Use the camera icon in the plot toolbar to download as PNG")
                        st.code(f"Kaleido error: {str(e)}")

else:
    # No data available
    st.error("❌ **No data available**")
    st.info("""
    No player data found for the selected parameters.
    
    This could mean:
    - API credentials issue
    - Data not available for this season
    - Network connection problem
    - Invalid parameters
    """)

# Footer
st.markdown("---")
st.caption("*Data from StatsBomb API (Hudl) • Use sidebar to navigate*")
