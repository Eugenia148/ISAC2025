# Data Quality Report: Deep Progression Unit (All Seasons Combined)

## Cohort
- **Total Size:** 604 player-seasons
- **Seasons:** 4 seasons combined
  - Season 281: 158 player-seasons
  - Season 317: 157 player-seasons
  - Season 235: 147 player-seasons
  - Season 108: 142 player-seasons
- **Positions:** Wing Backs, Full Backs, Holding Midfielders, Central Midfielders
- **Minutes filter:** > 500

## Features
- **Base features:** 79
- **360 metrics:** Yes (coverage: 100.0%)
- **360 features added:** 7
- **Total features extracted:** 86
- **Features dropped:** 10
- **Final features for PCA:** 76

## Preprocessing
- **Missingness threshold:** >=30%
- **Winsorization:** [1.0%, 99.0%] percentiles
- **Normalization:** zscore
- **Collinearity threshold:** |r| >= 0.9

## PCA Results
- **Total components:** 76
- **Components for 80% variance:** 18
- **Components for 90% variance:** 29
- **Components for 95% variance:** 39

### Variance Explained by First 10 PCs
  - **PC1:** 19.83% (cumulative: 19.83%)
  - **PC2:** 14.10% (cumulative: 33.94%)
  - **PC3:** 11.65% (cumulative: 45.58%)
  - **PC4:** 4.69% (cumulative: 50.28%)
  - **PC5:** 4.36% (cumulative: 54.64%)
  - **PC6:** 3.91% (cumulative: 58.55%)
  - **PC7:** 2.93% (cumulative: 61.48%)
  - **PC8:** 2.63% (cumulative: 64.11%)
  - **PC9:** 2.40% (cumulative: 66.50%)
  - **PC10:** 2.16% (cumulative: 68.66%)

## Dropped Features
- **player_season_defensive_action_90:** Missing from data
- **player_season_xgbuildup_90:** Correlated with player_season_xgchain_90 (r=0.936)
- **player_season_lbp_90:** Correlated with player_season_lbp_completed_90 (r=0.900)
- **player_season_xa_90:** Correlated with player_season_op_xa_90 (r=0.931)
- **player_season_op_passes_90:** Correlated with player_season_carries_90 (r=0.910)
- **player_season_sp_xa_90:** Correlated with player_season_sp_key_passes_90 (r=0.941)
- **player_season_aggressive_actions_90:** Correlated with player_season_pressures_90 (r=0.923)
- **player_season_fhalf_pressures_ratio:** Correlated with player_season_average_x_pressure (r=0.949)
- **player_season_average_x_defensive_action:** Correlated with player_season_average_x_pressure (r=0.966)
- **player_season_lbp_received_90:** Correlated with player_season_fhalf_lbp_received_90 (r=0.922)
