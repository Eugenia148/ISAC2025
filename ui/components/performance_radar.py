"""
Performance radar chart component for striker performance analysis.

This module renders a polygon radar chart showing striker performance metrics
across all individual metrics from the performance axes.
"""

import streamlit as st
import plotly.graph_objects as go
import numpy as np
from typing import Dict, List, Any, Optional


def render_performance_profile_header(profile_data: Dict[str, Any]) -> None:
    """Render the header section for a performance profile."""
    
    player_info = profile_data.get("player", {})
    player_name = player_info.get("name", "Unknown Player")
    team_name = player_info.get("team", "Unknown Team")
    season = profile_data.get("season", "2024/25")
    minutes = player_info.get("minutes", 0)
    minutes_threshold = profile_data.get("minutes_threshold", 600)
    
    st.subheader(f"📊 Performance Profile — {player_name}")
    
    # Create chips for player info
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.info(f"🏟️ **Team:** {team_name}")
    
    with col2:
        st.info(f"📅 **Season:** {season}")
    
    with col3:
        st.info(f"⏱️ **Minutes:** {int(round(minutes)):,}")
    
    with col4:
        # Calculate average percentile if available
        axes = profile_data.get("axes", [])
        if axes:
            try:
                all_percentiles = []
                for axis in axes:
                    metrics = axis.get('metrics', [])
                    for metric in metrics:
                        pct = metric.get('percentile')
                        if pct is not None and isinstance(pct, (int, float)):
                            all_percentiles.append(pct)
                
                if all_percentiles:
                    avg_percentile = sum(all_percentiles) / len(all_percentiles)
                    st.info(f"📈 **Avg Percentile:** {avg_percentile:.0f}%")
                else:
                    st.info("📈 **Avg Percentile:** N/A")
            except Exception as e:
                st.info("📈 **Avg Percentile:** N/A")
    
    # Show minutes warning if below threshold
    if minutes < minutes_threshold:
        st.warning(f"⚠️ Low minutes ({int(round(minutes)):,}); percentiles may be noisy (threshold: {minutes_threshold:,})")


def render_performance_mode_toggle() -> str:
    """Render toggle for switching between percentile and absolute modes."""
    col1, col2 = st.columns([1, 3])
    
    with col1:
        mode = st.radio(
            "View Mode:",
            ["percentile", "absolute"],
            format_func=lambda x: "Percentiles" if x == "percentile" else "Raw Values",
            horizontal=True
        )
    
    with col2:
        if mode == "percentile":
            st.caption("📊 Percentiles relative to Liga MX strikers (0-100)")
        else:
            st.caption("📈 Raw values (normalized to 0-1 range)")
    
    return mode


def render_performance_radar(
    profile_data: Dict[str, Any],
    mode: str = "percentile"
) -> None:
    """Render the performance radar as a polygon chart with individual metrics."""
    
    axes = profile_data.get("axes", [])
    if not axes:
        st.warning("No performance data available.")
        return
    
    # Collect all metrics across all axes
    all_metrics = []
    all_percentiles = []
    all_raw_values = []
    
    for axis in axes:
        metrics = axis.get('metrics', [])
        for metric in metrics:
            label = metric.get('label', 'Unknown')
            percentile = metric.get('percentile')
            raw = metric.get('raw')
            
            all_metrics.append(label)
            all_percentiles.append(percentile if percentile is not None else 0)
            all_raw_values.append(raw if raw is not None else 0)
    
    # Create radar chart
    fig = go.Figure()
    
    # Use percentiles or raw values based on mode
    if mode == "percentile":
        values = all_percentiles
        max_value = 100
    else:
        # Normalize raw values to 0-100 scale for better visualization
        if max(all_raw_values) > 0:
            max_value = max(all_raw_values) * 1.2  # Add 20% padding
            values = [v / max_value * 100 if max_value > 0 else 0 for v in all_raw_values]
        else:
            max_value = 100
            values = all_raw_values
    
    # Add player performance trace
    fig.add_trace(go.Scatterpolar(
        r=values,
        theta=all_metrics,
        fill='toself',
        name='Player',
        line=dict(color='rgb(32, 201, 151)', width=2),
        fillcolor='rgba(32, 201, 151, 0.3)',
        hovertemplate='<b>%{theta}</b><br>Percentile: %{r:.1f}%<extra></extra>'
    ))
    
    # Update layout
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100] if mode == "percentile" else [0, max(values) * 1.1],
                tickmode='array',
                tickvals=[20, 40, 60, 80, 100] if mode == "percentile" else None,
                ticktext=['20%', '40%', '60%', '80%', '100%'] if mode == "percentile" else None,
                gridcolor='rgba(0,0,0,0.2)',
                linecolor='rgba(0,0,0,0.2)'
            ),
            angularaxis=dict(
                gridcolor='rgba(0,0,0,0.2)',
                linecolor='rgba(0,0,0,0.2)',
                tickfont=dict(size=10, color='black')
            ),
            bgcolor='rgba(255,255,255,0)'
        ),
        showlegend=False,
        hovermode='closest',
        height=600,
        margin=dict(l=80, r=80, t=80, b=80),
        plot_bgcolor='rgba(255,255,255,1)',
        paper_bgcolor='rgba(255,255,255,1)',
        font=dict(color='black', size=11)
    )
    
    # Display chart
    st.plotly_chart(fig, use_container_width=True)


def render_performance_profile_panel(profile_data: Dict[str, Any]) -> None:
    """Render the complete performance profile panel."""
    
    if not profile_data:
        st.warning("No performance profile data available.")
        return
    
    # Render header
    render_performance_profile_header(profile_data)
    
    st.divider()
    
    # Render mode toggle
    mode = render_performance_mode_toggle()
    
    st.divider()
    
    # Render radar chart
    render_performance_radar(profile_data, mode=mode)
    
    # Show notes
    notes = profile_data.get("notes", "")
    if notes:
        st.caption(f"ℹ️ {notes}")
