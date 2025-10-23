import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

import pandas as pd
from core.roles.service import get_role_service

# Load sample data
df = pd.read_parquet('data/processed/roles/317/player_style_vectors.parquet')
print('Sample players from 317:')
print(df[['player_id', 'player_name']].head(10))
print(f'\nData type of player_id: {df["player_id"].dtype}\n')

# Test with a few player IDs
service = get_role_service()

for idx, row in df.head(3).iterrows():
    player_id = row['player_id']
    player_name = row['player_name']
    print(f'\nTesting player_id: {player_id} ({type(player_id).__name__}) - {player_name}')
    
    similar = service.get_similar_players(player_id, 317, k=3)
    print(f'  Found {len(similar)} similar players')
    if similar:
        for s in similar:
            print(f'    - {s["player_name"]} ({s["similarity"]}% similar)')
    else:
        print('  No similar players found')
