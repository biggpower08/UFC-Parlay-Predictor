# Source Feature And Label Drift Report

## Plain-English Summary
This report grades each model/source pair for label drift, feature drift, and source-holdout risk. Higher-risk rows should stay experimental.

| Model | Source | Rows | Target Rate | Holdout Drop | Feature Drift | Label Drift | Risk | Grade |
|---|---|---:|---|---:|---:|---:|---:|---|
| fight_duration_model | mdabbert_ultimate | 7190 | 0.5218 | 0.0286 | 0.0132 | 0.0107 | 0.0309 | low drift |
| fight_duration_model | ufc_1994_2025 | 16674 | 0.5325 | -0.0233 | 0.0308 | 0.0031 | 0.0235 | low drift |
| fight_duration_model | ufc_1994_2026 | 8551 | 0.5327 | 0.077 | 0.0178 | 0.0035 | 0.0445 | low drift |
| fight_duration_model | ufc_fight_forecast | 8231 | 0.5324 | None | 0.03 | 0.0031 | 0.0616 | low drift |
| fight_duration_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| finish_model | mdabbert_ultimate | 7190 | 0.5218 | 0.0286 | 0.0132 | 0.0107 | 0.0309 | low drift |
| finish_model | ufc_1994_2025 | 16674 | 0.5325 | -0.0233 | 0.0308 | 0.0031 | 0.0235 | low drift |
| finish_model | ufc_1994_2026 | 8551 | 0.5327 | 0.077 | 0.0178 | 0.0035 | 0.0445 | low drift |
| finish_model | ufc_fight_forecast | 8231 | 0.5324 | None | 0.03 | 0.0031 | 0.0616 | low drift |
| finish_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| goes_distance_model | mdabbert_ultimate | 7190 | 0.4782 | 0.0286 | 0.0132 | 0.0107 | 0.0309 | low drift |
| goes_distance_model | ufc_1994_2025 | 16674 | 0.4675 | -0.0233 | 0.0308 | 0.0031 | 0.0235 | low drift |
| goes_distance_model | ufc_1994_2026 | 8551 | 0.4673 | 0.077 | 0.0178 | 0.0035 | 0.0445 | low drift |
| goes_distance_model | ufc_fight_forecast | 8231 | 0.4676 | None | 0.03 | 0.0031 | 0.0616 | low drift |
| goes_distance_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| over_1_5_model | mdabbert_ultimate | 7190 | 0.6858 | -0.0102 | 0.0132 | 0.0399 | 0.0469 | low drift |
| over_1_5_model | ufc_1994_2025 | 16674 | 0.6451 | -0.0106 | 0.0308 | 0.0125 | 0.0423 | low drift |
| over_1_5_model | ufc_1994_2026 | 8551 | 0.6475 | 0.0232 | 0.0178 | 0.0093 | 0.0474 | low drift |
| over_1_5_model | ufc_fight_forecast | 8231 | 0.645 | None | 0.03 | 0.0127 | 0.0649 | low drift |
| over_1_5_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| over_2_5_model | mdabbert_ultimate | 7190 | 0.5603 | -0.002 | 0.0132 | 0.0404 | 0.0369 | low drift |
| over_2_5_model | ufc_1994_2025 | 16674 | 0.5193 | -0.0381 | 0.0308 | 0.0124 | 0.03 | low drift |
| over_2_5_model | ufc_1994_2026 | 8551 | 0.5211 | 0.0663 | 0.0178 | 0.0101 | 0.0487 | low drift |
| over_2_5_model | ufc_fight_forecast | 8231 | 0.5193 | None | 0.03 | 0.0124 | 0.0648 | low drift |
| over_2_5_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| ends_before_round_3_model | mdabbert_ultimate | 7190 | 0.4024 | -0.0098 | 0.0132 | 0.041 | 0.0405 | low drift |
| ends_before_round_3_model | ufc_1994_2025 | 16674 | 0.4442 | -0.0378 | 0.0308 | 0.0128 | 0.0338 | low drift |
| ends_before_round_3_model | ufc_1994_2026 | 8551 | 0.4421 | 0.0374 | 0.0178 | 0.01 | 0.0448 | low drift |
| ends_before_round_3_model | ufc_fight_forecast | 8231 | 0.4441 | None | 0.03 | 0.0127 | 0.0649 | low drift |
| ends_before_round_3_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| finish_in_round_1_model | mdabbert_ultimate | 7190 | 0.2465 | -0.0083 | 0.0132 | 0.0346 | 0.0454 | low drift |
| finish_in_round_1_model | ufc_1994_2025 | 16674 | 0.2821 | -0.0097 | 0.0308 | 0.0111 | 0.0421 | low drift |
| finish_in_round_1_model | ufc_1994_2026 | 8551 | 0.2794 | 0.0267 | 0.0178 | 0.0076 | 0.0478 | low drift |
| finish_in_round_1_model | ufc_fight_forecast | 8231 | 0.2821 | None | 0.03 | 0.0112 | 0.0644 | low drift |
| finish_in_round_1_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| finish_type_model | mdabbert_ultimate | 7190 | {'KO/TKO': 0.5942, 'Other': 0.069, 'Submission': 0.3368} | -0.063 | 0.0132 | 0.0569 | 0.0693 | low drift |
| finish_type_model | ufc_1994_2025 | 16674 | {'KO/TKO': 0.6235, 'Other': 0.0053, 'Submission': 0.3712} | -0.0556 | 0.0308 | 0.026 | 0.0652 | low drift |
| finish_type_model | ufc_1994_2026 | 8551 | {'KO/TKO': 0.6114, 'Other': 0.0252, 'Submission': 0.3633} | 0.058 | 0.0178 | 0.0034 | 0.0623 | low drift |
| finish_type_model | ufc_fight_forecast | 8231 | {'KO/TKO': 0.6237, 'Other': 0.0052, 'Submission': 0.3711} | None | 0.03 | 0.026 | 0.0696 | low drift |
| finish_type_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| method_umbrella_model | mdabbert_ultimate | 7190 | {'Decision': 0.4782, 'KO/TKO': 0.3101, 'Other': 0.036, 'Submission': 0.1758} | 0.001 | 0.0132 | 0.0402 | 0.0939 | low drift |
| method_umbrella_model | ufc_1994_2025 | 16674 | {'Decision': 0.4675, 'KO/TKO': 0.332, 'Other': 0.0028, 'Submission': 0.1977} | -0.0104 | 0.0308 | 0.0169 | 0.0917 | low drift |
| method_umbrella_model | ufc_1994_2026 | 8551 | {'Decision': 0.4673, 'KO/TKO': 0.3257, 'Other': 0.0134, 'Submission': 0.1935} | 0.0036 | 0.0178 | 0.0035 | 0.0832 | low drift |
| method_umbrella_model | ufc_fight_forecast | 8231 | {'Decision': 0.4676, 'KO/TKO': 0.3321, 'Other': 0.0028, 'Submission': 0.1976} | None | 0.03 | 0.0168 | 0.0664 | low drift |
| method_umbrella_model | ufc_stats_complete | 8709 | None | None | 0.02 | 1.0 | 0.407 | high drift |
| strike_volume_model | mdabbert_ultimate | 7190 | None | None | 0.0132 | 1.0 | 0.4046 | high drift |
| strike_volume_model | ufc_1994_2025 | 16674 | {'high': 0.2676, 'low': 0.4176, 'medium': 0.3148} | 0.0738 | 0.0308 | 0.0013 | 0.0768 | low drift |
| strike_volume_model | ufc_1994_2026 | 8551 | None | None | 0.0178 | 1.0 | 0.4062 | high drift |
| strike_volume_model | ufc_fight_forecast | 8231 | {'high': 0.2672, 'low': 0.4191, 'medium': 0.3136} | None | 0.03 | 0.0017 | 0.0611 | low drift |
| strike_volume_model | ufc_stats_complete | 8709 | {'high': 0.2697, 'low': 0.4169, 'medium': 0.3134} | 0.1594 | 0.02 | 0.0022 | 0.0994 | low drift |
| takedown_control_model | mdabbert_ultimate | 7190 | None | None | 0.0132 | 1.0 | 0.4046 | high drift |
| takedown_control_model | ufc_1994_2025 | 16674 | 0.4506 | 0.0463 | 0.0308 | 0.0387 | 0.0675 | low drift |
| takedown_control_model | ufc_1994_2026 | 8551 | 0.3361 | 0.0026 | 0.0178 | 0.1143 | 0.0758 | low drift |
| takedown_control_model | ufc_fight_forecast | 8231 | 0.4501 | None | 0.03 | 0.0284 | 0.0704 | low drift |
| takedown_control_model | ufc_stats_complete | 8709 | 0.4504 | 0.0942 | 0.02 | 0.0293 | 0.0761 | low drift |
