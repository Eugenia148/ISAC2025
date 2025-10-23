"""
Check for players with data across multiple seasons.
"""

import pandas as pd

def check_multi_season_players():
    """Check which players have data for multiple seasons."""
    
    # Load the data
    df = pd.read_parquet('C:/Users/carls/OneDrive/Dokumente/Uni/05 Semester/Marketing y Estrategia de Deportes/Projekt/Repo/ISAC2025/data/processed/striker_artifacts/ability_scores.parquet')
    
    print(f"Total players in dataset: {len(df)}")
    
    # Count players by season
    player_counts = {}
    for idx in df.index:
        player_id = idx.split('_')[0]
        player_counts[player_id] = player_counts.get(player_id, 0) + 1
    
    # Find players with multiple seasons
    multi_season_players = {k: v for k, v in player_counts.items() if v > 1}
    
    print(f"Players with multiple seasons: {len(multi_season_players)}")
    
    if multi_season_players:
        print("\nSample multi-season players:")
        for player_id, count in list(multi_season_players.items())[:5]:
            print(f"  Player {player_id}: {count} seasons")
            
            # Show which seasons
            seasons = []
            for idx in df.index:
                if idx.startswith(f"{player_id}_"):
                    season = idx.split('_')[1]
                    seasons.append(season)
            print(f"    Seasons: {', '.join(seasons)}")
    
    return multi_season_players

if __name__ == "__main__":
    check_multi_season_players()
