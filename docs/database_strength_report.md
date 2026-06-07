# Database Strength Report

## Plain-English Summary
Imported local Kaggle files were normalized into fight, fighter, stats, and odds coverage summaries. Raw datasets remain local-only under `data/imports/`.

## Coverage
- Normalized rows: 49355
- Canonical fight keys: 32982
- Fighters found: 2804
- Date range: {'min': '1993-11-12', 'max': '2026-05-16'}
- Odds status: review_needed

## Dataset Contributions
| Dataset | Available | Rows | Files | Helps Models | Zero-row Reason |
|---|---|---:|---:|---|---|
| ufc_fight_forecast | True | 8231 | 2 | finish_model, goes_distance_model, method_model, odds_calibration_model, round_phase_model, strike_volume_model, takedown_control_model, winner_model |  |
| ufc_stats_complete | True | 8709 | 2 | finish_model, goes_distance_model, method_model, round_phase_model, strike_volume_model, takedown_control_model, winner_model |  |
| ufc_1994_2026 | True | 8551 | 2 | finish_model, goes_distance_model, method_model, round_phase_model, takedown_control_model, winner_model |  |
| ufc_1994_2025 | True | 16674 | 4 | finish_model, goes_distance_model, method_model, round_phase_model, strike_volume_model, takedown_control_model, winner_model |  |
| mdabbert_ultimate | True | 7190 | 2 | finish_model, goes_distance_model, method_model, odds_calibration_model, round_phase_model, winner_model |  |
| mdabbert_2010_2020_odds | True | 0 | 1 |  | odds-only dataset; retained for odds research until pre-fight timestamp quality is confirmed |
| ufc_datalab | False | 0 | 0 |  | dataset folder missing |

## Missing Common Fields
- `fighter_1_id_source`
- `fighter_2_id_source`
- `gender_or_division_group`
- `title_fight`
- `catchweight`
- `fighter_1_total_strikes_landed`
- `fighter_2_total_strikes_landed`
- `odds_source`
- `odds_snapshot_date`
- `odds_is_prefight`
- `closing_line_available`
- `fighter_1_age`
- `fighter_2_age`
- `invalid_target_reason`
- `inside_distance`
- `fighter_1_by_ko_tko`
- `fighter_1_by_submission`
- `fighter_1_by_decision`
- `fighter_2_by_ko_tko`
- `fighter_2_by_submission`
- `fighter_2_by_decision`
- `ends_round_1`
- `ends_round_2`
- `ends_round_3`
- `ends_before_round_2`
- `ends_before_round_3`
- `over_1_5`
- `over_2_5`
- `over_3_5`
- `fighter_1_over_25_sig_strikes`
- `fighter_1_over_50_sig_strikes`
- `fighter_1_over_75_sig_strikes`
- `fighter_2_over_25_sig_strikes`
- `fighter_2_over_50_sig_strikes`
- `fighter_2_over_75_sig_strikes`
- `fighter_1_over_0_5_takedowns`
- `fighter_1_over_1_5_takedowns`
- `fighter_1_over_2_5_takedowns`
- `fighter_2_over_0_5_takedowns`
- `fighter_2_over_1_5_takedowns`
- `fighter_2_over_2_5_takedowns`
- `fighter_1_control_time_over_300_seconds`
- `fighter_2_control_time_over_300_seconds`

## Source Priority
Higher-priority UFCStats-derived result/stat datasets provide fight labels first; odds-only datasets are retained for research until timestamp quality is trusted.
