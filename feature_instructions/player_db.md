# Feature 1 — Player Database & Search (Spec + Agent Instructions)

## What this feature is and why it’s useful

The **Player Database** is the scouting entry point: a fast, filterable list of **all Liga MX players** for a selected season, with **role context** (primary/secondary position) and **key production indicators** (minutes, appearances, goals, assists). It lets analysts quickly discover candidates that **fit Club América’s tactical profile** and build shortlists for deeper evaluation.
New in this spec: **filters for position, preferred foot, and age**, plus **row actions** to jump into “View Tactical Profile” or “Compare” flows (routes stubbed, pages TBA).

---

## Scope (this build)

* Season switcher (Liga MX only; multiple seasons).
* In-memory data (per session), **manual refresh** only.
* Table view (sortable), client-side filters.
* Row actions: **View Tactical Profile** and **Compare** (link to placeholder pages).
* Uses existing API client:

  * `player_season_stats(competition_id, season_id)` for minutes/appearances + positions.   
  * `player_mapping(competition_id, season_id)` (or equivalent) for **preferred foot** and **birth date** (to compute age). 

---

## Data sources (fields needed)

* **Season Player Stats** (per season):

  * `player_name`, `team_name`, `player_season_minutes`, `player_season_appearances`, `player_season_goals_90`, `player_season_assists_90`, `primary_position`, `secondary_position`.  
* **Player Mapping** (same comp/season):

  * `player_preferred_foot`, `player_birth_date` (derive `age`). 

> Note: We only need **one** Player Mapping call per comp/season (join by `player_id`), then enrich Season Player Stats rows.

---

## Table columns (exact)

1. **Player**
2. **Team**
3. **Position** → `"{primary_position} / {secondary_position}"` (fallback “—” if missing). 
4. **Minutes** → `player_season_minutes`. 
5. **Appearances** → `player_season_appearances`. 
6. **Goals** → `round(player_season_goals_90 * minutes / 90)`
7. **Assists** → `round(player_season_assists_90 * minutes / 90)`
8. **Foot** → `player_preferred_foot` (from mapping). 
9. **Age** → derived from `player_birth_date` at render time (years as of season end or “today”; pick one rule and apply consistently). 

Default sort: Player (A–Z), then **Minutos (desc)**

---

## Filters (client-side)

* **Search** (text) → matches Player (case-insensitive substring).
* **Team** (multi-select) → unique `team_name`.
* **Position (primary)** (multi-select) → unique `primary_position`. 
* **Foot** (multi-select) → Left / Right / Both (based on values present). 
* **Age** (range slider) → [min_age, max_age] (derive from birth date). 
* **Minuts ≥** (slider) → integer threshold (default 0).

**All filters combine (AND).** Pagination is client-side (Streamlit table).

---

## Row actions (per selected row)

When the user **selects a row** (or clicks a small “…” action cell), show two buttons:

* **View Tactical Profile** → navigate to `pages/3_Tactical_Profile.py` (TBA) with `player_id` in query params/state.
* **Compare** → navigate to `pages/2_Player_Compare.py` (TBA) with `player_id` in query params/state.

> Use Streamlit’s multipage navigation you already employ (e.g., `st.experimental_set_query_params` + page link, or `st.page_link` if available). If neither is available, store selection in `st.session_state` and display a notice “page coming soon”.

---

## File locations

* **Page:** `pages/2_Player_Database.py` (copied from your `_TEMPLATE_Feature.py`).
* **Business logic helpers:** keep inside the feature file’s **BUSINESS LOGIC** section per template rules.
* **No TTL**; **Refresh** button re-fetches current season.

---

## Function contracts (coding agent can implement exactly)

**Fetch + Join**

```python
def feature_fetch_season(api_client, *, competition_id: int, season_id: int) -> dict | None:
    """
    Returns:
      {
        'season_stats': list[dict],    # Season Player Stats rows
        'mapping': list[dict],         # Player Mapping rows (same comp/season)
      }
    """
```

**Compute rows**

```python
def feature_compute_rows(payload: dict) -> dict | None:
    """
    Joins Season Player Stats with Player Mapping on player_id.
    Derives goals/assists totals, position display, age, and collects filter options.

    Returns:
      {
        'rows': list[dict],         # final table rows (see columns)
        'teams': list[str],         # unique team_name
        'positions': list[str],     # unique primary_position
        'foots': list[str],         # unique preferred foot values
        'age_min': int, 'age_max': int
      }
    """
```

**Filter rows (client-side)**

```python
def feature_filter_rows(
    rows: list[dict],
    *,
    q: str,
    teams: list[str],
    positions: list[str],
    foots: list[str],
    age_range: tuple[int, int],
    min_minutes: int
) -> list[dict]:
    """Applies all filters. Keep fast and pure (no streamlit here)."""
```

**UI Hooks (inside the template’s UI section)**

* Season switcher (`selectbox`), **Refresh** button.
* If cache miss or Refresh: call `feature_fetch_season(...)` → `feature_compute_rows(...)` and cache under `(competition_id, season_id)`.
* Render filters using the returned options.
* Render table with filtered rows.
* When a row is selected: render **View Tactical Profile** + **Compare** buttons and perform navigation with the selected `player_id`.

---

## Implementation notes

* **IDs for joins:** Use the same `player_id` key exposed by both endpoints. (If your API client returns `player_id` as `player_id_offline/live`, keep a small normalizer.)
* **Age calculation:** Decide a single reference date:

  * Option A (simple): compute age as of **today**.
  * Option B (consistent per season): compute age as of **June 30** of the season end year.
    Document the chosen rule in code comments.
* **Null safety:** Default unknown position/foot to “—”; unknown age to “—” (exclude from age filtering unless the user widens range to extremes).
* **Performance:** Liga MX scale is small; client-side filters + in-memory store is fine.
* **Sorting:** After filtering, default sort by **Minutos desc**. Allow user resort via table UI.

---

## Minimal acceptance criteria

* [ ] Switching seasons refetches and rebuilds the table.
* [ ] Manual **Refresh** re-fetches the current season.
* [ ] Filters work together: Team, Position (primary), Preferred Foot, Age range, Minutos ≥.
* [ ] Columns exactly as specified; goals/assists totals computed correctly from per-90 and minutes.
* [ ] Clicking a row surfaces **View Tactical Profile** and **Compare** buttons; clicking either routes with `player_id` attached (placeholder pages are fine).
* [ ] No Streamlit calls in business-logic functions (follows `_TEMPLATE_Feature.py` separation).

---

## Endpoints referenced

* Season Player Stats: `.../api/v4/competitions/{competition_id}/seasons/{season_id}/player-stats`. 

  * Provides minutes, appearances, and primary/secondary positions.  
* Player Mapping: `.../api/v1/player-mapping?competition-id=...&season-id=...` (same scope).

  * Provides preferred foot and birth date for age calculation. 

for both endpoints, call them by calling the respective funtions on the api client object. if no data is outputted, the error most likely lies within the function of the api client or the argument the endpoint expects.
---

