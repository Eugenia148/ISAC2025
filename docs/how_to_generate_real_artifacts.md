# How to Generate Real Tactical Profile Artifacts

## Overview

To get real tactical profiles with actual player data instead of sample data, you need to extract the results from your striker PCA clustering notebook and generate the required artifacts.

## Step-by-Step Process

### Step 1: Complete Your PCA Analysis

1. **Open your striker PCA notebook**: `notebooks/striker_pca_clustering.ipynb`
2. **Run all cells** to complete the PCA analysis
3. **Ensure you have these variables** in your notebook:
   - `ability_df_norm` - Normalized ability scores DataFrame
   - `striker_features_scaled_df` - Features DataFrame with player_season_id index
   - `pca` - Fitted PCA object

### Step 2: Generate Real Artifacts

**Option A: Use the Integration Template**

1. **Copy the code** from `notebook_integration_template.py`
2. **Add it to the end** of your striker PCA notebook
3. **Run the cell** to generate artifacts

**Option B: Run the Extraction Script**

1. **Run the extraction script**:
   ```bash
   python scripts/extract_real_artifacts.py
   ```
2. **Choose option 2** to create the integration template
3. **Copy the generated code** to your notebook

### Step 3: Verify the Artifacts

After running the code, you should have these files in `data/processed/striker_artifacts/`:

- ✅ `ability_axes.json` - Ability dimension definitions
- ✅ `ability_scores.parquet` - Real PCA ability scores per player
- ✅ `ability_percentiles.parquet` - Real percentile rankings per player
- ✅ `league_reference.json` - Real league average reference scores
- ✅ `axis_ranges.json` - Real axis ranges for absolute mode

### Step 4: Test the System

1. **Run the test script**:
   ```bash
   python scripts/test_tactical_profile.py
   ```
2. **Check that real data** is loaded instead of sample data
3. **Verify player IDs** match your actual data

## What the Code Does

The integration template code:

1. **Creates the artifacts directory** if it doesn't exist
2. **Saves ability axes** definitions (same as before)
3. **Saves normalized ability scores** from your PCA analysis
4. **Calculates percentiles** for each player vs. the striker pool
5. **Generates league reference** (median values across all strikers)
6. **Calculates axis ranges** (min/max values for absolute mode)

## Expected Output

After running the code, you should see:

```
Generating tactical profile artifacts from PCA analysis...
Generated artifacts for 279 strikers
Artifacts saved to: data/processed/striker_artifacts
```

## Data Structure

Your real artifacts will contain:

### Player IDs
- Format: `{player_id}_{season_id}` (e.g., `12345_317`)
- Matches the `player_season_id` from your notebook

### Ability Scores
- Normalized values (0-1) from your PCA analysis
- 6 dimensions per player

### Percentiles
- Calculated as percentile rank within the striker pool
- Values 0-100 representing relative performance

### League Reference
- Median values across all strikers
- Used as baseline for comparisons

## Troubleshooting

### If you get errors:

1. **Check that your notebook variables exist**:
   - `ability_df_norm` should be defined
   - `striker_features_scaled_df` should have the right index

2. **Verify the data structure**:
   - Player IDs should be in the index
   - Ability scores should be normalized (0-1)

3. **Check file permissions**:
   - Make sure you can write to the artifacts directory

### If you see sample data instead of real data:

1. **Verify the artifacts were generated** correctly
2. **Check that the file paths** are correct
3. **Restart your Streamlit app** to reload the artifacts

## Next Steps

Once you have real artifacts:

1. **Test the Player Database** - Select a striker and view their tactical profile
2. **Verify the data** - Check that the scores and percentiles look reasonable
3. **Customize the display** - Adjust the radar chart settings if needed

## Files Created

- `notebook_integration_template.py` - Code to add to your notebook
- `scripts/extract_real_artifacts.py` - Extraction script
- `docs/how_to_generate_real_artifacts.md` - This guide

The tactical profile system will automatically use the real data once the artifacts are generated!
