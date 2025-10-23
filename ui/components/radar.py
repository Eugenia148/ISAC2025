"""
Radar Chart Component for Tactical Profiles
Renders radar charts for striker tactical ability visualization.
"""

import streamlit as st
import plotly.graph_objects as go
import plotly.express as px
import numpy as np
from typing import Dict, List, Optional, Any, Literal
from scipy.stats import norm
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
    
    # Get axes from the appropriate loader based on position group
    meta = profile_data.get("meta", {})
    position_group = meta.get("position_group", "striker")
    
    if position_group == "deep_progression":
        from core.profiles.loader import TacticalProfileLoader
        loader = TacticalProfileLoader(artifacts_dir="data/processed/deep_progression_artifacts")
    else:
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
    elif mode == "zscore":
        # Z-score mode (Deep Progression only) - display as percentiles
        values = profile_data.get("ability_scores_zscore", {})
        value_range = (-2.5, 2.5)  # Capped Z-scores for internal use
        title_suffix = "Performance (Percentile Rank)"
        value_format = ".2f"
    elif mode == "l2":
        # L2-normalized mode (Deep Progression only)
        values = profile_data.get("ability_scores_l2", {})
        value_range = (-1, 1)  # L2-normalized vectors
        title_suffix = "Style (L2-normalized)"
        value_format = ".3f"
    else:
        # Default/absolute mode (striker raw scores)
        values = profile_data.get("ability_scores", {})
        # Get axis ranges from the same loader we're using
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
    # Prepare hover text based on mode
    if mode == "zscore":
        # For Z-score mode, show percentiles with Z-score context
        hover_texts = []
        for i, val in enumerate(player_values):
            percentile = norm.cdf(val) * 100
            hover_texts.append(
                f"<b>{axis_labels[i]}</b><br>"
                f"Percentile: {percentile:.1f}%<br>"
                f"(Better than {percentile:.0f}% of players)<br>"
                f"Z-score: {val:+.2f} SD"
            )
        hover_template = '%{text}<extra></extra>'
        
        fig.add_trace(go.Scatterpolar(
            r=player_values,
            theta=axis_labels,
            fill='toself',
            name=profile_data.get("player_name", "Player"),
            line=dict(color='#1f77b4', width=2),
            fillcolor='rgba(31, 119, 180, 0.25)',
            text=hover_texts,
            hovertemplate=hover_template
        ))
    else:
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
    mode: str
) -> None:
    """Render detailed value information below the radar chart."""
    
    if mode == "percentile":
        values = profile_data.get("percentiles", {})
        value_suffix = "%"
    elif mode == "zscore":
        values = profile_data.get("ability_scores_zscore", {})
        value_suffix = " SD"  # Standard deviations
    elif mode == "l2":
        values = profile_data.get("ability_scores_l2", {})
        value_suffix = ""
    else:  # absolute
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
                
                # Color coding based on mode
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
                elif mode == "zscore":
                    # Convert Z-score to percentile for primary display
                    percentile = norm.cdf(value) * 100
                    
                    # Color code based on Z-scores (for consistency)
                    if value >= 1.5:
                        color = "🟢"  # Green for well above average
                    elif value >= 0.5:
                        color = "🟡"  # Yellow for above average
                    elif value >= -0.5:
                        color = "⚪"  # White for average
                    elif value >= -1.5:
                        color = "🟠"  # Orange for below average
                    else:
                        color = "🔴"  # Red for well below average
                    
                    # Display percentile as primary, Z-score as delta
                    st.metric(
                        label=f"{color} {axis.label}",
                        value=f"{percentile:.1f}%",
                        delta=f"{value:+.2f} SD",
                        help=f"{axis.description}\n\n**Percentile:** {percentile:.1f}% (better than {percentile:.0f}% of players)\n**Z-score:** {value:+.2f} standard deviations from mean"
                    )
                else:
                    color = "⚪"  # White circle for absolute/L2 values
                
                if mode != "zscore":
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
    stats = profile_data.get("stats", {})
    
    st.subheader(f"🎯 Tactical Profile — {player_name}")
    
    # Create chips for player info - expanded to show more stats
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
    
    # Add role badge row if role_data is provided
    if profile_data.get("role_data"):
        from ui.components.player_role_header import render_role_badge
        render_role_badge(profile_data.get("role_data"))
    
    # Add a second row for key stats
    if stats:
        col1, col2, col3, col4, col5, col6 = st.columns(6)
        
        with col1:
            st.metric("🎮 **Games**", stats.get("appearances", 0))
        
        with col2:
            st.metric("⏱️ **Minutes**", f"{int(round(stats.get('minutes', 0))):,}")
        
        with col3:
            st.metric("⚽ **Goals**", stats.get("goals", 0))
        
        with col4:
            st.metric("🎯 **Assists**", stats.get("assists", 0))
        
        with col5:
            st.metric("🦶 **Foot**", stats.get("foot", "—"))
        
        with col6:
            st.metric("👤 **Age**", stats.get("age", "—"))


