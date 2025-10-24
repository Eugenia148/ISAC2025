"""
[FEATURE NAME] Page - [Brief description]

INSTRUCTIONS:
1. Copy this file and rename it with a number prefix (e.g., 2_Player_Finder.py)
2. Fill in the BUSINESS LOGIC section with your data fetching and computation
3. Fill in the UI section with your Streamlit components
4. DO NOT import or use Streamlit in the BUSINESS LOGIC section!
5. Return None from business logic functions when data is unavailable
"""

# ===== IMPORTS & PAGE CONFIG =====
import streamlit as st
from api.client import client  # Import the API client

# Page configuration
st.set_page_config(
    page_title="[Feature Name]",
    page_icon="🎯",  # Choose an appropriate icon
    layout="wide"
)


# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====
# IMPORTANT: Do not import or use 'streamlit' (st.*) in this section!
# All API calls must go through the api_client parameter
# Return None or empty lists/dicts when data is unavailable

def feature_fetch(api_client, **params):
    """
    Fetch raw data from API.
    
    Args:
        api_client: The StatsBomb API client instance
        **params: Any parameters needed for the API call
        
    Returns:
        DataFrame | list | dict | None: Raw data from API or None if unavailable
    
    Example:
        data = api_client.competitions()
        data = api_client.team_season_stats(competition_id=73, season_id=317)
    """
    try:
        # TODO: Replace with actual API call
        # raw_data = api_client.some_method(params...)
        raw_data = None
        return raw_data
    except Exception as e:
        print(f"Failed to fetch data: {e}")
        return None


def feature_compute_results(raw_data):
    """
    Compute/aggregate/transform raw data into UI-ready format.
    
    Args:
        raw_data: Raw data from feature_fetch() or None
        
    Returns:
        dict | list | None: Computed results ready for UI rendering, or None if no data
    
    Example:
        If raw_data is a DataFrame, select columns, compute aggregations, etc.
        Return a dict or list that the UI can easily display.
    """
    if raw_data is None:
        return None
    
    try:
        # TODO: Implement your computation logic here
        # Examples:
        # - Filter/select columns from DataFrame
        # - Compute aggregations (mean, sum, etc.)
        # - Format data for tables/charts
        # - Return structured dicts/lists
        
        results = {
            'summary': 'Example summary',
            'data': []
        }
        return results
    except Exception as e:
        print(f"Failed to compute results: {e}")
        return None


def feature_compute_additional(raw_data):
    """
    Optional: Compute additional metrics or transformations.
    
    Args:
        raw_data: Raw data from feature_fetch() or None
        
    Returns:
        dict | None: Additional computed data or None
    """
    if raw_data is None:
        return None
    
    try:
        # TODO: Implement additional computations if needed
        additional = {}
        return additional
    except Exception as e:
        print(f"Failed to compute additional data: {e}")
        return None


# ===== UI (STREAMLIT ONLY BELOW) =====
# This section contains all Streamlit components and user interactions

# Page header
st.title("🎯 [Feature Name]")
st.markdown("[Brief description of what this page does]")

# User inputs (if needed)
st.markdown("---")
st.subheader("⚙️ Settings")

# TODO: Add your input widgets here
# Examples:
# competition = st.selectbox("Select Competition", options=["Liga MX", "Premier League"])
# season = st.selectbox("Select Season", options=["2024/2025", "2023/2024"])
# min_matches = st.slider("Minimum Matches", min_value=1, max_value=50, value=10)

# Fetch and compute data
st.markdown("---")
st.subheader("📊 Results")

with st.spinner("Loading data..."):
    # TODO: Call your business logic functions with appropriate parameters
    raw_data = feature_fetch(client)  # Pass any needed parameters
    results = feature_compute_results(raw_data)
    additional = feature_compute_additional(raw_data)

# Display results
if results is not None:
    # TODO: Render your results here
    # Examples:
    # st.success(f"✅ Found {len(results['data'])} items")
    # st.dataframe(results['data'], use_container_width=True)
    # st.metric("Total", results['total'])
    # st.plotly_chart(figure)
    
    st.success("✅ Data loaded successfully")
    st.json(results)  # Replace with actual rendering
    
    # Display additional data if available
    if additional:
        st.markdown("---")
        st.subheader("📈 Additional Metrics")
        st.json(additional)  # Replace with actual rendering
        
else:
    # No data available
    st.error("❌ **no data available**")
    st.info("""
    No data found for the selected parameters.
    
    This could mean:
    - API credentials issue
    - Data not available
    - Network connection problem
    - Invalid parameters
    """)

# Footer
st.markdown("---")
st.caption("*Data from StatsBomb API • Use sidebar to navigate*")


# ===== GUIDELINES & BEST PRACTICES =====
"""
KEY RULES:
1. ✅ DO: Keep business logic functions pure (no Streamlit)
2. ✅ DO: Return None when data is unavailable
3. ✅ DO: Handle all exceptions gracefully
4. ✅ DO: Use the api_client parameter for all API calls
5. ✅ DO: Keep the API client fetch-only (no computations in API client)

6. ❌ DON'T: Import or use streamlit in BUSINESS LOGIC section
7. ❌ DON'T: Put calculations in the API client
8. ❌ DON'T: Crash the page when data is missing
9. ❌ DON'T: Use global variables or state in business logic

WORKFLOW:
1. User interacts with UI (selects, sliders, buttons)
2. UI calls business logic functions with parameters
3. Business logic fetches data via API client
4. Business logic computes/transforms data
5. Business logic returns UI-ready results or None
6. UI renders results or "no data available"
"""
