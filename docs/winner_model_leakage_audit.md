# Winner Model Leakage Audit

## Plain-English Summary
Winner model audit status: `high_confidence_only`. This report treats the high winner accuracy as suspicious and checks features, runtime parity, source holdouts, stress segments, and confidence buckets before trusting it.

## Winner Feature List
| Feature | Classification | Runtime? | Flags |
|---|---|---|---|
| a_prior_fights | runtime_available | True |  |
| b_prior_fights | runtime_available | True |  |
| a_prior_wins | runtime_available | True |  |
| b_prior_wins | runtime_available | True |  |
| a_prior_finishes | suspicious_review_needed | True | finish |
| b_prior_finishes | suspicious_review_needed | True | finish |
| a_prior_decisions | runtime_available | True | decision |
| b_prior_decisions | runtime_available | True | decision |
| fighter_1_stance_known | runtime_available | True |  |
| fighter_2_stance_known | runtime_available | True |  |
| fighter_1_history_count | runtime_available | True |  |
| fighter_2_history_count | runtime_available | True |  |
| minimum_history_count | runtime_available | True |  |
| fighter_1_win_rate_before | runtime_available | True |  |
| fighter_2_win_rate_before | runtime_available | True |  |
| win_rate_diff | runtime_available | True |  |
| fighter_1_finish_win_rate_before | runtime_available | True | finish |
| fighter_2_finish_win_rate_before | runtime_available | True | finish |
| finish_rate_diff | runtime_available | True | finish |
| fighter_1_decision_win_rate_before | runtime_available | True | decision |
| fighter_2_decision_win_rate_before | runtime_available | True | decision |
| decision_rate_diff | runtime_available | True | decision |
| fighter_1_elo_fights_count_before | runtime_available | True |  |
| fighter_2_elo_fights_count_before | runtime_available | True |  |
| fighter_1_elo_available | runtime_available | True |  |
| fighter_2_elo_available | runtime_available | True |  |
| same_division | runtime_available | True |  |
| cross_division | runtime_available | True |  |
| catchweight | runtime_available | True |  |
| weight_class_gap | runtime_available | True |  |
| estimated_weight_gap_lbs | runtime_available | True |  |
| height_gap | runtime_available | True |  |
| reach_gap | runtime_available | True |  |
| unknown_size_context | runtime_available | True |  |
| pound_for_pound_mode | runtime_available | True |  |
| size_features_used | runtime_available | True |  |
| low_sample_warning | runtime_available | True |  |
| missing_profile_warning | runtime_available | True |  |
| missing_stats_warning | runtime_available | True |  |
| cross_division_warning | runtime_available | True |  |

## Ablation Results
| Variant | Rows | Accuracy | Balanced Accuracy | ROC AUC | Brier | Log Loss | High-Confidence Accuracy | Coverage |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| full_current_feature_set | 3327 | 0.9092 | 0.9093 | 0.9663 | 0.0701 | 0.2421 | 0.9722 | 75.65 |
| remove_suspicious_named_features | 3327 | 0.9092 | 0.9093 | 0.9678 | 0.0685 | 0.2381 | 0.9712 | 76.22 |
| basic_history_only | 3327 | 0.9152 | 0.915 | 0.9698 | 0.0661 | 0.2329 | 0.9705 | 77.34 |
| elo_history_only | 3327 | 0.9255 | 0.9253 | 0.9724 | 0.0661 | 0.2377 | 0.9772 | 71.33 |
| runtime_compatible_only | 3327 | 0.9092 | 0.9093 | 0.9663 | 0.0701 | 0.2421 | 0.9722 | 75.65 |
| shuffle_label_sanity_check | 3327 | 0.4731 | 0.474 | 0.4625 | 0.2603 | 0.7145 | 0.4426 | 45.84 |

## Source Holdout Results
| Source | Status | Rows | Accuracy | Balanced Accuracy | ROC AUC |
|---|---|---:|---:|---:|---:|
| mdabbert_ultimate | evaluated | 1189 | 0.8797 | 0.88 | 0.945 |
| ufc_1994_2025 | evaluated | 914 | 0.9092 | 0.9096 | 0.9748 |
| ufc_1994_2026 | evaluated | 1164 | 0.7981 | 0.7976 | 0.8829 |
| ufc_fight_forecast | evaluated | 954 | 0.5723 | 0.5711 | 0.5952 |
| ufc_stats_complete | insufficient_rows | 0 | None | None | None |

## Stress Tests
| Segment | Rows | Accuracy | Balanced Accuracy |
|---|---:|---:|---:|
| cold_start_any_fighter_zero_prior | 20 | 0.55 | 0.5404 |
| low_history_any_fighter_under_3 | 267 | 0.8577 | 0.8583 |
| debutant_both_zero_prior | 7 | None | None |
| recent_only_newest_half | 1663 | 0.8677 | 0.8678 |

## Runtime Parity
- Runtime compatible: True
- Missing runtime features: 0

## Final Status
{
  "status": "high_confidence_only",
  "runtime_parity_ok": true,
  "leakage_scan_ok": false,
  "source_holdout_ok": false,
  "source_holdout_min_balanced_accuracy": 0.65,
  "low_history_ok": true,
  "reason": "Do not mark production_ready until runtime parity, source holdout, cold-start, and calibration are reviewed together."
}
