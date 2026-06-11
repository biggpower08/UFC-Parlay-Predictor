# Source Eligibility Rules

## Plain-English Summary
Each data source should only support the model targets it can safely label. This prevents stat-rich but result-label-weak sources from creating fake winner, duration, method, or round labels.

## ufc_stats_complete
- Safe uses: strike labels, takedown/control labels, stat coverage cross-checks
- Unsafe uses: universal winner labels, universal duration labels, universal method labels, universal round labels
- Notes: Treat primarily as a stat-rich source, not a universal result-label source.; No-contest, draw, unknown, or missing result rows must not create fake target labels.

| Model | Eligibility |
|---|---|
| winner_model | ineligible_result_labels_unsafe |
| fight_duration_model | ineligible_result_labels_unsafe |
| finish_model | ineligible_result_labels_unsafe |
| goes_distance_model | ineligible_result_labels_unsafe |
| over_1_5_model | ineligible_round_result_labels_unsafe |
| over_2_5_model | ineligible_round_result_labels_unsafe |
| ends_before_round_3_model | ineligible_round_result_labels_unsafe |
| finish_in_round_1_model | ineligible_round_result_labels_unsafe |
| finish_type_model | ineligible_method_labels_unsafe |
| method_umbrella_model | ineligible_method_labels_unsafe |
| method_model | ineligible_method_labels_unsafe |
| strike_volume_model | eligible_stat_labels |
| takedown_control_model | eligible_stat_labels |
| odds_calibration_model | ineligible_no_trusted_prefight_odds |

## mdabbert_ultimate
- Safe uses: broad result history, winner/duration/method labels where present, odds-aware research review
- Unsafe uses: primary strike/takedown/control labels when detailed stats are missing
- Notes: Useful broad history source, but detailed stat coverage is weaker.

| Model | Eligibility |
|---|---|
| winner_model | eligible_safe_result_labels |
| fight_duration_model | eligible_safe_result_labels |
| finish_model | eligible_safe_result_labels |
| goes_distance_model | eligible_safe_result_labels |
| over_1_5_model | eligible_if_round_time_present |
| over_2_5_model | eligible_if_round_time_present |
| ends_before_round_3_model | eligible_if_round_time_present |
| finish_in_round_1_model | eligible_if_round_time_present |
| finish_type_model | eligible_clean_method_labels |
| method_umbrella_model | eligible_if_components_eligible |
| method_model | eligible_if_components_eligible |
| strike_volume_model | ineligible_missing_stat_labels |
| takedown_control_model | ineligible_missing_stat_labels |
| odds_calibration_model | blocked_until_prefight_timestamps_trusted |

## ufc_1994_2025
- Safe uses: broad fight history, result/method/round labels, stat labels with drift review
- Unsafe uses: unreviewed production stat modeling
- Notes: Broad source, but method/stat drift still needs monitoring.

| Model | Eligibility |
|---|---|
| winner_model | eligible_safe_result_labels |
| fight_duration_model | eligible_safe_result_labels |
| finish_model | eligible_safe_result_labels |
| goes_distance_model | eligible_safe_result_labels |
| over_1_5_model | eligible_if_round_time_present |
| over_2_5_model | eligible_if_round_time_present |
| ends_before_round_3_model | eligible_if_round_time_present |
| finish_in_round_1_model | eligible_if_round_time_present |
| finish_type_model | eligible_clean_method_labels |
| method_umbrella_model | eligible_if_components_eligible |
| method_model | eligible_if_components_eligible |
| strike_volume_model | eligible_with_drift_review |
| takedown_control_model | eligible_with_drift_review |
| odds_calibration_model | ineligible_no_trusted_prefight_odds |

## ufc_1994_2026
- Safe uses: broad fight history, result/method/round labels
- Unsafe uses: unreviewed production use where holdout drift is high
- Notes: Useful broad history source with high drift in some holdouts.

| Model | Eligibility |
|---|---|
| winner_model | eligible_but_source_transfer_review_needed |
| fight_duration_model | eligible_safe_result_labels |
| finish_model | eligible_safe_result_labels |
| goes_distance_model | eligible_safe_result_labels |
| over_1_5_model | eligible_if_round_time_present |
| over_2_5_model | eligible_if_round_time_present |
| ends_before_round_3_model | eligible_if_round_time_present |
| finish_in_round_1_model | eligible_if_round_time_present |
| finish_type_model | eligible_clean_method_labels |
| method_umbrella_model | eligible_if_components_eligible |
| method_model | eligible_if_components_eligible |
| strike_volume_model | ineligible_missing_stat_labels |
| takedown_control_model | eligible_with_drift_review |
| odds_calibration_model | ineligible_no_trusted_prefight_odds |

## ufc_fight_forecast
- Safe uses: broad result history, result/method/round labels, some stat labels
- Unsafe uses: winner production claims until transfer stabilizes
- Notes: Medium drift source; winner transfer remains mixed.

| Model | Eligibility |
|---|---|
| winner_model | eligible_but_source_transfer_review_needed |
| fight_duration_model | eligible_safe_result_labels |
| finish_model | eligible_safe_result_labels |
| goes_distance_model | eligible_safe_result_labels |
| over_1_5_model | eligible_if_round_time_present |
| over_2_5_model | eligible_if_round_time_present |
| ends_before_round_3_model | eligible_if_round_time_present |
| finish_in_round_1_model | eligible_if_round_time_present |
| finish_type_model | eligible_clean_method_labels |
| method_umbrella_model | eligible_if_components_eligible |
| method_model | eligible_if_components_eligible |
| strike_volume_model | eligible_with_drift_review |
| takedown_control_model | eligible_with_drift_review |
| odds_calibration_model | ineligible_no_trusted_prefight_odds |
