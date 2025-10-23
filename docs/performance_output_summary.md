# Performance Output Radar - Implementation Summary

## Overview

The Performance Output Radar is a complementary visualization to the Tactical Profile. While the Tactical Profile shows **how strikers play** (playing style and approach), the Performance Radar shows **what they produce** (actual output and ability).

## What Was Implemented

### 1. Real Artifact Generation Script
**File**: `scripts/generate_real_performance_artifacts.py`

- Fetches real player season stats from StatsBomb API
- Filters for Liga MX strikers with ≥600 minutes played
- Calculates 18 performance metrics across 5 axes
- Generates season-specific artifacts (2024/25, 2023/24, 2022/23, 2021/22)
- Computes percentiles and benchmarks per season

**Output**:
- 47 strikers in 2024/25
- 51 strikers in 2023/24
- 58 strikers in 2022/23
- 54 strikers in 2021/22

### 2. Performance Loader
**File**: `core/performance/loader.py`

- Loads and caches season-specific artifacts
- Handles both string and integer player ID lookups
- Provides methods for:
  - Getting axes definitions
  - Retrieving metric rows for players
  - Getting axis scores
  - Accessing benchmarks and min/max ranges

### 3. Performance Service
**File**: `core/performance/service.py`

- Builds performance profile payloads
- Validates striker eligibility
- Maps season strings to season IDs (2024/25 → 317, etc.)
- Provides human-readable metric labels
- Integrates with both generic and season-specific loaders

### 4. Performance Radar UI Component
**File**: `ui/components/performance_radar.py`

- Renders interactive performance radar chart
- Toggle between percentile (0-100) and absolute modes
- Shows metric details in expandable section
- Displays league benchmarks (median, p80)
- Includes player stats header (minutes, games, etc.)
- Warning badge for low minutes (<600)

### 5. Player Database Integration
**File**: `pages/2_Player_Database.py`

- Added performance profile tab alongside tactical profile
- Automatic season switching loads correct artifacts
- Season-specific data display

## Performance Axes (5 Axes, 18 Metrics)

### 1. Finishing Output
- Touches in Box /90
- NP xG /90
- xG / Shot
- PS xG – xG (Finishing Quality)

### 2. Chance Creation
- xA /90
- Key Passes /90
- OBV Pass /90
- xA / Key Pass

### 3. Ball Progression & Link Play
- Deep Progressions /90
- Passing Ratio
- Dribble Ratio
- OBV Dribble /90

### 4. Defensive Work Rate
- Defensive Actions /90
- Tackles & Interceptions /90
- Aerial Ratio

### 5. Overall Impact
- NP xG + xA /90
- OBV /90
- Positive Outcome Score

## Architecture

```
Player Database (pages/2_Player_Database.py)
    ↓
    ├─→ Tactical Profile Service (core/profiles/service.py)
    │   ├─→ Tactical Loader (core/profiles/loader.py)
    │   └─→ Tactical Radar UI (ui/components/radar.py)
    │
    └─→ Performance Service (core/performance/service.py)
        ├─→ Performance Loader (core/performance/loader.py)
        └─→ Performance Radar UI (ui/components/performance_radar.py)
```

## Key Features

1. **Season-Specific Data**
   - Each season has separate artifact directories
   - Percentiles calculated within-season (not across all seasons)
   - Benchmarks reflect league averages for that season

2. **Real Data from API**
   - All metrics sourced from StatsBomb API
   - 18 metrics across 5 axes
   - Precomputed artifacts for fast loading

3. **Flexible Season Mapping**
   - Same strategy as tactical profile
   - `_extract_season_id()` method maps season strings to IDs
   - Centralized season mapping

4. **Performance Optimization**
   - Artifacts loaded once and cached
   - <200ms response times for subsequent retrievals
   - No runtime API calls

5. **Data Quality**
   - 600 minutes minimum threshold
   - League-wide percentiles per season
   - Handles missing metrics gracefully

## Files Modified/Created

### Created Files
- `scripts/generate_real_performance_artifacts.py`
- `core/performance/loader.py`
- `core/performance/service.py`
- `ui/components/performance_radar.py`
- `scripts/test_real_performance_artifacts.py`
- `docs/how_to_generate_real_performance_artifacts.md`

### Modified Files
- `pages/2_Player_Database.py` - Added performance profile tab
- `core/performance/loader.py` - Fixed player ID type handling
- `core/performance/service.py` - Added season mapping

## Usage

### Generating Real Artifacts

```bash
python scripts/generate_real_performance_artifacts.py
```

### In Player Database

1. Select a striker
2. Click "View Tactical Profile"
3. Choose between tabs:
   - **🎯 Tactical Profile** - Playing style
   - **📊 Performance Profile** - Output metrics
4. Switch seasons to see season-specific data

### In Code

```python
from core.performance.service import get_performance_service

# Get service for specific season
service = get_performance_service(season_id="317")

# Build profile
profile = service.build_performance_profile(
    player_id="17299",
    player_name="Player Name",
    team_name="Team Name",
    primary_position="Centre Forward",
    season="2024/25",
    minutes=1200
)

# Render
from ui.components.performance_radar import render_performance_profile_panel
render_performance_profile_panel(profile)
```

## Data Directory Structure

```
data/processed/
├── performance_artifacts_317/  (2024/25)
│   ├── performance_axes.json
│   ├── performance_percentiles.parquet
│   ├── performance_axis_scores.parquet
│   ├── performance_benchmarks.json
│   ├── performance_minmax.json
│   ├── performance_config.json
│   └── performance_raw_metrics.parquet
├── performance_artifacts_281/  (2023/24)
├── performance_artifacts_235/  (2022/23)
└── performance_artifacts_108/  (2021/22)
```

## Troubleshooting

### Season mapping not found
- Ensure `_extract_season_id()` method is available in performance service
- Check that season strings match expected format (e.g., "2024/25")

### Player not found in artifacts
- Verify player has ≥600 minutes in selected season
- Some players may only appear in specific seasons

### Missing metrics
- Handled gracefully - excluded from axis score calculations
- Shown as "Insufficient data" in UI

## Next Steps

- Add performance comparison charts
- Export performance data
- Predictive models based on performance profiles
- Performance benchmarking reports
- Integration with scouting workflows
