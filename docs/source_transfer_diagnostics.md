# Source Transfer Diagnostics

## Plain-English Summary
This report compares each imported source against the combined training set and highlights why source-holdout transfer is weak. It does not weaken gates or mark any model production-ready.

## Source Summary
| Source | Rows | Date Range | Final-Test Rows | Drift Grade | Hardest Failing Models |
|---|---:|---|---:|---|---|
| mdabbert_ultimate | 7190 | 2010-03-21 to 2026-04-04 | 1210 | medium drift | fight_duration_model, finish_model, goes_distance_model |
| ufc_1994_2025 | 16674 | 1994-03-11 to 2025-09-06 | 922 | high drift | strike_volume_model, takedown_control_model, finish_in_round_1_model |
| ufc_1994_2026 | 8551 | 1994-03-11 to 2026-03-07 | 1164 | high drift | winner_model, fight_duration_model, finish_model |
| ufc_fight_forecast | 8231 | 1994-03-11 to 2025-10-04 | 955 | medium drift | winner_model, fight_duration_model, over_1_5_model |
| ufc_stats_complete | 8709 | 1993-11-12 to 2026-05-16 | 1286 | high drift | strike_volume_model, takedown_control_model |

## UFCStats Complete Answer
- present: True
- likely_failure_mode: ['source-holdout regression', 'missing or sparse labels', 'high missingness/stat distribution drift', 'models trained on other sources do not transfer cleanly to this source']
- is_noisy: True
- label_difference_suspected: False
- normalization_issue_suspected: True
- duplicate_issue_suspected: True
- target_definition_difference_suspected: False

## Source Details
### mdabbert_ultimate
- Root causes: missing or sparse labels, high missingness/stat distribution drift
- Target coverage: `{"winner_model": 7169, "fight_duration_model": 7169, "finish_model": 7169, "goes_distance_model": 7169, "over_1_5_model": 6737, "over_2_5_model": 6737, "ends_before_round_3_model": 6737, "finish_in_round_1_model": 6737, "finish_type_model": 3741, "method_umbrella_model": 7169, "method_model": 7169, "strike_volume_model": 0, "takedown_control_model": 0}`
- Missingness by feature group: `{"profile": 0.8182, "record": 0.1193, "recent_form": 0.6508, "elo": 0.5, "striking": 1.0, "grappling": 1.0, "style": 0.0092, "opponent_weakness": 0.0093, "size_context": 0.0, "data_quality": 0.0}`

### ufc_1994_2025
- Root causes: missing or sparse labels, high missingness/stat distribution drift
- Target coverage: `{"winner_model": 8190, "fight_duration_model": 8190, "finish_model": 8190, "goes_distance_model": 8190, "over_1_5_model": 8190, "over_2_5_model": 8190, "ends_before_round_3_model": 8190, "finish_in_round_1_model": 8190, "finish_type_model": 4361, "method_umbrella_model": 8190, "method_model": 8190, "strike_volume_model": 16632, "takedown_control_model": 16632}`
- Missingness by feature group: `{"profile": 0.8182, "record": 0.0945, "recent_form": 0.7537, "elo": 0.5, "striking": 1.0, "grappling": 1.0, "style": 0.0, "opponent_weakness": 0.0218, "size_context": 0.0026, "data_quality": 0.0}`

### ufc_1994_2026
- Root causes: missing or sparse labels, high missingness/stat distribution drift
- Target coverage: `{"winner_model": 8551, "fight_duration_model": 8551, "finish_model": 8551, "goes_distance_model": 8551, "over_1_5_model": 8551, "over_2_5_model": 8551, "ends_before_round_3_model": 8551, "finish_in_round_1_model": 8551, "finish_type_model": 4555, "method_umbrella_model": 8551, "method_model": 8551, "strike_volume_model": 0, "takedown_control_model": 8551}`
- Missingness by feature group: `{"profile": 0.8182, "record": 0.1283, "recent_form": 0.6495, "elo": 0.5, "striking": 1.0, "grappling": 1.0, "style": 0.0001, "opponent_weakness": 0.0006, "size_context": 0.0853, "data_quality": 0.0}`

### ufc_fight_forecast
- Root causes: missing or sparse labels, high missingness/stat distribution drift
- Target coverage: `{"winner_model": 8230, "fight_duration_model": 8230, "finish_model": 8230, "goes_distance_model": 8230, "over_1_5_model": 8230, "over_2_5_model": 8230, "ends_before_round_3_model": 8230, "finish_in_round_1_model": 8230, "finish_type_model": 4382, "method_umbrella_model": 8230, "method_model": 8230, "strike_volume_model": 8210, "takedown_control_model": 8210}`
- Missingness by feature group: `{"profile": 0.8182, "record": 0.2378, "recent_form": 0.714, "elo": 0.5, "striking": 1.0, "grappling": 1.0, "style": 0.1885, "opponent_weakness": 0.1886, "size_context": 0.0023, "data_quality": 0.0}`

### ufc_stats_complete
- Root causes: source-holdout regression, missing or sparse labels, high missingness/stat distribution drift, models trained on other sources do not transfer cleanly to this source
- Target coverage: `{"winner_model": 0, "fight_duration_model": 0, "finish_model": 0, "goes_distance_model": 0, "over_1_5_model": 0, "over_2_5_model": 0, "ends_before_round_3_model": 0, "finish_in_round_1_model": 0, "finish_type_model": 0, "method_umbrella_model": 0, "method_model": 0, "strike_volume_model": 8688, "takedown_control_model": 8688}`
- Missingness by feature group: `{"profile": 0.8182, "record": 0.1313, "recent_form": 0.6507, "elo": 0.5, "striking": 1.0, "grappling": 1.0, "style": 0.0095, "opponent_weakness": 0.0096, "size_context": 0.0857, "data_quality": 0.0}`

