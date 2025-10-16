# ⚽ ISAC2025 Streamlit App - Quick Start Guide

A minimal, extensible Streamlit app for player analysis. Each feature lives in its own page file, making it easy for non-coders and AI agents to add new functionality.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Locally
```bash
streamlit run app.py
```

### 3. Set API Credentials (Optional)
The app works without API credentials but will show **"no data available"** where data is needed.

**Option A: Streamlit Secrets** (Recommended for deployment)
Create `.streamlit/secrets.toml`:
```toml
SB_USERNAME = "your_statsbomb_username"
SB_PASSWORD = "your_statsbomb_password"
```

**Option B: Environment Variables**
```bash
export SB_USERNAME="your_statsbomb_username"
export SB_PASSWORD="your_statsbomb_password"
```

**Option C: .env file**
Create `.env` in the project root:
```
SB_USERNAME=your_statsbomb_username
SB_PASSWORD=your_statsbomb_password
```

## 📚 How to Create a New Page (5-minute tutorial)

### For Non-Coders & AI Agents

We follow a **strict separation of concerns** pattern: each page has a **BUSINESS LOGIC** section (no Streamlit) and a **UI** section (Streamlit only).

#### Step 1: Copy the Template

```bash
cp pages/_TEMPLATE_Feature.py pages/2_Your_Feature.py
```

- Streamlit sorts pages by the **leading number**
- Replace `2` with the next available number

#### Step 2: Fill in BUSINESS LOGIC (No Streamlit!)

In the **BUSINESS LOGIC** section, define pure functions that:
- Fetch data from the API client (fetch-only!)
- Compute/aggregate/transform data
- Return UI-ready dicts/lists or `None` if no data

```python
# ===== BUSINESS LOGIC (NO STREAMLIT BELOW) =====

def feature_fetch(api_client, competition_id, season_id):
    """Fetch raw data from API."""
    try:
        data = api_client.team_season_stats(
            competition_id=competition_id,
            season_id=season_id
        )
        return data
    except Exception as e:
        print(f"Failed to fetch: {e}")
        return None

def feature_compute_table(raw_data):
    """Transform raw data into UI-ready format."""
    if raw_data is None or len(raw_data) == 0:
        return None
    
    # Select columns, compute aggregations, etc.
    table = raw_data[['team_name', 'team_season_matches']].copy()
    return table
```

**IMPORTANT RULES:**
- ✅ DO: Use `api_client` parameter for all API calls
- ✅ DO: Return `None` when data is unavailable
- ✅ DO: Handle exceptions gracefully
- ❌ DON'T: Import or use `streamlit` (st.*) in this section
- ❌ DON'T: Put calculations in the API client (keep it fetch-only)

#### Step 3: Fill in UI (Streamlit Only)

In the **UI** section, use Streamlit components:

```python
# ===== UI (STREAMLIT ONLY BELOW) =====

st.title("🔍 Your Feature")

# User inputs
competition_id = st.selectbox("Competition", [73])
season_id = st.selectbox("Season", [317, 281])

# Fetch and compute
with st.spinner("Loading..."):
    raw_data = feature_fetch(client, competition_id, season_id)
    table = feature_compute_table(raw_data)

# Render results
if table is not None:
    st.success(f"✅ Found {len(table)} items")
    st.dataframe(table, use_container_width=True)
else:
    st.error("❌ **no data available**")
    st.info("Check API credentials or parameters")
```

#### Step 4: Add New API Methods (If Needed)

If you need a new API endpoint, add it to `api/client.py`:

```python
def new_endpoint(self, param1, param2):
    """Fetch data from new endpoint (fetch-only, no computations!)."""
    try:
        creds = self._get_creds()
        if creds:
            return sb.new_function(param1=param1, param2=param2, creds=creds)
        else:
            return sb.new_function(param1=param1, param2=param2)
    except Exception as e:
        print(f"Error fetching: {e}")
        return None
```

**Keep API client methods fetch-only!** No calculations, aggregations, or transformations.

#### Step 5: Test & Commit

```bash
streamlit run app.py
# Navigate to your new page
# Test with valid and invalid inputs
git add pages/2_Your_Feature.py
git commit -m "Add Your Feature page"
git push
```

### ✅ Do's and Don'ts

**✅ DO:**
- Keep each feature confined to a single file in `/pages/`
- Follow the BUSINESS LOGIC → UI separation pattern
- Return `None` from business logic when data is unavailable
- Pass `api_client` as parameter to business logic functions
- Keep API client methods fetch-only (no computations)
- Handle all exceptions gracefully
- Always show "no data available" when results are None

**❌ DON'T:**
- Import or use `streamlit` in the BUSINESS LOGIC section
- Put calculations or aggregations in the API client
- Let the page crash when data is missing
- Edit other pages unless absolutely necessary
- Add caching or mock data (out of scope)
- Skip the leading number in page filenames
- Use global variables or state in business logic

## 🔧 Environment Variables / Secrets

### Expected Keys:
- `SB_USERNAME`: StatsBomb username (for premium access)
- `SB_PASSWORD`: StatsBomb password (for premium access)

### Behavior:
- If missing/invalid: app still runs but shows **"no data available"**
- No crashes, graceful degradation
- Check console logs for debugging

## 🚀 Deployment

### Streamlit Community Cloud
1. Push your code to GitHub
2. Connect your repo to Streamlit Cloud
3. Set entry point: `app.py`
4. Configure secrets in the Streamlit Cloud dashboard

### Local Development
```bash
streamlit run app.py --server.port 8501
```

## 🏗️ App Structure

```
/
├── app.py                    # Home page (landing + navigation)
├── pages/                    # Feature pages (auto-sorted by filename)
│   ├── 1_All_Teams.py       # Teams table/list
│   └── 2_Your_Feature.py    # Your new feature here
├── data/
│   └── fetcher.py           # API calls only (no cache/mocks)
├── .streamlit/
│   ├── config.toml          # Dark theme + wide layout
│   └── secrets.toml         # Your API credentials (not in git)
└── README_STREAMLIT.md      # This file
```

## 🎯 Current Features

- **Home**: Landing page with status and navigation
- **All Teams**: Simple table of teams (placeholder for real data)
- **Extensible**: Easy to add new pages without touching existing code

## 🆘 Troubleshooting

**"no data available" everywhere?**
- Check API credentials in secrets or environment variables
- Verify API endpoints are accessible
- Check console logs for error details

**Page not showing up?**
- Make sure filename starts with a number (e.g., `2_My_Page.py`)
- Restart Streamlit after adding new pages

**Need help?**
- Check this README first
- Look at existing pages for examples
- Ask your AI agent to help add new features

---

*Built for ISAC2025 • Keep it simple, keep it working* ⚽
