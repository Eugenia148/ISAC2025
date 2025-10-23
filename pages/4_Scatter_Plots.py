"""
Scatter Plots Page - Interactive Player Analysis
Displays interactive scatter plots of players using real data from Hudl/StatsBomb API.
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from api.client import client
import io
import base64

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
            'player_season_shots_90': 0,
            'player_season_xg_90': 0,
            'player_season_xa_90': 0,
            'player_season_passes_90': 0,
            'player_season_progressive_passes_90': 0,
            'player_season_dribbles_90': 0,
            'player_season_duels_90': 0
        }
        
        for col, default_val in required_columns.items():
            if col not in df.columns:
                df[col] = default_val
        
        # Calculate total metrics from per90 stats
        minutes = df['player_season_minutes']
        df['goals'] = (df['player_season_goals_90'] * minutes / 90).round(2)
        df['assists'] = (df['player_season_assists_90'] * minutes / 90).round(2)
        df['shots'] = (df['player_season_shots_90'] * minutes / 90).round(2)
        df['xG'] = (df['player_season_xg_90'] * minutes / 90).round(2)
        df['xA'] = (df['player_season_xa_90'] * minutes / 90).round(2)
        df['passes_completed'] = (df['player_season_passes_90'] * minutes / 90).round(2)
        df['progressive_passes'] = (df['player_season_progressive_passes_90'] * minutes / 90).round(2)
        df['dribbles_succeeded'] = (df['player_season_dribbles_90'] * minutes / 90).round(2)
        df['duels_won'] = (df['player_season_duels_90'] * minutes / 90).round(2)
        
        # Create per90 metrics for applicable columns
        per90_metrics = ['goals', 'assists', 'shots', 'xG', 'xA', 'passes_completed', 
                         'progressive_passes', 'dribbles_succeeded', 'duels_won']
        
        for metric in per90_metrics:
            if metric in df.columns:
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
    basic_metrics = ['goals', 'assists', 'shots', 'xG', 'xA', 'passes_completed', 
                     'progressive_passes', 'dribbles_succeeded', 'duels_won', 'minutes_played']
    
    per90_metrics = [col for col in df.columns if col.endswith('_per90')]
    
    # Filter to only include metrics that exist in the dataframe
    available_basic = [col for col in basic_metrics if col in df.columns]
    available_per90 = [col for col in per90_metrics if col in df.columns]
    
    return {
        'basic': available_basic,
        'per90': available_per90,
        'all': available_basic + available_per90
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
        title=f"{y_var} vs {x_var} (colored by {color_var})"
    )
    
    # Add median reference lines
    x_median = df[x_var].median()
    y_median = df[y_var].median()
    
    fig.add_vline(x=x_median, line_dash="dash", line_color="red", 
                  annotation_text=f"Median {x_var}: {x_median:.2f}")
    fig.add_hline(y=y_median, line_dash="dash", line_color="red", 
                  annotation_text=f"Median {y_var}: {y_median:.2f}")
    
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
        x_var = st.selectbox(
            "X-axis Variable",
            options=available_metrics['all'],
            index=available_metrics['all'].index('xA') if 'xA' in available_metrics['all'] else 0
        )
    
    with col2:
        # Y-axis variable
        y_var = st.selectbox(
            "Y-axis Variable",
            options=available_metrics['all'],
            index=available_metrics['all'].index('duels_won') if 'duels_won' in available_metrics['all'] else 1
        )
        
        # Color variable
        color_var = st.selectbox(
            "Color Variable",
            options=available_metrics['all'],
            index=available_metrics['all'].index('minutes_played') if 'minutes_played' in available_metrics['all'] else 2
        )
    
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
            
            # Create scatter plot
            fig = feature_create_scatter_plot(
                filtered_data, x_var, y_var, color_var, colorscale, show_labels
            )
            
            if fig:
                st.plotly_chart(fig, use_container_width=True)
                
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
