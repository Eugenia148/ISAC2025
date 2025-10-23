# Data Quality Report: Deep Progression Unit (All Seasons Combined)

## Cohort
- **Total Size:** 314 player-seasons
- **Seasons:** 4 seasons combined
  - Season 317: 83 player-seasons
  - Season 235: 79 player-seasons
  - Season 281: 79 player-seasons
  - Season 108: 73 player-seasons
- **Positions:** Wing Backs, Full Backs, Holding Midfielders, Central Midfielders
- **Minutes filter:** > 500

## Features
- **Base features:** 79
- **360 metrics:** Yes (coverage: 100.0%)
- **360 features added:** 7
- **Total features extracted:** 86
- **Features dropped:** 11
- **Final features for PCA:** 75

## Preprocessing
- **Missingness threshold:** >=30%
- **Winsorization:** [1.0%, 99.0%] percentiles
- **Normalization:** zscore
- **Collinearity threshold:** |r| >= 0.9

## PCA Results
- **Total components:** 75
- **Components for 80% variance:** 17
- **Components for 90% variance:** 28
- **Components for 95% variance:** 37

### Variance Explained by First 10 PCs
  - **PC1:** 22.47% (cumulative: 22.47%)
  - **PC2:** 14.56% (cumulative: 37.02%)
  - **PC3:** 7.16% (cumulative: 44.18%)
  - **PC4:** 6.52% (cumulative: 50.70%)
  - **PC5:** 4.19% (cumulative: 54.89%)
  - **PC6:** 3.40% (cumulative: 58.29%)
  - **PC7:** 3.11% (cumulative: 61.40%)
  - **PC8:** 2.84% (cumulative: 64.24%)
  - **PC9:** 2.54% (cumulative: 66.78%)
  - **PC10:** 2.21% (cumulative: 68.99%)

## Dropped Features
- **player_season_defensive_action_90:** Missing from data
- **player_season_xgbuildup_90:** Correlated with player_season_xgchain_90 (r=0.930)
- **player_season_lbp_90:** Correlated with player_season_lbp_completed_90 (r=0.945)
- **player_season_xa_90:** Correlated with player_season_op_xa_90 (r=0.926)
- **player_season_op_passes_90:** Correlated with player_season_carries_90 (r=0.911)
- **player_season_sp_xa_90:** Correlated with player_season_sp_key_passes_90 (r=0.954)
- **player_season_sp_key_passes_90:** Correlated with player_season_sp_passes_into_box_90 (r=0.966)
- **player_season_fhalf_pressures_ratio:** Correlated with player_season_average_x_defensive_action (r=0.936)
- **player_season_average_x_defensive_action:** Correlated with player_season_average_x_pressure (r=0.972)
- **player_season_lbp_received_90:** Correlated with player_season_fhalf_lbp_received_90 (r=0.954)
- **player_season_fhalf_lbp_received_90:** Correlated with player_season_f3_lbp_received_90 (r=0.948)
