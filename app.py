"""
ISAC2025 Scouting Tool
Player profiling and recruitment intelligence for Club América
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
from api.client import client

# Page configuration
st.set_page_config(
    page_title="Ojos Diamantes Scouting Tool",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====

def home_get_status(api_client):
    """
    Get API connection status.
    
    Args:
        api_client: The StatsBomb API client instance
        
    Returns:
        dict | None: Status dict with 'ok', 'message', etc., or None if unavailable
    """
    try:
        status = api_client.get_status()
        return status
    except Exception as e:
        print(f"Status check failed: {e}")
        return None


# ===== UI (STREAMLIT ONLY BELOW) =====

# Hero Section
st.title("Ojos Diamantes Scouting Tool")
st.markdown("### Player profiling and recruitment intelligence for Club América")
st.markdown("""
Discover, analyze, and compare Liga MX tactical profiles and evolution of players
to help Club América identify players for their system.
""")

# Status indicator
status = home_get_status(client)
if status and status.get('ok'):
    st.success(f"🟢 {status['message']}")
else:
    st.warning("🟡 **Limited data available** - Some features may be restricted")

st.markdown("---")

# Key Features Section
st.subheader("Application Features")

# Create three columns for feature cards
col1, col2, col3 = st.columns(3, gap="large")

with col1:
    st.markdown("""
    ### 🧩 Player Database
    
    **Browse and analyze Liga MX players**
    
    • Quickly understand their tactical profiles  
    • Identify their strengths and weaknesses  
    • View most similar players by style  
    • Investigate season-to-season player evolution  
    """)
    
    if st.button("🔍 Explore Players", use_container_width=True, type="primary"):
        st.switch_page("pages/1_Player_Database.py")

with col2:
    st.markdown("""
    ### ⚖️ Compare Players
    
    **Side-by-side tactical analysis**
    
    • Quickly compare tactical profiles between players  
    • Multiple view modes (Z-score, percentiles)  
    • Cross-season comparison  
    • Similarity analysis  
    """)
    
    if st.button("⚖️ Compare Now", use_container_width=True, type="primary"):
        st.switch_page("pages/2_Compare_Players.py")

with col3:
    st.markdown("""
    ### 📊 Scatter Plots
    
    **Interactive data visualization**
    
    • Discover unique combinations of player skillsets  
    • 40+ metrics from StatsBomb API  
    • Customizable axes and filters  
    • Export options (CSV, PNG)  
    """)
    
    if st.button("📈 Create Plots", use_container_width=True, type="primary"):
        st.switch_page("pages/3_Scatter_Plots.py")

st.markdown("---")

# Methodology Section (Expandable)
with st.expander("📖 Methodology & Technical Details", expanded=False):
    st.markdown("""
    ### Data Source & Processing
    
    **Data Source**: StatsBomb API (Hudl) - Liga MX (Competition ID 73)
    
    **Coverage**: 4 seasons (2021/22, 2022/23, 2023/24, 2024/25)
    
    **Player Filter**: Minimum 500 minutes per season for tactical profiles, PCA and GMM clustering
    
    ### Analysis Methods
    
    **Tactical Profiles**:
    - PCA-based dimensionality reduction from 70+ raw metrics
    - Z-score normalization for cross-season comparison
    - L2-normalized style vectors for similarity analysis
    
    **Role Classification for Centre Forwards**:
    - Gaussian Mixture Model (GMM) clustering on PCA components
    - 3 striker roles: Poacher, Pressing Striker, Link-Up Striker
    - Confidence threshold: <60% = Hybrid classification
    
    **Similarity Analysis**:
    - Cosine distance for striker role comparison
    - Euclidean distance for tactical profile similarity
    - Multi-season player-season nodes
    
    **Position Groups**:
    - Strikers: 6 PCA dimensions → 3 roles
    - Deep Progression Unit: 7 tactical dimensions
    - Attacking Midfielders & Wingers: 7 ability axes
    - Center Backs: 6 defensive dimensions
    """)

# Footer
st.markdown("---")
st.markdown("*Built for ISAC2025 • Data via StatsBomb API (Hudl) • Player Analysis for Club América*")