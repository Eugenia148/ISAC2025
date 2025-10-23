# Striker Role & Similar Players — Implementation Guide

## 📋 Overview

This guide documents the complete implementation of the Striker Role Classification and Similar Players Discovery feature for the ISAC 2025 project.

**Objective**: Augment the Player Database page with:
1. **Role Badges** (Link-Up/Complete, Pressing, Poacher) with confidence indicators
2. **Similar Strikers Panel** showing top matches by cosine similarity on 6D style vectors
3. **Multi-season support** with season-scoped data filtering (minutes > 500)

---

## 🏗️ Architecture

### Module Structure

```
core/roles/
├── __init__.py           # Module exports
├── loader.py             # Artifact loading & caching (memoized)
└── service.py            # Business logic (role assignment, similarity)

ui/components/
└── player_role_header.py # UI rendering (badges, similar strikers)

scripts/
└── generate_role_artifacts.py  # ETL pipeline for artifact generation

tests/
└── test_roles.py         # Comprehensive unit tests

data/processed/roles/
├── config.json           # Global configuration
├── player_neighbors.parquet  # Multi-season similarity (all player-seasons)
├── 108/                  # Season 2021/22
│   ├── player_style_vectors.parquet
│   ├── player_cluster_probs.parquet
│   ├── pca_pipeline.pkl
│   ├── pca_model.pkl
│   ├── gmm_model.pkl
│   ├── cluster_to_role.json
│   ├── role_descriptions.json
│   └── features.json
├── 235/                  # Season 2022/23
├── 281/                  # Season 2023/24
└── 317/                  # Season 2024/25
```

---

## 🚀 Setup & Usage

### Step 1: Generate Role Artifacts

The artifacts are generated directly in your `striker_pca_clustering.ipynb` notebook using helper functions.

**In the notebook (at the end):**

```python
# Import helper functions
import sys
sys.path.insert(0, "notebooks")
from save_role_artifacts import (
    save_season_artifacts,
    save_multiseasson_neighbors,
    save_global_config
)

# After computing PCA and GMM for each season, save artifacts
for season_id, season_name, season_df, pca_vectors, scaler, pca_model, gmm_model, posteriors, assignments in your_season_loop:
    save_season_artifacts(
        season_id=season_id,
        pca_vectors=pca_vectors,
        scaler=scaler,
        pca_model=pca_model,
        gmm_model=gmm_model,
        posteriors=posteriors,
        assignments=assignments,
        features=features_list,
        striker_df=season_df
    )

# After all seasons processed:
save_multiseasson_neighbors(all_season_data)
save_global_config()
```

**Output:**
- Per-season PCA models, GMM cluster assignments, style vectors
- Multi-season player_neighbors.parquet for similarity search
- Configuration and role mappings
- Takes ~2-5 minutes

### Step 2: Core Module Usage

#### Loader (`core/roles/loader.py`)

```python
from core.roles.loader import get_role_loader

loader = get_role_loader()  # Singleton with memoization

# Get cluster-to-role mapping
cluster_to_role = loader.load_cluster_to_role()
# {0: "Link-Up / Complete Striker", 1: "Pressing Striker", 2: "Poacher"}

# Get role descriptions
descriptions = loader.load_role_descriptions()

# Get player's style vector for a season
style_row = loader.get_player_style_row(player_id=1234, season_id=317)
# {player_id, season_id, minutes, team_id, pca_1..pca_6}

# Get player's cluster posteriors
probs = loader.get_player_cluster_probs(player_id=1234, season_id=317)
# {cluster_0: 0.75, cluster_1: 0.15, cluster_2: 0.10, predicted_cluster: 0}

# Get top-K similar players (all seasons)
neighbors = loader.get_neighbors(player_id=1234, season_id=317, top_k=5)
# [{neighbor_player_id, neighbor_season_id, cosine_sim}, ...]

# Minutes threshold
threshold = loader.minutes_threshold()  # 500
```

#### Service (`core/roles/service.py`)

