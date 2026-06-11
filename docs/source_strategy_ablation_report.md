# Source Strategy Ablation Report

## Plain-English Summary
This report lists controlled recovery strategies. Current source-holdout already acts as the exclude-source ablation. Stable source-holdout can restore production-candidate status, but no model is marked production-ready in this pass.

| Model | Strategy | Excluded Sources | Normal Metric | Holdout Metric | Worst Source | Drop | Status After Gates | Improves Production Status | Notes |
|---|---|---|---:|---:|---|---:|---|---|---|
| fight_duration_model | current_combined_source_training |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | baseline strategy currently used for reports |
| fight_duration_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| fight_duration_model | source_quality_flags_enabled |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| fight_duration_model | source_balanced_sampling_or_weights |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| fight_duration_model | model_specific_source_subset | ufc_1994_2026 | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | review weakest source ufc_1994_2026 before packaging |
| finish_model | current_combined_source_training |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | baseline strategy currently used for reports |
| finish_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| finish_model | source_quality_flags_enabled |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| finish_model | source_balanced_sampling_or_weights |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| finish_model | model_specific_source_subset | ufc_1994_2026 | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | review weakest source ufc_1994_2026 before packaging |
| goes_distance_model | current_combined_source_training |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | baseline strategy currently used for reports |
| goes_distance_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| goes_distance_model | source_quality_flags_enabled |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| goes_distance_model | source_balanced_sampling_or_weights |  | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| goes_distance_model | model_specific_source_subset | ufc_1994_2026 | 0.8596 | 0.7826 | ufc_1994_2026 | 0.077 | production_candidate | True | review weakest source ufc_1994_2026 before packaging |
| over_1_5_model | current_combined_source_training |  | 0.7947 | 0.7715 | ufc_1994_2026 | 0.0232 | production_candidate | True | baseline strategy currently used for reports |
| over_1_5_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.7947 | 0.7715 | ufc_1994_2026 | 0.0232 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| over_1_5_model | source_quality_flags_enabled |  | 0.7947 | 0.7715 | ufc_1994_2026 | 0.0232 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| over_1_5_model | source_balanced_sampling_or_weights |  | 0.7947 | 0.7715 | ufc_1994_2026 | 0.0232 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| over_1_5_model | model_specific_source_subset | ufc_1994_2026 | 0.7947 | 0.7715 | ufc_1994_2026 | 0.0232 | production_candidate | True | round models should use only sources with reliable finish round/time parsing |
| over_2_5_model | current_combined_source_training |  | 0.8197 | 0.7534 | ufc_1994_2026 | 0.0663 | production_candidate | True | baseline strategy currently used for reports |
| over_2_5_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.8197 | 0.7534 | ufc_1994_2026 | 0.0663 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| over_2_5_model | source_quality_flags_enabled |  | 0.8197 | 0.7534 | ufc_1994_2026 | 0.0663 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| over_2_5_model | source_balanced_sampling_or_weights |  | 0.8197 | 0.7534 | ufc_1994_2026 | 0.0663 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| over_2_5_model | model_specific_source_subset | ufc_1994_2026 | 0.8197 | 0.7534 | ufc_1994_2026 | 0.0663 | production_candidate | True | round models should use only sources with reliable finish round/time parsing |
| ends_before_round_3_model | current_combined_source_training |  | 0.7926 | 0.7552 | ufc_1994_2026 | 0.0374 | production_candidate | True | baseline strategy currently used for reports |
| ends_before_round_3_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.7926 | 0.7552 | ufc_1994_2026 | 0.0374 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| ends_before_round_3_model | source_quality_flags_enabled |  | 0.7926 | 0.7552 | ufc_1994_2026 | 0.0374 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| ends_before_round_3_model | source_balanced_sampling_or_weights |  | 0.7926 | 0.7552 | ufc_1994_2026 | 0.0374 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| ends_before_round_3_model | model_specific_source_subset | ufc_1994_2026 | 0.7926 | 0.7552 | ufc_1994_2026 | 0.0374 | production_candidate | True | round models should use only sources with reliable finish round/time parsing |
| finish_in_round_1_model | current_combined_source_training |  | 0.8437 | 0.817 | ufc_1994_2026 | 0.0267 | production_candidate | True | baseline strategy currently used for reports |
| finish_in_round_1_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.8437 | 0.817 | ufc_1994_2026 | 0.0267 | production_candidate | True | already represented by source-holdout when ufc_stats_complete is the held-out source |
| finish_in_round_1_model | source_quality_flags_enabled |  | 0.8437 | 0.817 | ufc_1994_2026 | 0.0267 | production_candidate | True | recommended next implementation; not used as direct source shortcut |
| finish_in_round_1_model | source_balanced_sampling_or_weights |  | 0.8437 | 0.817 | ufc_1994_2026 | 0.0267 | production_candidate | True | candidate next experiment to reduce domination by any one source |
| finish_in_round_1_model | model_specific_source_subset | ufc_1994_2026 | 0.8437 | 0.817 | ufc_1994_2026 | 0.0267 | production_candidate | True | round models should use only sources with reliable finish round/time parsing |
| finish_type_model | current_combined_source_training |  | 0.7956 | 0.8512 | ufc_1994_2025 | -0.0556 | experimental | False | baseline strategy currently used for reports |
| finish_type_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.7956 | 0.8512 | ufc_1994_2025 | -0.0556 | experimental | False | already represented by source-holdout when ufc_stats_complete is the held-out source |
| finish_type_model | source_quality_flags_enabled |  | 0.7956 | 0.8512 | ufc_1994_2025 | -0.0556 | experimental | False | recommended next implementation; not used as direct source shortcut |
| finish_type_model | source_balanced_sampling_or_weights |  | 0.7956 | 0.8512 | ufc_1994_2025 | -0.0556 | experimental | False | candidate next experiment to reduce domination by any one source |
| finish_type_model | model_specific_source_subset | ufc_1994_2025 | 0.7956 | 0.8512 | ufc_1994_2025 | -0.0556 | experimental | False | method models should use sources with clean canonical method labels |
| method_umbrella_model | current_combined_source_training |  | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | baseline strategy currently used for reports |
| method_umbrella_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | already represented by source-holdout when ufc_stats_complete is the held-out source |
| method_umbrella_model | source_quality_flags_enabled |  | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | recommended next implementation; not used as direct source shortcut |
| method_umbrella_model | source_balanced_sampling_or_weights |  | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | candidate next experiment to reduce domination by any one source |
| method_umbrella_model | model_specific_source_subset | ufc_1994_2026 | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | method models should use sources with clean canonical method labels |
| method_model | current_combined_source_training |  | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | baseline strategy currently used for reports |
| method_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | already represented by source-holdout when ufc_stats_complete is the held-out source |
| method_model | source_quality_flags_enabled |  | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | recommended next implementation; not used as direct source shortcut |
| method_model | source_balanced_sampling_or_weights |  | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | candidate next experiment to reduce domination by any one source |
| method_model | model_specific_source_subset | ufc_1994_2026 | 0.5191 | 0.5155 | ufc_1994_2026 | 0.0036 | weak_or_failed_baseline | False | method models should use sources with clean canonical method labels |
| strike_volume_model | current_combined_source_training |  | 0.5749 | 0.4155 | ufc_stats_complete | 0.1594 | experimental | False | baseline strategy currently used for reports |
| strike_volume_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.5749 | 0.4155 | ufc_stats_complete | 0.1594 | experimental | False | already represented by source-holdout when ufc_stats_complete is the held-out source |
| strike_volume_model | source_quality_flags_enabled |  | 0.5749 | 0.4155 | ufc_stats_complete | 0.1594 | experimental | False | recommended next implementation; not used as direct source shortcut |
| strike_volume_model | source_balanced_sampling_or_weights |  | 0.5749 | 0.4155 | ufc_stats_complete | 0.1594 | experimental | False | candidate next experiment to reduce domination by any one source |
| strike_volume_model | model_specific_source_subset | ufc_stats_complete | 0.5749 | 0.4155 | ufc_stats_complete | 0.1594 | experimental | False | stat models may need source eligibility based on reliable strike/takedown coverage, not all combined sources |
| takedown_control_model | current_combined_source_training |  | 0.7285 | 0.6343 | ufc_stats_complete | 0.0942 | experimental | False | baseline strategy currently used for reports |
| takedown_control_model | exclude_ufc_stats_complete_from_training_test_on_it | ufc_stats_complete | 0.7285 | 0.6343 | ufc_stats_complete | 0.0942 | experimental | False | already represented by source-holdout when ufc_stats_complete is the held-out source |
| takedown_control_model | source_quality_flags_enabled |  | 0.7285 | 0.6343 | ufc_stats_complete | 0.0942 | experimental | False | recommended next implementation; not used as direct source shortcut |
| takedown_control_model | source_balanced_sampling_or_weights |  | 0.7285 | 0.6343 | ufc_stats_complete | 0.0942 | experimental | False | candidate next experiment to reduce domination by any one source |
| takedown_control_model | model_specific_source_subset | ufc_stats_complete | 0.7285 | 0.6343 | ufc_stats_complete | 0.0942 | experimental | False | stat models may need source eligibility based on reliable strike/takedown coverage, not all combined sources |

## Recovery Recommendations
- `winner_model`: Keep high_confidence_only until winner-specific source holdout and leakage audit gates pass.
- `fight_duration_model`: Investigate duration label drift and try source-stable feature subsets before restoring candidate status.
- `finish_model`: Compatibility output follows fight_duration_model.
- `goes_distance_model`: Compatibility output follows fight_duration_model.
- `round_models`: Check round/time parsing and avoid production until source-holdout stabilizes.
- `finish_type_model`: Audit method mappings and consider binary KO/TKO-vs-other and submission-vs-other finish submodels.
- `method_umbrella_model`: Keep composite and improve through duration and finish-type components.
- `strike_volume_model`: Treat ufc_stats_complete as a likely preferred stat-label source, but keep output experimental until transfer/calibration improves.
- `takedown_control_model`: Check takedown/control coverage and definitions by source before production use.
- `odds_calibration_model`: Remain blocked until trusted pre-fight odds timestamps exist.
