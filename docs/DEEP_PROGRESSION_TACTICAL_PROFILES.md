# Deep Progression Unit — Tactical Profile Radar Charts

## 🎯 Overview

Deep Progression Unit players (Full-backs, Wing-backs, and Midfielders) now have tactical profile radar charts identical to strikers, displaying their abilities across 7 dimensions derived from PCA analysis.

## ✅ Implementation Complete

### 1. **Artifacts Generated**
Location: `data/processed/deep_progression_artifacts/`

- `ability_axes.json` - 7 ability dimension definitions
- `ability_scores.parquet` - Raw PC scores for all 604 player-seasons
- `ability_percentiles.parquet` - Percentile rankings (0-100)
- `axis_ranges.json` - Min/max/mean/std for each PC
- `league_reference.json` - League averages for comparison

### 2. **Ability Labels (7 Dimensions)**

| PC  | Label | Description |
|-----|-------|-------------|
| PC1 | Final Third Influence | Offensive output, shot creation, attacking presence |
| PC2 | Pass Security | Passing accuracy, completion rate, reliability |
| PC3 | Deep Progression | Progressive passing, line-breaking passes |
| PC4 | Defensive Intensity | Pressing, tackles, defensive work rate |
| PC5 | Attacking Output | Goals, assists, key passes, direct contributions |
| PC6 | Defensive Duel Efficiency | Success rate in defensive duels and challenges |
| PC7 | Carrying & Dribbling | Ball carrying, dribbling success, individual progression |

### 3. **Service Updates**

**`core/profiles/service.py`**
- Added `is_deep_progression()` method
- Added `get_position_group()` method (returns "striker" or "deep_progression")
- Added `build_deep_progression_profile()` method
- Added unified `build_profile()` method (auto-detects position group)

### 4. **UI Integration**

**`pages/2_Player_Database.py`**
- Updated to use unified `build_profile()` method
- Automatically detects player position group
- Shows tactical profile radar for both strikers and Deep Progression players
- Performance profile tab only for strikers (Info tab for others)
- Updated messages to reflect Deep Progression support

### 5. **Radar Chart Display**

**Same radar component (`ui/components/radar.py`)**
- Reuses existing `render_tactical_profile_panel()` function
- Identical visual styling (colors, fonts, layout)
- Same display modes:
  - **Percentile mode** (0-100, default)
  - **Absolute mode** (raw PC scores)
- League average overlay (absolute mode only)

## 📊 Data Source

- **Input**: `data/processed/deep_progression_artifacts/pca_scores_player_season.csv`
- **Cohort**: 604 player-seasons across 4 Liga MX seasons
- **Positions**:
  - Left/Right Back
  - Left/Right Wing Back
  - Centre/Left/Right Defensive Midfielder
  - Centre/Left/Right Midfielder

## 🚀 Usage

### In Player Database:

1. Select a Deep Progression player (full-back or midfielder)
2. Click **"📊 View Tactical Profile"**
3. View 7-dimensional radar chart with percentiles
4. Toggle between Percentile and Absolute modes
5. Compare with league average

### Example Players:
- Full-backs: Luis Reyes, Jesús Angulo
- Defensive Midfielders: Erick Sánchez, Fernando Beltrán
- Central Midfielders: Sebastián Córdova, Alan Mozo

## 🔧 Technical Details

### Normalization:
- **L2 normalized** ability vectors capture playing **style** (relative distribution)
- **Z-score** option available for performance comparison

### Percentile Calculation:
- Rankings computed across entire Deep Progression cohort (all seasons)
- 0th percentile = lowest, 100th percentile = highest

### Artifacts Script:
```bash
python scripts/generate_deep_progression_profile_artifacts.py
```

Re-run this script after updating PCA scores to refresh artifacts.

## 📝 Notes

- Radar charts appear in the **same location and layout** as striker profiles
- Caption updated to indicate Deep Progression Unit cohort
- **Performance Profile** tab still striker-only (not applicable to Deep Progression)
- Similar players feature not yet implemented for Deep Progression (future enhancement)

## ✅ Acceptance Criteria Met

✅ Radar charts display in same interface spot as striker profiles  
✅ Design and plotting functions identical to striker radar  
✅ Uses 7 ability axes as specified  
✅ Handles both L2 (style) and Z-score (performance) modes  
✅ Saves artifacts in `deep_progression_artifacts/`  
✅ Consistent radar appearance, color, and layout  

## 🎨 Visual Example

When viewing a Deep Progression player's tactical profile, you'll see:

1. **Header** with player info (name, team, position, season, stats)
2. **Display Options** toggle (Percentile vs Absolute)
3. **7-axis Radar Chart** (circular, filled, with league average option)
4. **Ability Breakdown** (color-coded metrics grid below radar)
5. **Caption** indicating Deep Progression Unit cohort

---

**Ready to use!** 🎉 

All Deep Progression Unit players now have full tactical profile support in the Player Database.

