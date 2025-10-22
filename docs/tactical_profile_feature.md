# Tactical Profile Feature

## Overview

The Tactical Profile feature provides radar chart visualization of striker abilities based on PCA analysis of tactical metrics. When a user selects a striker from the Player Database, they can view a detailed tactical profile showing the player's abilities across 6 key dimensions.

## Architecture

### Core Components

1. **`core/profiles/loader.py`** - Loads PCA artifacts and provides data access
2. **`core/profiles/service.py`** - Builds striker profile payloads for the UI
3. **`ui/components/radar.py`** - Renders radar charts and tactical profile panels

### Data Flow

1. **Artifacts Generation** - PCA analysis from notebook creates artifacts
2. **Data Loading** - Loader loads artifacts into memory
3. **Profile Building** - Service builds profile payloads for selected strikers
4. **UI Rendering** - Radar component renders interactive charts

## Ability Dimensions

The tactical profile analyzes strikers across 6 key dimensions:

1. **Progressive Play** - Ball progression & link play
2. **Finishing & Box Presence** - Goal scoring and box positioning
3. **Pressing Work Rate** - Defensive pressure and work rate
4. **Finishing Efficiency** - Shot conversion and efficiency
5. **Dribbling & Risk-Taking** - Ball carrying and risk taking
6. **Decision Making & Balance** - Decision making and balance

## Data Sources

### Artifacts (Required)

The system requires the following artifacts to be generated from the PCA analysis:

- `ability_axes.json` - Ability dimension definitions
- `ability_scores.parquet` - Raw PCA ability scores per player
- `ability_percentiles.parquet` - Percentile rankings per player
- `league_reference.json` - League average reference scores
- `axis_ranges.json` - Axis ranges for absolute mode rendering

### Player Data

- Player identity and attributes from StatsBomb API
- Position mapping for striker identification
- Season statistics for context

## Usage

### In Player Database

1. Navigate to the Player Database page
2. Select a striker from the table
3. Click "View Tactical Profile" button
4. View the radar chart and ability breakdown

### Display Modes

- **Percentiles (0-100)** - Shows player's percentile ranking vs. all Liga MX strikers
- **Absolute Scores** - Shows raw PCA ability scores (0-1 normalized)

### Features

- Interactive radar chart with hover tooltips
- League average overlay (percentile mode only)
- Detailed ability breakdown with color-coded metrics
- Responsive design for different screen sizes

## Implementation Details

### Striker Identification

Players are considered strikers if their primary or secondary position is:
- Centre Forward
- Left Centre Forward
- Right Centre Forward

### Data Processing

- PCA analysis performed offline from notebook
- Artifacts cached in memory for fast access
- Graceful fallbacks for missing data
- Error handling for edge cases

### Performance

- Artifacts loaded once at startup
- Profile building < 150ms after cache warm-up
- No live PCA computation at runtime
- Efficient data structures for fast lookups

## File Structure

```
core/
├── profiles/
│   ├── __init__.py
│   ├── loader.py          # Artifact loading and data access
│   └── service.py         # Profile building and striker detection

ui/
├── components/
│   ├── __init__.py
│   └── radar.py           # Radar chart rendering and UI components

data/
└── processed/
    └── striker_artifacts/ # PCA artifacts directory
        ├── ability_axes.json
        ├── ability_scores.parquet
        ├── ability_percentiles.parquet
        ├── league_reference.json
        └── axis_ranges.json

scripts/
├── generate_artifacts.py  # Artifact generation script
└── test_tactical_profile.py # System testing script
```

## Testing

Run the test script to validate the system:

```bash
python scripts/test_tactical_profile.py
```

## Future Enhancements

- Compare multiple players side-by-side
- Cluster-based comparisons (vs. cluster centroids)
- Historical trend analysis
- Export functionality for analysts
- Additional player positions (midfielders, defenders)

## Dependencies

- streamlit
- plotly
- pandas
- numpy
- scikit-learn (for PCA analysis)

## Notes

- Currently only supports strikers
- Requires PCA artifacts to be generated from notebook analysis
- Sample data provided for testing and demonstration
- Production use requires real PCA analysis from StatsBomb data