def render_mode_toggle(position_group: str = "striker") -> tuple:
    """Render mode toggle for display options.
    
    Args:
        position_group: "striker" or "deep_progression" to determine available modes
        
    Returns:
        tuple: (mode, show_league_avg) where mode is "percentile", "zscore", or "l2"
    """
    
    st.subheader("⚙️ Display Options")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        if position_group == "deep_progression":
            # Deep Progression: 3 modes (percentile, zscore default, l2)
            mode = st.radio(
                "Display Mode:",
                options=["zscore", "l2", "percentile"],
                format_func=lambda x: {
                    "zscore": "📊 Performance (Percentile Rank)",
                    "l2": "🎨 Style (L2-normalized)",
                    "percentile": "📈 Raw Percentiles"
                }[x],
                index=0,  # Default to zscore
                help="Percentile Rank: performance-based ranking (Z-score normalized) | L2: playing style comparison | Raw Percentiles: direct ranking"
            )
        else:
            # Striker: 2 modes (percentile, absolute)
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
             help="Display league average overlay (only available in some modes)"
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
    
    # Get position group from metadata
    meta = profile_data.get("meta", {})
    position_group = meta.get("position_group", "striker")
    
    # Render header
    render_tactical_profile_header(profile_data)
    
    st.divider()
    
    # Render mode toggle (with position-specific options)
    mode, show_league_avg = render_mode_toggle(position_group=position_group)
    
    # Render radar chart
    render_tactical_profile_radar(
        profile_data,
        mode=mode,
        show_league_average=show_league_avg
    )
    
    # Render footer note (dynamic based on position group and mode)
    if position_group == "deep_progression":
        cohort_label = "Liga MX Deep Progression Unit (Wing Backs, Full Backs, Defensive & Central Midfielders)"
        n_dimensions = 7
        
        if mode == "zscore":
            note = (
                f"📝 **Performance vs League (Percentile Rank):** Percentiles show ranking within cohort. "
                f"50% = average, 84% = one standard deviation above average, 98% = two standard deviations above average. "
                f"**Z-scores shown as delta for statistical context.** Based on {cohort_label} ({n_dimensions}D PCA)."
            )
        elif mode == "l2":
            note = (
                f"📝 **Style Distribution (L2-normalized):** Shows relative distribution of abilities (unit vector). "
                f"Emphasizes playing style shape rather than magnitude. "
                f"Based on {cohort_label} ({n_dimensions}D PCA)."
            )
        else:  # percentile
            note = (
                f"📝 **Percentiles:** Rankings relative to {cohort_label}, 2024/25. "
                f"50% = median, 90% = top 10%. Data from {n_dimensions}D PCA analysis."
            )
    else:
        cohort_label = "Liga MX strikers"
        n_dimensions = 6
        note = (
            f"📝 **Note:** Percentiles relative to {cohort_label}, 2024/25. "
            f"Data computed from PCA analysis ({n_dimensions}D) of tactical metrics."
        )
    
    st.caption(note)
