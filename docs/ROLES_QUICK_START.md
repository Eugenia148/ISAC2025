# Striker Roles & Similar Players — Quick Start Guide

## ⚡ 30-Second Overview

The Striker Roles feature classifies strikers into 3 playing styles:
- **Link-Up / Complete Striker** (gold) — builders & playmakers
- **Pressing Striker** (red) — defensive leaders
- **Poacher** (blue) — box predators

Plus finds similar players across all seasons using PCA + cosine similarity.

---

## 🚀 Quick Setup

### 1️⃣ Generate Artifacts (in notebook)
Open `notebooks/striker_pca_clustering.ipynb` and add cells at the end:

```python
# Import artifact saving functions
import sys
sys.path.insert(0, "notebooks")
from save_role_artifacts import (
    save_season_artifacts,
    save_multiseasson_neighbors,
    save_global_config
)

# After PCA and GMM are computed for each season, save artifacts
# (See notebook cells for complete example)

# Save global config
save_global_config()
```

Takes ~2-5 minutes. Creates per-season models + multi-season similarity data.

### 2️⃣ View in Player Database
Open `pages/2_Player_Database.py` → Select striker → Click profile → New tab "⭐ Role & Similarity"

### 3️⃣ Done! ✅
Role badges and similar strikers appear automatically.

---

## 📖 Code Examples

### Get a Player's Role
```python
from core.roles.service import get_role_service

service = get_role_service()
role_data = service.get_player_role(player_id=1234, season_id=317)

print(f"Role: {role_data['role']}")
print(f"Hybrid: {role_data['is_hybrid']}")
print(f"Confidence: {role_data['confidence']:.0%}")
# Output:
# Role: Poacher
# Hybrid: False
# Confidence: 73%
```

### Find Similar Strikers
```python
similar = service.get_similar_players(player_id=1234, season_id=317, k=5)

for player in similar:
    print(f"{player['player_name']} ({player['season_id']}) "
          f"• {player['role']} • {player['similarity']}%")
# Output:
# Player A (2024) • Poacher • 92%
# Player B (2023) • Poacher • 88%
# ...
```

### Render in Streamlit
```python
from ui.components.player_role_header import render_player_role_section

render_player_role_section(
    player_id=player_id,
    player_name=player_name,
    season_id=317,
    role_service=service,
    show_similar=True,
    similar_k=5
)
```

---

## 🎨 UI Elements

### Role Badge
```
┌──────────────────────────┬─────────────────┐
│ 🔵 Poacher               │ ✓ High (73%)     │
│ Focuses on box...        │                 │
└──────────────────────────┴─────────────────┘
```

### Similar Strikers Table
```
Player Name              Season  Role                          Similarity
─────────────────────────────────────────────────────────────────────────
Striker A               2024   🔵 Poacher                    92%
Striker B               2023   🔵 Poacher                    88%
Striker C               2024   🟡 Link-Up / Complete         85%
```

---

## 🔑 Key Parameters

### Season Mapping
```python
{
    "2024/25": 317,
    "2023/24": 281,
    "2022/23": 235,
    "2021/22": 108
}
```

### Thresholds
- **Hybrid detection:** max_probability < 0.60
- **Minutes filter:** > 500 minutes per season
- **Similarity metric:** Cosine on 6D PCA vectors

---

## 🧪 Testing

Run all tests:
```bash
pytest tests/test_roles.py -v
```

Run specific test class:
```bash
pytest tests/test_roles.py::TestHybridThreshold -v
```

---

## ⚙️ Artifacts Structure

```
data/processed/roles/
├── config.json                    # Global config
├── player_neighbors.parquet       # Multi-season similarity (KEY FILE)
├── 317/                           # Season 2024/25
│   ├── player_style_vectors.parquet
│   ├── player_cluster_probs.parquet
│   ├── pca_model.pkl
│   ├── gmm_model.pkl
│   ├── cluster_to_role.json
│   └── role_descriptions.json
├── 281/                           # Season 2023/24
├── 235/                           # Season 2022/23
└── 108/                           # Season 2021/22
```

---

## 🐛 Common Issues

| Issue | Solution |
|-------|----------|
| "No role data available" | Player has <500 minutes or isn't a striker |
| "No similar players found" | Rare; check season_id matches directory name |
| Slow first load | Normal (~100-200ms); subsequent loads cached |
| Tests fail | Run `pytest tests/test_roles.py::TestRoleMapping` first |

---

## 📊 What Gets Computed

### Per Season
1. **PCA:** 6D playing style vectors from 14+ metrics
2. **GMM:** 3-cluster model with posteriors
3. **Outputs:** style_vectors.parquet, cluster_probs.parquet, models

### Multi-Season
1. **Similarity:** Cosine distance on all PCA vectors
2. **Neighbors:** Top-10 most similar for each (player, season)
3. **Output:** player_neighbors.parquet (~100K+ rows)

---

## 🎯 API Reference

### Loader
```python
loader.load_cluster_to_role()           # Dict[int, str]
loader.load_role_descriptions()         # Dict[str, str]
loader.get_player_style_row(pid, sid)   # Dict | None
loader.get_player_cluster_probs(pid, sid) # Dict | None
loader.get_neighbors(pid, sid, k=5)     # List[Dict]
```

### Service
```python
service.get_player_role(pid, sid)           # Dict | None
service.get_similar_players(pid, sid, k=5)  # List[Dict]
service.is_valid_data(pid, sid)             # Bool
```

### UI
```python
render_role_badge(role_data)
render_player_role_section(pid, name, sid, service, show_similar=True, similar_k=5)
render_role_chip_inline(role, is_hybrid=False, compact=True)
render_similar_players_compact(similar_list, max_rows=3)
```

---

## ✅ Checklist

- [ ] Run artifact generation: `python scripts/generate_role_artifacts.py`
- [ ] Verify directories created: `data/processed/roles/{108,235,281,317}/`
- [ ] Check player_neighbors.parquet exists
- [ ] Run tests: `pytest tests/test_roles.py -v`
- [ ] Open Player Database page
- [ ] Select a striker player
- [ ] Click on their profile
- [ ] See new "⭐ Role & Similarity" tab
- [ ] Role badge + similar strikers display ✅

---

**Next Step:** Read `docs/IMPLEMENTATION_ROLES.md` for detailed architecture & troubleshooting.
