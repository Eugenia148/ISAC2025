stats that are relevant to strikers:

striker_columns = [
    # Identifiers
    "player_id", "player_name",
    
    # Outcome / Finishing
    "player_season_goals_90", "player_season_npg_90", "player_season_np_xg_90",
    "player_season_np_xg_per_shot", "player_season_conversion_ratio",
    "player_season_shot_on_target_ratio", "player_season_np_psxg_90",
    "player_season_npga_90", "player_season_npxgxa_90", "player_season_obv_shot_90",

    # Shot profile
    "player_season_np_shots_90", "player_season_carries_90", "player_season_carry_length",
    "player_season_total_dribbles_90", "player_season_dribbles_90", "player_season_failed_dribbles_90",

    # Box presence & off-ball movement
    "player_season_touches_inside_box_90", "player_season_passes_into_box_90",
    "player_season_op_passes_into_box_90", "player_season_op_passes_into_and_touches_inside_box_90",

    # Chance creation & link-up
    "player_season_xa_90", "player_season_op_xa_90", "player_season_sp_xa_90",
    "player_season_key_passes_90", "player_season_op_key_passes_90", "player_season_sp_key_passes_90",
    "player_season_through_balls_90", "player_season_xgbuildup_90", "player_season_xgchain_90",
    "player_season_obv_pass_90",

    # Ball progression & 1v1
    "player_season_deep_progressions_90", "player_season_deep_completions_90",
    "player_season_dribble_ratio", "player_season_turnovers_90", "player_season_dispossessions_90",

    # Aerial & physical presence
    "player_season_aerial_wins_90", "player_season_aerial_ratio",

    # Defensive work & pressing
    "player_season_pressures_90", "player_season_padj_pressures_90",
    "player_season_counterpressures_90", "player_season_pressure_regains_90",
    "player_season_counterpressure_regains_90", "player_season_fhalf_pressures_90",
    "player_season_fhalf_counterpressures_90", "player_season_tackles_90",
    "player_season_interceptions_90", "player_season_tackles_and_interceptions_90",
    "player_season_defensive_action_90",

    # Set pieces & fouls
    "player_season_sp_passes_into_box_90", "player_season_sp_key_passes_90",
    "player_season_penalty_wins_90", "player_season_fouls_90", "player_season_fouls_won_90",

    # Passing directionality (for link-up style)
    "player_season_passing_ratio", "player_season_pressured_passing_ratio",
    "player_season_passes_pressed_ratio", "player_season_forward_pass_proportion",
    "player_season_sideways_pass_proportion", "player_season_backward_pass_proportion",
    "player_season_op_f3_forward_pass_proportion", "player_season_op_f3_sideways_pass_proportion",
    "player_season_op_f3_backward_pass_proportion", "player_season_lbp_90",
    "player_season_lbp_completed_90", "player_season_lbp_ratio", "player_season_obv_lbp_90",
    "player_season_crosses_90", "player_season_crossing_ratio", "player_season_box_cross_ratio",

    # Baselines
    "player_season_minutes", "player_season_90s_played"
]


categories for stats:
    Finishi