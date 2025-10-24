"""
Add player metadata (names, teams, positions) to ability_scores_l2.parquet files.

This script fetches player data from the API once and adds it to the existing
parquet files to avoid repeated API calls during similarity searches.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

import pandas as pd
from api.client import client


def add_metadata_to_artifacts(artifacts_dir: str):
    """Add player metadata to ability_scores_l2.parquet in the given artifacts directory."""
    
    artifacts_path = Path(artifacts_dir)
    scores_path = artifacts_path / "ability_scores_l2.parquet"
    
    if not scores_path.exists():
        print(f"❌ {scores_path} not found")
        return
    
    # Load existing scores
    scores_df = pd.read_parquet(scores_path)
    print(f"✓ Loaded {len(scores_df)} players from {scores_path}")
    
    # Check if metadata already exists and is populated
    if 'player_name' in scores_df.columns:
        # Check if it's actually populated (not just player_season_ids)
        sample_name = scores_df['player_name'].iloc[0] if len(scores_df) > 0 else None
        if sample_name and not sample_name.startswith(str(scores_df.index[0])):
            print(f"⚠️  Metadata already populated in {artifacts_dir}")
            return
        else:
            print(f"  Metadata columns exist but not populated, regenerating...")
            scores_df = scores_df.drop(columns=['player_name', 'team_name', 'primary_position'], errors='ignore')
    
    # Season mapping
    season_map = {317: (73, 317), 281: (73, 281), 235: (73, 235), 108: (73, 108)}
    
    # Fetch player data for all seasons
    all_player_data = {}
    
    for season_id, (comp_id, s_id) in season_map.items():
        print(f"  Fetching data for season {season_id}...")
        try:
            stats_df = client.player_season_stats(competition_id=comp_id, season_id=s_id)
            
            # API returns a DataFrame
            for _, stat in stats_df.iterrows():
                player_id = stat.get('player_id')
                if player_id:
                    player_season_id = f"{int(player_id)}_{season_id}"
                    all_player_data[player_season_id] = {
                        'player_name': stat.get('player_name', f'Player {int(player_id)}'),
                        'team_name': stat.get('team_name', '—'),
                        'primary_position': stat.get('primary_position', '—')
                    }
        except Exception as e:
            print(f"    Error fetching season {season_id}: {e}")
            import traceback
            traceback.print_exc()
    
    print(f"✓ Fetched metadata for {len(all_player_data)} player-seasons")
    
    # Add metadata columns
    scores_df['player_name'] = scores_df.index.map(
        lambda x: all_player_data.get(x, {}).get('player_name', x)
    )
    scores_df['team_name'] = scores_df.index.map(
        lambda x: all_player_data.get(x, {}).get('team_name', '—')
    )
    scores_df['primary_position'] = scores_df.index.map(
        lambda x: all_player_data.get(x, {}).get('primary_position', '—')
    )
    
    # Save updated parquet
    scores_df.to_parquet(scores_path)
    print(f"✅ Updated {scores_path} with metadata")
    print(f"   Columns: {scores_df.columns.tolist()}")


def main():
    """Add metadata to all position group artifacts."""
    
    print("=" * 80)
    print("Adding Player Metadata to Artifacts")
    print("=" * 80)
    
    # Deep Progression Unit
    print("\n🎯 Deep Progression Unit")
    print("-" * 80)
    add_metadata_to_artifacts("data/processed/deep_progression_artifacts")
    
    # Attacking Midfielders & Wingers
    print("\n🎯 Attacking Midfielders & Wingers")
    print("-" * 80)
    add_metadata_to_artifacts("data/processed/attacking_midfielders_wingers_artifacts")
    
    print("\n" + "=" * 80)
    print("✅ All metadata added successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()

