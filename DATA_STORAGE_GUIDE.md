# Liga MX Data Storage & Analysis Guide

This guide explains how to efficiently download, store, and analyze Liga MX data from StatsBomb for faster offline analysis.

## 🏗️ Project Structure

```
ISAC2025/
├── data/
│   ├── raw/ligamx/              # Raw downloaded data (JSON)
│   │   ├── season_317/          # 2024/2025 season
│   │   ├── season_281/          # 2023/2024 season
│   │   ├── season_235/          # 2022/2023 season
│   │   └── season_108/          # 2021/2022 season
│   ├── processed/ligamx/        # Processed data (for future use)
│   └── exports/ligamx/          # CSV exports for external tools
├── src/
│   ├── data_loader.py           # Download and cache data
│   ├── data_analyzer.py         # Load and analyze cached data
│   └── pull_data.ipynb         # Your original notebook
├── notebooks/
│   └── data_analysis_example.ipynb  # Example analysis notebook
└── requirements.txt
```

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Set Up Credentials (Optional)
Create a `.env` file in your project root:
```
SB_USERNAME=your_statsbomb_username
SB_PASSWORD=your_statsbomb_password
```

*Note: Credentials are optional for most Liga MX data, but recommended for premium datasets.*

### 3. Download Data
```bash
python src/data_loader.py
```

Choose option 1 to download all seasons, or option 2 for a specific season.

### 4. Analyze Data
```bash
python src/data_analyzer.py
```

Or open the example notebook: `notebooks/data_analysis_example.ipynb`

## 📊 Available Data

### Liga MX Seasons
- **2024/2025** (Season ID: 317)
- **2023/2024** (Season ID: 281) 
- **2022/2023** (Season ID: 235)
- **2021/2022** (Season ID: 108)

### Data Types per Match
- **Matches**: Basic match information (teams, scores, dates)
- **Events**: Detailed event data (passes, shots, fouls, etc.)
- **Lineups**: Starting lineups and substitutions

## 🔧 Usage Examples

### Load Match Data
```python
from src.data_analyzer import LigaMXAnalyzer

analyzer = LigaMXAnalyzer()
matches = analyzer.load_matches(season_id=281)  # 2023/2024
print(f"Loaded {len(matches)} matches")
```

### Load Events Data
```python
# Load all events for a season
events = analyzer.combine_events_by_season(season_id=281)

# Load events for a specific match
events = analyzer.load_events(season_id=281, match_id=12345)
```

### Get Team Performance
```python
team_matches = analyzer.get_team_matches(season_id=281, team_name="Club América")
```

### Export to CSV
```python
analyzer.export_to_csv(season_id=281)
# Creates CSV files in data/exports/ligamx/
```

## 💾 Data Storage Strategy

### Why Offline Storage?
- **Speed**: No API calls during analysis
- **Reliability**: Work offline without internet
- **Consistency**: Same data across analysis sessions
- **Cost**: Reduce API usage if you have rate limits

### Caching Logic
- Files are only downloaded if they don't exist
- Partial downloads can be resumed
- JSON format preserves all original data structure
- Easy to backup and share

### File Organization
```
data/raw/ligamx/season_281/
├── matches.json           # All matches for the season
├── events_12345.json      # Events for match 12345
├── events_12346.json      # Events for match 12346
├── lineups_12345.json     # Lineups for match 12345
└── lineups_12346.json     # Lineups for match 12346
```

## 📈 Performance Benefits

### Before (API calls)
- Each analysis requires API calls
- ~2-5 seconds per match for events
- Risk of rate limiting
- Requires internet connection

### After (Cached data)
- Instant data loading
- ~0.1 seconds to load all season data
- No rate limiting concerns
- Works offline

## 🛠️ Advanced Usage

### Custom Analysis
```python
# Load data
analyzer = LigaMXAnalyzer()
matches = analyzer.load_matches(281)
events = analyzer.combine_events_by_season(281)

# Your custom analysis here
# ...

# Export results
analyzer.export_to_csv(281)
```

### Multiple Seasons Comparison
```python
seasons = [317, 281, 235, 108]  # All available seasons
all_data = {}

for season_id in seasons:
    if analyzer.check_season_exists(season_id):
        all_data[season_id] = analyzer.load_matches(season_id)

# Compare seasons
# ...
```

## 🔍 Data Quality & Validation

### Built-in Checks
- File existence validation
- Data completeness reports
- Error handling for missing data
- Summary statistics

### Manual Verification
```python
# Check data summary
summary = analyzer.get_all_seasons_summary()
print(summary)

# Get detailed season info
season_info = analyzer.get_season_summary(281)
print(season_info)
```

## 🚨 Troubleshooting

### Common Issues

**"No data found"**
- Run `python src/data_loader.py` first
- Check if `.env` file has correct credentials

**"File not found" errors**
- Verify data was downloaded successfully
- Check file paths in `data/raw/ligamx/`

**Memory issues with events data**
- Load specific matches instead of entire season
- Use CSV exports for large datasets

### Data Recovery
If downloads are interrupted:
1. Re-run the data loader
2. It will skip existing files and continue
3. Check the summary report for completeness

## 📚 Next Steps

1. **Explore the example notebook** (`notebooks/data_analysis_example.ipynb`)
2. **Run your own analysis** using the cached data
3. **Export data** for use in other tools (Tableau, Power BI, etc.)
4. **Create visualizations** with the processed data
5. **Build predictive models** using the rich event data

## 🤝 Contributing

To extend this system:
- Add new data sources in `data_loader.py`
- Create new analysis functions in `data_analyzer.py`
- Share useful analysis patterns in notebooks

---

**Happy analyzing! 🎉**