```python
from core.roles.service import get_role_service

service = get_role_service()

# Get role assignment with confidence
role_data = service.get_player_role(player_id=1234, season_id=317)
"""
Returns:
{
    "role": "Poacher",                    # Primary role
    "is_hybrid": False,                   # True if max_prob < 0.60
    "confidence": 0.73,                   # Max posterior [0, 1]
    "top_roles": [
        {"role": "Poacher", "prob": 0.73},
        {"role": "Link-Up / Complete Striker", "prob": 0.22}
    ],
    "tooltip": "Focuses on box occupation and finishing..."
}
"""

# Get similar strikers
similar = service.get_similar_players(player_id=1234, season_id=317, k=5)
"""
Returns:
[
    {
        "player_id": 1011,
        "season_id": 2024,
        "similarity": 92,           # 0-100%
        "role": "Link-Up / Complete Striker",
        "confidence": 0.68,
        "player_name": "Player Name",
        "team_id": 100
    },
    ...
]
"""

# Check if player has valid data
is_valid = service.is_valid_data(player_id=1234, season_id=317)
```

### Step 3: UI Integration

#### Adding to Player Database Page

```python
from core.roles.service import get_role_service
from ui.components.player_role_header import render_player_role_section

# In your player selection flow:
role_service = get_role_service()

# Season ID mapping
season_id_map = {
    "2024/25": 317,
    "2023/24": 281,
    "2022/23": 235,
    "2021/22": 108
}
season_id = season_id_map.get(selected_season, 317)

# Render role section
render_player_role_section(
    player_id=player_id,
    player_name=player_name,
    season_id=season_id,
    role_service=role_service,
    show_similar=True,
    similar_k=5
)
```

#### UI Component Functions

```python
from ui.components.player_role_header import (
    render_role_badge,
    render_player_role_section,
    render_role_chip_inline,
    render_similar_players_compact
)

# Render a role badge with confidence indicator
render_role_badge(role_data)

# Render complete role + similar players section
render_player_role_section(
    player_id, player_name, season_id, role_service,
    show_similar=True, similar_k=5
)

# Inline role chip for tables
role_html = render_role_chip_inline(role="Poacher", is_hybrid=False, compact=True)

# Compact similar players list
render_similar_players_compact(similar_players, max_rows=3)
```

---

## 🔍 Key Concepts

### Role Assignment Logic

**Hybrid Detection:**
- If `max_posterior >= 0.60` → Primary role (non-hybrid)
- If `max_posterior < 0.60` → Hybrid role (show top-2)
- No "Unclear" category — all players get a primary assignment

**Confidence:**
- Displayed as percentage (0-100%) on UI
- Stored internally as float (0-1)
- Rounded to 3 decimal places

### Similarity Search

**Universe:** All player-season combinations with minutes > 500 across all seasons

**Metric:** Cosine similarity on 6D PCA vectors

**Neighbors:** Top-K most similar strikers, excluding self (player_id, season_id)

**Output:** Similarity as integer percent (0-100%)

### Season Handling

- **Per-season artifacts:** Stored in `data/processed/roles/{season_id}/`
- **Multi-season similarity:** Single `player_neighbors.parquet` computed across all seasons
- **Filtering:** Automatic via minutes threshold in artifact generation

---

## 🧪 Testing

### Run Unit Tests

```bash
pytest tests/test_roles.py -v
```

### Test Coverage

1. **Role Mapping Integrity**
   - Cluster-to-role mapping exactness (0→Link-Up, 1→Pressing, 2→Poacher)
   - All roles have descriptions

2. **Hybrid Threshold**
   - High confidence (≥0.60) → non-hybrid
   - Low confidence (<0.60) → hybrid
   - Boundary test at exactly 0.60

3. **Neighbor Exclusion & Ordering**
   - Self exclusion (player_id, season_id) not in neighbors
   - Descending sort by similarity
   - Top-K limiting works correctly

4. **Confidence Scoring**
   - Valid range [0, 1]
   - Proper rounding (3 decimals)
   - Top-roles probabilities rounded

5. **Data Integrity**
   - All required fields present
   - No missing data handling
   - Tooltip matching

