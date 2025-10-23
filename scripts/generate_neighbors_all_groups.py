"""
Generate player_neighbors.parquet for Deep Progression and AM/W position groups.

Uses Euclidean distance on L2-normalized PCA vectors to find most similar players
based on playing style.
"""

import pandas as pd
import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from pathlib import Path


def generate_neighbors_for_group(artifacts_dir: str, top_k: int = 10):
    """
    Generate neighbor data using Euclidean distance on L2-normalized vectors.
    
    Args:
        artifacts_dir: Path to artifacts directory (e.g., "data/processed/deep_progression_artifacts")
        top_k: Number of neighbors to keep for each player
    """
    artifacts_path = Path(artifacts_dir)
    
    if not artifacts_path.exists():
        print(f"❌ Artifacts directory not found: {artifacts_dir}")
        return
    
    # Load ability_scores_l2.parquet (already L2-normalized)
    scores_path = artifacts_path / "ability_scores_l2.parquet"
    
    if not scores_path.exists():
        print(f"❌ ability_scores_l2.parquet not found in {artifacts_dir}")
        return
    
    scores_df = pd.read_parquet(scores_path)
    print(f"✓ Loaded {len(scores_df)} players from {scores_path}")
    
    # Extract PC columns (PC1, PC2, ..., PC7)
    pc_cols = [c for c in scores_df.columns if c.startswith('PC')]
    print(f"✓ Using {len(pc_cols)} PCA dimensions: {pc_cols}")
    
    vectors = scores_df[pc_cols].values
    player_season_ids = scores_df.index.tolist()
    
    print(f"🔍 Computing Euclidean distances for {len(player_season_ids)} players...")
    
    # Compute pairwise Euclidean distance
    distance_matrix = euclidean_distances(vectors)
    
    # Build neighbor records
    neighbors_list = []
    
    for i, anchor_id in enumerate(player_season_ids):
        # Get distances for this player (excluding self)
        distances = distance_matrix[i]
        
        # Get indices of top-K closest neighbors (lowest distance, excluding self at index i)
        neighbor_indices = np.argsort(distances)[1:top_k+1]
        
        for neighbor_idx in neighbor_indices:
            neighbor_id = player_season_ids[neighbor_idx]
            distance = distances[neighbor_idx]
            
            # Convert distance to similarity (0-1, where 0=far, 1=identical)
            # Using inverse: similarity = 1 / (1 + distance)
            similarity = 1.0 / (1.0 + distance)
            
            neighbors_list.append({
                'anchor_player_season_id': anchor_id,
                'neighbor_player_season_id': neighbor_id,
                'euclidean_distance': float(distance),
                'similarity': float(similarity)
            })
    
    # Save to parquet
    neighbors_df = pd.DataFrame(neighbors_list)
    output_path = artifacts_path / "player_neighbors.parquet"
    neighbors_df.to_parquet(output_path, index=False)
    
    print(f"✅ Generated {len(neighbors_df)} neighbor records for {len(player_season_ids)} players")
    print(f"✅ Saved to: {output_path}")
    
    # Show statistics
    avg_distance = neighbors_df['euclidean_distance'].mean()
    avg_similarity = neighbors_df['similarity'].mean()
    print(f"\n📊 Statistics:")
    print(f"   Average distance: {avg_distance:.4f}")
    print(f"   Average similarity: {avg_similarity:.4f} ({avg_similarity*100:.1f}%)")
    print(f"   Distance range: [{neighbors_df['euclidean_distance'].min():.4f}, {neighbors_df['euclidean_distance'].max():.4f}]")


def main():
    """Generate neighbor data for all position groups."""
    
    print("=" * 80)
    print("Generating Similar Players Data (Euclidean Distance on L2 Vectors)")
    print("=" * 80)
    
    # Deep Progression Unit
    print("\n🎯 Deep Progression Unit")
    print("-" * 80)
    generate_neighbors_for_group("data/processed/deep_progression_artifacts", top_k=10)
    
    # Attacking Midfielders & Wingers
    print("\n🎯 Attacking Midfielders & Wingers")
    print("-" * 80)
    generate_neighbors_for_group("data/processed/attacking_midfielders_wingers_artifacts", top_k=10)
    
    print("\n" + "=" * 80)
    print("✅ All neighbor data generated successfully!")
    print("=" * 80)


if __name__ == "__main__":
    main()

