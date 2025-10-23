# Cell 20 — SAVE ROLE ARTIFACTS (CORRECT APPROACH)

**Replace Cell 20 with this code:**

```python
# Prepare data for artifact saving - use already-computed PCA/GMM
# Just format the data with season information

# Make sure striker_stats_filtered has the season_id column
if 'season_id' not in striker_stats_filtered.columns:
    print("ERROR: striker_stats_filtered missing 'season_id' column")
else:
    print(f"Saving role artifacts from pre-computed PCA/GMM results...")
    print(f"Total strikers: {len(striker_stats_filtered)}")
    print(f"PCA vectors shape: {X_pca.shape}")
    print(f"GMM assignments shape: {assignments.shape}\n")
    
    # Call the save function with your already-computed results
    save_role_artifacts(
        pca_vectors=X_pca,                    # Your 6D PCA vectors
        gmm_model=gmm,                        # Your fitted GMM
        posteriors=posteriors,                # Your GMM posteriors
        assignments=assignments,              # Your cluster assignments
        striker_df_with_season=striker_stats_filtered,  # Data with season_id
        artifacts_root="data/processed/roles"
    )
    
    print("\n" + "="*60)
    print("✅ ROLE ARTIFACTS SAVED SUCCESSFULLY!")
    print("="*60)
```

That's it! This code:
- ✅ Uses your existing `X_pca` (already computed)
- ✅ Uses your existing `gmm` model (already fitted)
- ✅ Uses your existing `posteriors` and `assignments` (already computed)
- ✅ Automatically handles all 4 seasons
- ✅ Saves to `data/processed/roles/`

No recomputation needed!
