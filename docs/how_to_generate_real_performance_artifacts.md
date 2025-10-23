# How to Generate Real Performance Artifacts

This guide explains how to generate and use real performance output artifacts from StatsBomb API data.

## Overview

The Performance Output radar shows striker performance metrics across 5 axes with actual data from Liga MX matches:

- **Finishing Output** - Goal scoring and finishing quality
- **Chance Creation** - Creating scoring opportunities  
- **Ball Progression & Link Play** - Ball progression and link-up play
- **Defensive Work Rate** - Defensive contributions and work rate
- **Overall Impact** - Overall performance and impact

## Artifacts Generated

For each season, the following artifacts are created:

### Directory Structure
```
data/processed/
├── performance_artifacts_317/  (2024/25)
├── performance_artifacts_281/  (2023/24)
├── performance_artifacts_235/  (2022/23)
└── performance_artifacts_108/  (2021/22)
```

### Artifacts per Season

1. **performance_axes.json** - Axis definitions with metrics
2. **performance_percentiles.parquet** - Per-player percentile scores for all metrics
3. **performance_axis_scores.parquet** - Per-player axis scores (0-100)
4. **performance_benchmarks.json** - League median and p80 for each metric
5. **performance_minmax.json** - Min/max ranges for absolute view scaling
6. **performance_config.json** - Configuration (minutes threshold, season info, striker count)
7. **performance_raw_metrics.parquet** - Raw metric values for debugging

## Generating Real Artifacts

### Prerequisites

1. StatsBomb API credentials (.env file with SB_USERNAME and SB_PASSWORD)
2. Python environment with required packages (pandas, numpy, statsbombpy)

### Run the Script

```bash
python scripts/generate_real_performance_artifacts.py
```

This will:
1. Fetch player season stats from StatsBomb API for all 4 seasons
2. Filter for strikers with ≥600 minutes played
3. Calculate 18 performance metrics
4. Compute percentiles against the striker pool for each season
5. Calculate league benchmarks (median, p80)
6. Save season-specific artifacts

### Output

```
Generating Performance Output artifacts with real data...
StatsBomb client initialized with credentials: ita***
Generating Performance Output artifacts for 2024/25...
Fetched 636 player records for 2024/25
Found 47 strikers with >= 600 minutes
Generated artifacts for 47 strikers in 2024/25
Artifacts saved to: data\processed\performance_artifacts_317
Generated 5 performance axes with 18 total metrics

... (repeated for other seasons)

Completed: 4/4 seasons processed successfully
```

## Performance Metrics

### Finishing Output (4 metrics)
- `touches_inside_box_90` - Touches in the box per 90 minutes
- `np_xg_90` - Non-penalty expected goals per 90 minutes
- `np_xg_per_shot` - Expected goals per shot (quality of shots)
- `finishing_quality` - Derived from `np_psxg_90 - np_xg_90` (Post-shot xG advantage)

### Chance Creation (4 metrics)
- `xa_90` - Expected assists per 90 minutes
- `key_passes_90` - Key passes per 90 minutes
- `obv_pass_90` - Offensive box touches value from passes per 90
- `xa_per_shot_assist` - Derived from `xa_90 / key_passes_90`

### Ball Progression & Link Play (4 metrics)
- `deep_progressions_90` - Deep progressions per 90 minutes
- `passing_ratio` - Successful passes ratio
- `dribble_ratio` - Successful dribbles ratio
- `obv_dribble_carry_90` - Offensive box touches value from dribbles per 90

### Defensive Work Rate (3 metrics)
- `defensive_actions_90` - Defensive actions per 90 minutes
- `tackles_and_interceptions_90` - Tackles and interceptions per 90
- `aerial_ratio` - Aerial duel win ratio

### Overall Impact (3 metrics)
- `npxgxa_90` - Non-penalty xG + xA per 90 minutes
- `obv_90` - Offensive box touches value per 90 minutes
- `positive_outcome_score` - Positive outcome score

## Season IDs

- 2024/25: `317`
- 2023/24: `281`
- 2022/23: `235`
- 2021/22: `108`

## Integration in Player Database

When selecting a striker in the Player Database:

1. A **Tactical Profile** tab shows playing style (from PCA analysis)
2. A **Performance Profile** tab shows actual output (from real data)

The app automatically loads the correct season's artifacts based on the selected season.

### Usage in Code

```python
from core.performance.service import get_performance_service

# Get service for a specific season
service = get_performance_service(season_id="317")  # 2024/25

# Build performance profile
profile = service.build_performance_profile(
    player_id="17299",
    player_name="Player Name",
    team_name="Team Name",
    primary_position="Centre Forward",
    season="2024/25",
    minutes=1200
)

# Use profile with UI component
from ui.components.performance_radar import render_performance_profile_panel
render_performance_profile_panel(profile)
```

## Data Quality

- **Minutes Threshold**: 600 minutes minimum for inclusion
- **Pool**: All Liga MX strikers meeting the minutes threshold
- **Percentiles**: Calculated per season (not across all seasons)
- **Benchmarks**: Median and p80 per season

### Striker Count by Season
- 2024/25: 47 strikers
- 2023/24: 51 strikers
- 2022/23: 58 strikers
- 2021/22: 54 strikers

## Troubleshooting

### No credentials error
Ensure you have a `.env` file with:
```
SB_USERNAME=your_username
SB_PASSWORD=your_password
```

### Missing metrics
Some players may have missing metrics (null values). These are:
- Handled gracefully in the loader
- Excluded from axis score calculations
- Shown as "Insufficient data" in the UI

### Regenerating Artifacts

To regenerate artifacts (e.g., after updating the script):

```bash
# Remove old artifacts
rm -r data/processed/performance_artifacts_*

# Re-generate
python scripts/generate_real_performance_artifacts.py
```

## Performance Optimization

- Artifacts are loaded once and cached in memory
- Subsequent player profile retrievals are <200ms
- No API calls made at runtime (all data pre-computed)

## Next Steps

- Display performance comparison charts
- Add predictive models based on performance profiles
- Export performance data for analysis
- Create performance benchmarking reports
