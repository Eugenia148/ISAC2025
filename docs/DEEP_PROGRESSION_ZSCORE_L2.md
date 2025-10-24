# Deep Progression Unit — Z-Score & L2 Tactical Profiles

## Overview

Deep Progression Unit players now have **three display modes** for their tactical profiles:

1. **📊 Performance (Z-score)** — Default mode, shows performance vs league average
2. **🎨 Style (L2-normalized)** — Shows playing style distribution (unit vector)
3. **📈 Percentiles (0-100)** — Shows ranking within the cohort

---

## Display Modes

### 1. Performance (Z-score) — Default ✨

**Purpose:** Compare player performance to league average

**How it works:**
- Each ability (PC1-PC7) is normalized to show **standard deviations from the mean**
- Computed **per season** to account for league evolution
- **Capped at ±2.5** for readability
- **Percentiles automatically shown** alongside Z-scores for easier interpretation

**Interpretation:**
- `0.0` = League average (50th percentile)
- `+1.0` = One standard deviation above average (84th percentile)
- `+2.0` = Two standard deviations above average (98th percentile)
- `-1.0` = One standard deviation below average (16th percentile)
- `-2.0` = Two standard deviations below average (2nd percentile)

**Display format:**
- **Value:** `+1.44 SD`
- **Delta:** `92nd percentile` (automatically converted from Z-score)
- **Hover tooltip:** Shows both Z-score and percentile with full explanation

**Color coding:**
- 🟢 Green: ≥ +1.5 (well above average, ~93rd percentile+)
- 🟡 Yellow: +0.5 to +1.5 (above average, ~69th-93rd percentile)
- ⚪ White: -0.5 to +0.5 (average, ~31st-69th percentile)
- 🟠 Orange: -1.5 to -0.5 (below average, ~7th-31st percentile)
- 🔴 Red: ≤ -1.5 (well below average, ~7th percentile or lower)

**Use cases:**
- Identify players who excel in specific dimensions
- Scout for specific strengths/weaknesses
- Compare performance across seasons
- Quick understanding via percentile ranks

---

### 2. Style (L2-normalized)

**Purpose:** Compare playing style distribution regardless of overall level

**How it works:**
- Each player's 7D ability vector is **normalized to unit length**
- Emphasizes the **shape** of the profile rather than magnitude
- All players have the same "total ability" (L2 norm = 1.0)

**Interpretation:**
- Values show the **relative distribution** of abilities
- A player with high PC1 and low PC7 has a style oriented toward Final Third Influence vs Carrying & Dribbling
- Two players with similar L2 profiles have similar playing styles, regardless of performance level

**Use cases:**
- Find stylistically similar players (e.g., for tactical fit)
- Identify role archetypes
- Scout for specific playing styles

---

### 3. Percentiles (0-100)

**Purpose:** Show ranking within the Deep Progression Unit cohort

**How it works:**
- Each ability is ranked within all Deep Progression players in the dataset
- `50%` = median, `90%` = top 10%, etc.

**Color coding:**
- 🟢 Green: ≥ 75% (top quartile)
- 🟡 Yellow: 50-75% (above median)
- 🟠 Orange: 25-50% (below median)
- 🔴 Red: < 25% (bottom quartile)

**Use cases:**
- Quick ranking/comparison
- Identify elite performers in specific dimensions
- Benchmarking

---

## Artifacts Generated

### Files created by `generate_deep_progression_zscore_l2.py`:

1. **`zscore_params.json`**
   - Contains mean and std for each PC, per season
   - Used for reproducibility and future data updates
   - Format:
     ```json
     {
       "z_cap_min": -2.5,
       "z_cap_max": 2.5,
       "seasons": {
         "108": {"PC1": {"mean": 0.0, "std": 3.2}, ...},
         ...
       }
     }
     ```

2. **`ability_scores_zscore.parquet`**
   - Z-score normalized values (capped)
   - Index: `player_season_id` (e.g., `26297_317`)
   - Columns: `player_id`, `season_id`, `PC1`–`PC7`

3. **`ability_scores_l2.parquet`**
   - L2-normalized values (unit vectors)
   - Index: `player_season_id`
   - Columns: `player_id`, `season_id`, `PC1`–`PC7`
   - All rows have L2 norm = 1.0

---

## Implementation Details

### Code Changes

1. **`core/profiles/loader.py`**
   - Added `get_ability_scores_zscore()` method
   - Added `get_ability_scores_l2()` method

2. **`core/profiles/service.py`**
   - Updated `build_deep_progression_profile()` to load Z-score and L2 data
   - Profile payload now includes `ability_scores_zscore` and `ability_scores_l2`

3. **`ui/components/radar.py`**
   - Updated `render_mode_toggle()` to support 3 modes for Deep Progression
   - Updated `render_tactical_profile_radar()` to handle Z-score and L2 modes
   - Added mode-specific color coding and value formatting
   - Updated footer notes to explain each mode

---

## Usage in Streamlit App

When viewing a Deep Progression Unit player's tactical profile:

1. **Default view:** Performance (Z-score) mode
2. **Toggle options:** Use radio buttons to switch between modes
3. **Radar chart:** Automatically updates with appropriate scales and colors
4. **Value breakdown:** Shows numeric values with color coding
5. **Footer note:** Explains the current mode

---

## Example Output

### Player: Carlos Alberto Rodríguez Gómez (2024/25)

**Z-Scores (Performance):**
- PC1 (Final Third Influence): +2.18 SD → **99th percentile** 🟢
- PC2 (Pass Security): +0.27 SD → **61st percentile** ⚪
- PC3 (Deep Progression): +2.50 SD → **99th percentile** 🟢
- PC4 (Aggressiveness): -0.37 SD → **36th percentile** ⚪
- PC5 (Attacking Output): +1.44 SD → **93rd percentile** 🟡
- PC6 (Defensive Duel Efficiency): -0.15 SD → **44th percentile** ⚪
- PC7 (Carrying & Dribbling): -0.82 SD → **21st percentile** 🟠

**Interpretation:** Elite progressive passer (top 1%) with strong attacking output (top 7%), but below average in carrying/dribbling (bottom 21%).

---

## Regenerating Artifacts

To regenerate Z-score and L2 artifacts (e.g., after data updates):

```bash
python scripts/generate_deep_progression_zscore_l2.py
```

This will recompute all normalization parameters and update the parquet files.

---

## Technical Notes

### Why Z-score as default?

- **Performance-oriented:** Shows actual ability level, not just style
- **Interpretable:** Standard deviations are intuitive
- **Comparable:** Can compare across abilities with different scales
- **Statistically sound:** Based on normal distribution assumptions

### Why cap Z-scores at ±2.5?

- **Readability:** Extreme outliers can make charts hard to read
- **Focus:** Values beyond ±2.5 are rare (< 1% of data)
- **Fairness:** Prevents one extreme dimension from dominating the visualization

### L2 normalization vs Z-score

- **L2:** All players have "equal total ability" → pure style comparison
- **Z-score:** Players have different levels → performance + style

---

## Future Enhancements

- [ ] Add league average overlay for Z-score mode
- [ ] Implement player comparison view with dual radars
- [ ] Add "style similarity score" based on L2 vectors
- [ ] Generate batch radars for all Deep Progression players

---

## Contact

For questions or issues, refer to the main project documentation or contact the development team.