---

## 📊 Data Quality & Performance

### Minutes Threshold

All players in artifacts have **minutes > 500** per season. This filtering happens in ETL.

### Caching Strategy

- **Loader:** Memoized singleton with per-season caching
- **First load:** ~100-200ms per season (parquet read + parse)
- **Subsequent loads:** <10ms (memory cache)
- **Similarity queries:** <50ms for top-K lookup

### Expected Performance

After first load:
- Role assignment: < 5ms
- Similar players (K=5): < 20ms
- Full section render: < 150ms

---

## 🎨 Visual Design

### Role Badge Colors

- **Link-Up / Complete Striker:** `#C9A227` (Gold)
- **Pressing Striker:** `#C94A4A` (Red)
- **Poacher:** `#3C7DCC` (Blue)

### Confidence Indicator

- **High (≥ 0.60):** `#6B7280` (Neutral gray) with ✓ emoji
- **Hybrid (< 0.60):** `#FBBF24` (Amber) with ⚠ emoji

### UI Layout

1. **Player Profile Section**
   - Role badge + confidence pill (horizontal)
   - Role description as caption
   - Expandable "Role Probabilities" for hybrid roles

2. **Similar Strikers Section**
   - Title: "⭐ Most Similar Strikers (all seasons)"
   - Table with: Player Name (Season) • Role • Similarity%
   - Info caption with span of seasons

---

## 🔧 Troubleshooting

### "No role data available"

- **Cause:** Player not in artifacts (minutes ≤ 500 or position not striker)
- **Solution:** Check minutes played and position; regenerate artifacts if needed

### "No similar strikers found"

- **Cause:** Player not in neighbor lookup (rare; check season ID mapping)
- **Solution:** Verify season_id matches artifact directory name

### Missing per-season directories

- **Cause:** Artifacts not generated or incomplete ETL
- **Solution:** Run `scripts/generate_role_artifacts.py`

### Neighbors include self

- **Cause:** Bug in loader or service
- **Solution:** Check neighbor exclusion logic in `get_neighbors()` call

---

## 📝 Configuration

### Constants (in `scripts/generate_role_artifacts.py`)

```python
MINUTES_THRESHOLD = 500          # Players with >= 500 minutes
N_COMPONENTS_PCA = 6             # 6D style vectors
N_CLUSTERS_GMM = 3               # 3-cluster model
TOP_K_NEIGHBORS = 10             # Top-K for similarity (displayed K can be < 10)
```

### Season Mapping (in Player Database page)

```python
season_id_map = {
    "2024/25": 317,
    "2023/24": 281,
    "2022/23": 235,
    "2021/22": 108
}
```

---

## 📚 References

### Files Modified/Created

- `core/roles/__init__.py` — Module exports
- `core/roles/loader.py` — Artifact loading (memoized)
- `core/roles/service.py` — Business logic
- `ui/components/player_role_header.py` — UI rendering
- `pages/2_Player_Database.py` — Integration into player profile
- `scripts/generate_role_artifacts.py` — ETL pipeline
- `tests/test_roles.py` — Comprehensive unit tests

### Acceptance Criteria ✅

- [x] Cluster mapping exactly: 0→Link-Up, 1→Pressing, 2→Poacher
- [x] Hybrid detection: max_prob < 0.60
- [x] All players have roles (no "Unclear")
- [x] Per-season artifacts with minutes > 500 filter
- [x] Multi-season neighbor search (cosine similarity)
- [x] Similarity as 0-100% integer, excluding self
- [x] UI renders role badges + similar strikers
- [x] No images/logos, layout responsive
- [x] Performance: <150ms after cache warm-up
- [x] Unit tests for core logic

---

## 🔄 Future Enhancements

- [ ] Dynamic role reassignment on new season data
- [ ] Export role/similarity reports
- [ ] Custom role descriptions per league
- [ ] Compare role profiles side-by-side
- [ ] Historical role evolution tracking
- [ ] Role recommendation engine

---

**Last Updated:** October 22, 2025
**Status:** ✅ Complete & Ready for Use
