"""
Streamlit Home Page - ISAC2025 Player Analysis
Find players that fit Club América and justify why — fast.
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
from api.client import client

# Page configuration
st.set_page_config(
    page_title="ISAC2025 Player Analysis",
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

# Main title and subtitle
st.title("⚽ ISAC2025 Player Analysis")
st.markdown("**Find players that fit Club América and justify why — fast.**")

# Status section
st.markdown("---")
st.subheader("📊 System Status")

status = home_get_status(client)
if status and status.get('ok'):
    st.success(f"🟢 {status['message']}")
else:
    st.warning("🟡 **no data available**")

# Navigation section
st.markdown("---")
st.subheader("🚀 Quick Navigation")

col1, col2 = st.columns(2)

with col1:
    if st.button("📋 All Teams", use_container_width=True, type="primary"):
        st.switch_page("pages/1_All_Teams.py")

with col2:
    if st.button("➕ Add a New Feature", use_container_width=True):
        st.markdown("---")
        st.markdown("### 📚 How to Add New Features")
        st.markdown("""
        **Quick Tutorial for Non-Coders & AI Agents:**
        
        1. **Copy** `pages/_TEMPLATE_Feature.py` and rename it (e.g., `2_Player_Finder.py`)
        2. **Streamlit sorts pages by the leading number** in the filename
        3. **Fill in the BUSINESS LOGIC block** - fetch data and compute results (no Streamlit!)
        4. **Fill in the UI block** - render inputs and display results
        5. **If data is missing**, return `None` from business logic → UI shows **"no data available"**
        6. **Commit & push** - that's it!
        
        See `README_STREAMLIT.md` for detailed instructions.
        """)

# How to use section
st.markdown("---")
st.subheader("📖 How to Use This App")

st.markdown("""
1. **Navigate** via the left sidebar or the buttons above
2. **Each feature** is a separate page under `/pages/`
3. **If data is missing**, you'll see **"no data available"**

### 🎯 Current Features
- **All Teams**: View all Liga MX teams with season statistics
- **Add New Features**: Copy the template and follow the pattern

### 🔧 Configuration
- API credentials loaded from `.env` file
- If missing/invalid, the app runs but shows "no data available" where needed
- Check `README_STREAMLIT.md` for detailed setup instructions
""")

# Footer
st.markdown("---")
st.markdown("*Built with Streamlit • ISAC2025 Project*")
