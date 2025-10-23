"""
Player Role Header Component

Renders:
1. Role badge with confidence indicator
2. Similar strikers panel with multi-season data
"""

import streamlit as st
from typing import Dict, List, Optional, Any


# Role colors (hex)
ROLE_COLORS = {
    "Link-Up / Complete Striker": "#C9A227",  # Gold
    "Pressing Striker": "#C94A4A",             # Red
    "Poacher": "#3C7DCC"                       # Blue
}

CONFIDENCE_HIGH_COLOR = "#6B7280"   # Neutral gray
CONFIDENCE_HYBRID_COLOR = "#FBBF24"  # Amber


def render_role_badge(
    role_data: Dict[str, Any],
    show_confidence: bool = True
) -> None:
    """
    Render a role badge with optional confidence indicator.
    
    Args:
        role_data: {role, is_hybrid, confidence, tooltip, top_roles}
        show_confidence: Whether to show confidence pill
    """
    if not role_data:
        return
    
    role = role_data.get("role", "Unknown")
    is_hybrid = role_data.get("is_hybrid", False)
    confidence = role_data.get("confidence", 0)
    tooltip = role_data.get("tooltip", "")
    
    col1, col2 = st.columns([2, 1])
    
    # Role badge
    with col1:
        role_color = ROLE_COLORS.get(role, "#999999")
        badge_label = f"{role} (Hybrid)" if is_hybrid else role
        
        st.markdown(
            f"<div style='display: inline-block; padding: 8px 12px; "
            f"background-color: {role_color}; color: white; border-radius: 4px; "
            f"font-weight: bold; font-size: 0.95em;'>{badge_label}</div>",
            unsafe_allow_html=True
        )
        
        # Show tooltip on hover (using Streamlit's native tooltip)
        if tooltip:
            st.caption(f"ℹ️ {tooltip}")
    
    # Confidence indicator
    if show_confidence:
        with col2:
            if confidence >= 0.60:
                badge_color = CONFIDENCE_HIGH_COLOR
                badge_text = "High"
                emoji = "✓"
            else:
                badge_color = CONFIDENCE_HYBRID_COLOR
                badge_text = f"Hybrid"
                emoji = "⚠"
            
            st.markdown(
                f"<div style='display: inline-block; padding: 6px 10px; "
                f"background-color: {badge_color}; color: white; border-radius: 4px; "
                f"font-size: 0.85em;'>{emoji} {badge_text} ({confidence:.1%})</div>",
                unsafe_allow_html=True
            )


def render_player_role_section(
    player_id: int,
    player_name: str,
    season_id: int,
    role_service,
    show_similar: bool = True,
    similar_k: int = 5
) -> bool:
    """
    Render the complete role section for a player.
    
    Args:
        player_id: Player ID
        player_name: Player name
        season_id: Season ID
        role_service: RoleService instance
        show_similar: Whether to show similar players section
        similar_k: Number of similar players to show
    
    Returns:
        True if data was available and rendered
    """
    # Get role data
    role_data = role_service.get_player_role(player_id, season_id)
    
    if not role_data:
        st.info(f"ℹ️ Role data not available for {player_name} in this season.")
        return False
    
    # Render role badge
    st.subheader("🎯 Role Classification")
    render_role_badge(role_data)
    
    # Show role details if hybrid
    if role_data.get("is_hybrid"):
        with st.expander("📊 Role Probabilities", expanded=False):
            top_roles = role_data.get("top_roles", [])
            for role_info in top_roles:
                prob = role_info.get("prob", 0)
                st.write(f"**{role_info['role']}**: {prob:.1%}")
    
    # Render similar strikers section
    if show_similar:
        st.divider()
        st.subheader("⭐ Most Similar Strikers (all seasons)")
        
        similar_players = role_service.get_similar_players(player_id, season_id, k=similar_k)
        
        if similar_players:
            # Create table data
            table_data = []
            for neighbor in similar_players:
                neighbor_name = neighbor.get("player_name", f"Player {neighbor['player_id']}")
                neighbor_role = neighbor.get("role", "Unknown")
                neighbor_season = neighbor.get("season_id", "—")
                similarity = neighbor.get("similarity", 0)
                
                # Format role badge inline
                role_color = ROLE_COLORS.get(neighbor_role, "#999999")
                
                table_data.append({
                    "Player": neighbor_name,
                    "Season": neighbor_season,
                    "Role": neighbor_role,
                    "Similarity": f"{similarity}%"
                })
            
            # Display as table
            import pandas as pd
            df_similar = pd.DataFrame(table_data)
            
            st.dataframe(
                df_similar,
                use_container_width=True,
                hide_index=True,
                column_config={
                    "Player": st.column_config.TextColumn("Player"),
                    "Season": st.column_config.NumberColumn("Season", format="%d"),
                    "Role": st.column_config.TextColumn("Role"),
                    "Similarity": st.column_config.TextColumn("Similarity")
                }
            )
            
            st.caption(
                f"Similarity scores are cosine similarity (0-100%) on 6D playing style vectors. "
                f"Span across all {len(set(n['season_id'] for n in similar_players))} seasons in dataset."
            )
        else:
            st.warning(f"No similar strikers found for {player_name}.")
    
    return True


def render_role_chip_inline(
    role: str,
    is_hybrid: bool = False,
    confidence: Optional[float] = None,
    compact: bool = False
) -> str:
    """
    Render a compact role chip as HTML string (for inline use in tables).
    
    Args:
        role: Role name
        is_hybrid: Whether role is hybrid
        confidence: Confidence value (optional)
        compact: If True, return minimal HTML
    
    Returns:
        HTML string
    """
    role_color = ROLE_COLORS.get(role, "#999999")
    role_label = f"{role} (Hybrid)" if is_hybrid else role
    
    if compact:
        return f"<span style='background-color: {role_color}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.85em;'>{role_label}</span>"
    else:
        conf_text = f" • {confidence:.0%}" if confidence else ""
        return f"<span style='background-color: {role_color}; color: white; padding: 4px 8px; border-radius: 4px; font-weight: bold;'>{role_label}{conf_text}</span>"


def render_similar_players_compact(
    similar_players: List[Dict[str, Any]],
    max_rows: int = 3
) -> None:
    """
    Render a compact similar players list.
    
    Args:
        similar_players: List of similar player dicts
        max_rows: Maximum number of rows to show
    """
    if not similar_players:
        st.caption("No similar strikers found.")
        return
    
    st.caption(f"**Top {min(len(similar_players), max_rows)} Similar**")
    
    for i, player in enumerate(similar_players[:max_rows]):
        player_name = player.get("player_name", f"Player {player['player_id']}")
        season = player.get("season_id", "—")
        role = player.get("role", "Unknown")
        sim = player.get("similarity", 0)
        
        role_html = render_role_chip_inline(role, compact=True)
        st.write(f"{player_name} ({season}) • {role_html} • **{sim}%**")
