import os
import json

# New mapping based on PCA analysis
NEW_CLUSTER_TO_ROLE = {
    "0": "Balanced Striker",
    "1": "Poacher",
    "2": "Creator / Pressing Striker"
}

NEW_ROLE_DESCRIPTIONS = {
    "Balanced Striker": "Versatile striker with moderate pressing and finishing, limited link play.",
    "Poacher": "Pure finisher focused on box occupation and scoring, limited pressing and playmaking.",
    "Creator / Pressing Striker": "High-intensity pressing striker combining excellent playmaking and ball progression with strong defensive engagement."
}

# Update all season directories
artifacts_root = "data/processed/roles"

for season_dir in os.listdir(artifacts_root):
    season_path = os.path.join(artifacts_root, season_dir)
    
    if not os.path.isdir(season_path):
        continue
    
    try:
        season_id = int(season_dir)
    except ValueError:
        continue
    
    # Update cluster_to_role.json
    cluster_role_path = os.path.join(season_path, "cluster_to_role.json")
    with open(cluster_role_path, 'w') as f:
        json.dump(NEW_CLUSTER_TO_ROLE, f, indent=2)
    print(f"✓ Updated cluster_to_role.json for season {season_id}")
    
    # Update role_descriptions.json
    role_desc_path = os.path.join(season_path, "role_descriptions.json")
    with open(role_desc_path, 'w') as f:
        json.dump(NEW_ROLE_DESCRIPTIONS, f, indent=2)
    print(f"✓ Updated role_descriptions.json for season {season_id}")

# CREATE global config.json at root
config = {
    "cluster_to_role": NEW_CLUSTER_TO_ROLE,
    "role_descriptions": NEW_ROLE_DESCRIPTIONS,
    "minutes_threshold": 500,
    "n_components_pca": 6,
    "n_clusters_gmm": 3,
    "top_k_neighbors": 10
}

config_path = os.path.join(artifacts_root, "config.json")
with open(config_path, 'w') as f:
    json.dump(config, f, indent=2)
print(f"✓ Created global config.json")

print("\n✅ All cluster names have been updated!")
print("\nNew mapping:")
for cluster_id, role_name in NEW_CLUSTER_TO_ROLE.items():
    print(f"  Cluster {cluster_id}: {role_name}")
    print(f"    {NEW_ROLE_DESCRIPTIONS[role_name]}\n")
