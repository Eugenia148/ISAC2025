import sys
import os
sys.path.insert(0, os.getcwd())

import pickle
import pandas as pd
import json

# Load PCA model
with open('data/processed/roles/317/pca_model.pkl', 'rb') as f:
    pca_model = pickle.load(f)

# Load features
with open('data/processed/roles/317/features.json', 'r') as f:
    features = json.load(f)['features']

print("=" * 100)
print("PCA LOADINGS - Which features contribute most to each PC")
print("=" * 100)

# Create loadings dataframe
loadings = pd.DataFrame(
    pca_model.components_.T,
    columns=[f'PC{i+1}' for i in range(pca_model.n_components_)],
    index=features
)

print("\nPCA Loadings Matrix (absolute values):")
print(loadings.abs())

print("\n\n" + "=" * 100)
print("TOP CONTRIBUTORS TO EACH PC (Absolute Loading)")
print("=" * 100)

for i in range(pca_model.n_components_):
    pc = f'PC{i+1}'
    print(f"\n🔹 {pc} (Explains {pca_model.explained_variance_ratio_[i]*100:.1f}% of variance)")
    print("-" * 100)
    
    # Get top positive and negative
    top_positive = loadings[pc].nlargest(3)
    top_negative = loadings[pc].nsmallest(3)
    
    print(f"  TOP POSITIVE (PC increases with these):")
    for feat, load in top_positive.items():
        print(f"    {feat:45s}: +{load:.3f}")
    
    print(f"  TOP NEGATIVE (PC decreases with these):")
    for feat, load in top_negative.items():
        print(f"    {feat:45s}: {load:.3f}")

print("\n\n" + "=" * 100)
print("INTERPRETATION")
print("=" * 100)
print("""
Low PC1 (negative) = High on features with negative loadings
High PC1 (positive) = High on features with positive loadings

Cluster 2 (Poacher) has HIGH PC1 → High on positive PC1 features
Cluster 0 & 1 have LOW PC1 → Low on positive PC1 features
""")
