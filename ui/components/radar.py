"""
Radar Chart Component for Tactical Profiles
Renders radar charts for striker tactical ability visualization.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Optional, Any, Literal
from core.profiles.loader import Axis, get_loader


def render_tactical_profile_radar(
    profile_data: Dict[str, Any],
    mode: Literal["percentile", "absolute"] = "percentile",
    show_league_average: bool = True,
    chart_height: int = 500
) -> None:
    """
    Render a radar chart for a tactical profile.
    
    Args:
        profile_data: Profile payload from TacticalProfileService
        mode: Display mode - "percentile" (0-100) or "absolute" (raw scores)
        show_league_average: Whether to show league average overlay
        chart_height: Height of the chart in pixels
    """
    if not profile_data:
        st.error("No profile data available")
        return
    
    # Get axes from loader
    loader = get_loader()
    axes = loader.get_axes()
    
    if not axes:
        st.error("No ability axes defined")
        return
    
    # Extract data based on mode
    if mode == "percentile":
        values = profile_data.get("percentiles", {})
        value_range = (0, 100)
        title_suffix = "Percentiles"
        value_format = ".0f"
    else:
        values = profile_data.get("ability_scores", {})
        axis_ranges = loader.get_axis_ranges()
        if axis_ranges:
            # Use actual ranges from data
            value_range = (0, 1)  # Default for normalized scores
        else:
            value_range = (0, 1)
        title_suffix = "Raw Scores"
        value_format = ".3f"
    
    if not values:
        st.error(f"No {mode} data available for this player")
        return
    
    # Prepare data for radar chart
    axis_keys = [axis.key for axis in axes]
    axis_labels = [axis.label for axis in axes]
    
    # Get values in the correct order
    player_values = []
    for axis_key in axis_keys:
        value = values.get(axis_key, 0)
        # Ensure value is numeric
        if not isinstance(value, (int, float)):
            value = 0
        player_values.append(value)
    
    # Create radar chart
    fig = go.Figure()
    
    # Player data
    fig.add_trace(go.Scatterpolar(
        r=player_values,
        theta=axis_labels,
        fill='toself',
        name=profile_data.get("player_name", "Player"),
        line=dict(color='#1f77b4', width=2),
        fillcolor='rgba(31, 119, 180, 0.25)'
    ))
    
    # League average overlay (if requested and available)
    # Only show league average for raw scores, not percentiles (where it's always 50%)
    if show_league_average and mode == "absolute":
         league_ref = profile_data.get("league_reference", {})
         if league_ref:
             # Get raw score averages for league reference
             if isinstance(league_ref, dict) and 'raw_score_averages' in league_ref:
                 raw_averages = league_ref['raw_score_averages']
             else:
                 # Fallback to old structure
                 raw_averages = league_ref
             
             league_values = []
             for axis_key in axis_keys:
                 value = raw_averages.get(axis_key, 0.5)  # Default to 0.5 for raw scores
                 # Ensure value is numeric
                 if not isinstance(value, (int, float)):
                     value = 0.5
                 league_values.append(value)
             fig.add_trace(go.Scatterpolar(
                 r=league_values,
                 theta=axis_labels,
                 fill='toself',
                 name="League Average",
                 line=dict(color='#ff7f0e', width=2, dash='dash'),
                 fillcolor='rgba(255, 127, 14, 0.1)'
             ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=value_range,
                tickformat=value_format
            ),
            angularaxis=dict(
                tickfont=dict(size=12)
            )
        ),
        showlegend=True,
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        height=chart_height,
        margin=dict(l=50, r=50, t=50, b=50)
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)
    
    # Display value details
    _render_value_details(profile_data, axes, mode)


def _render_value_details(
    profile_data: Dict[str, Any],
    axes: List[Axis],
    mode: Literal["percentile", "absolute"]
) -> None:
    """Render detailed value information below the radar chart."""
    
    if mode == "percentile":
        values = profile_data.get("percentiles", {})
        value_suffix = "%"
    else:
        values = profile_data.get("ability_scores", {})
        value_suffix = ""
    
    if not values:
        return
    
    st.subheader("📊 Ability Breakdown")
    
    # Create columns for value display
    cols = st.columns(3)
    
    for i, axis in enumerate(axes):
        col_idx = i % 3
        value = values.get(axis.key, 0)
        
        with cols[col_idx]:
            try:
                # Ensure value is numeric
                if not isinstance(value, (int, float)):
                    value = 0
                
                if mode == "percentile":
                    # Color code percentiles
                    if value >= 75:
                        color = "🟢"  # Green for high
                    elif value >= 50:
                        color = "🟡"  # Yellow for medium-high
                    elif value >= 25:
                        color = "🟠"  # Orange for medium-low
                    else:
                        color = "🔴"  # Red for low
                else:
                    color = "⚪"  # White circle for absolute values
                
                st.metric(
                    label=f"{color} {axis.label}",
                    value=f"{value:.1f}{value_suffix}",
                    help=axis.description
                )
            except Exception as e:
                st.metric(
                    label=f"⚪ {axis.label}",
                    value="N/A",
                    help=axis.description
                )


def render_tactical_profile_header(profile_data: Dict[str, Any]) -> None:
    """Render the header section for a tactical profile."""
    
    player_name = profile_data.get("player_name", "Unknown Player")
    team_name = profile_data.get("team_name", "Unknown Team")
    position = profile_data.get("position", "Striker")
    season = profile_data.get("season", "2024/25")
    
    st.subheader(f"🎯 Tactical Profile — {player_name}")
    
    # Create chips for player info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info(f"🏟️ **Team:** {team_name}")
    
    with col2:
        st.info(f"⚽ **Position:** {position}")
    
    with col3:
        st.info(f"📅 **Season:** {season}")
    
    with col4:
        # Calculate average percentile if available
        percentiles = profile_data.get("percentiles", {})
        if percentiles:
            try:
                # Ensure all values are numeric
                numeric_percentiles = [v for v in percentiles.values() if isinstance(v, (int, float))]
                if numeric_percentiles:
                    avg_percentile = sum(numeric_percentiles) / len(numeric_percentiles)
                    st.info(f"📈 **Avg Percentile:** {avg_percentile:.0f}%")
                else:
                    st.info("📈 **Avg Percentile:** N/A")
            except Exception as e:
                st.info("📈 **Avg Percentile:** N/A")


def render_mode_toggle() -> Literal["percentile", "absolute"]:
    """Render mode toggle for percentile vs absolute display."""
    
    st.subheader("⚙️ Display Options")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        mode = st.radio(
            "Display Mode:",
            options=["percentile", "absolute"],
            format_func=lambda x: "📊 Percentiles (0-100)" if x == "percentile" else "📈 Raw Scores",
            index=0
        )
    
    with col2:
         show_league_avg = st.checkbox(
             "Show League Average",
             value=True,
             help="Display league average overlay (only available in raw scores mode)"
         )
    
    return mode, show_league_avg


def render_tactical_profile_panel(profile_data: Dict[str, Any]) -> None:
    """
    Render a complete tactical profile panel with header, controls, and radar chart.
    
    Args:
        profile_data: Profile payload from TacticalProfileService
    """
    if not profile_data:
        st.error("No profile data available")
        return
    
    # Render header
    render_tactical_profile_header(profile_data)
    
    st.divider()
    
    # Render mode toggle
    mode, show_league_avg = render_mode_toggle()
    
    # Render radar chart
    render_tactical_profile_radar(
        profile_data,
        mode=mode,
        show_league_average=show_league_avg
    )
    
    # Render footer note
    st.caption(
        "📝 **Note:** Percentiles relative to Liga MX strikers, 2024/25. "
        "Data computed from PCA analysis of tactical metrics."
    )
