# Model Accuracy Report

## Plain-English Summary
Models were evaluated on the newest chronological holdout from normalized historical fight data. Finish and goes-distance are now one fight-duration model with inverse outputs, while method is estimated from duration plus conditional finish type. Metrics are approximate final-test results, not guarantees.

## Hierarchical Fight Outcome Model
- `fight_duration_model` predicts finish probability; `goes_distance_probability` is `1 - finish_probability`.
- `finish_model` and `goes_distance_model` remain as compatibility report entries backed by the same duration model.
- Round reads are separate binary submodels instead of one broad multiclass round-phase model.
- `finish_type_model` is trained only on fights that actually finished.
- `method_umbrella_model` combines `P(decision) = P(goes_distance)` with `P(KO/TKO or submission) = P(finish) * P(type | finish)`.

## Hierarchy Metrics
| Model | Status | Rows | Accuracy | Balanced Accuracy | ROC AUC | Brier | Baseline | Improvement |
|---|---|---:|---:|---:|---:|---:|---:|---:|
| fight_duration_model | evaluated | 3696 | 0.8287 | 0.8282 | 0.9021 | 0.1257 | 0.5141 | 0.3146 |
| over_1_5_model | evaluated | 3683 | 0.7869 | 0.7009 | 0.8299 | 0.145 | 0.6964 | 0.0905 |
| over_2_5_model | evaluated | 3683 | 0.7993 | 0.7916 | 0.8734 | 0.1428 | 0.5599 | 0.2394 |
| ends_before_round_3_model | evaluated | 3683 | 0.7763 | 0.7503 | 0.8472 | 0.1532 | 0.6066 | 0.1697 |
| finish_in_round_1_model | evaluated | 3683 | 0.8306 | 0.6966 | 0.861 | 0.1177 | 0.7613 | 0.0693 |
| finish_type_model | evaluated | 1796 | 0.7728 | 0.6162 | None | None | 0.632 | 0.1408 |
| method_umbrella_model | evaluated | 3696 | 0.7538 | 0.5628 | None | None | 0.5141 | 0.2397 |

## Method Probability Logic
- Decision probability comes from the duration model's goes-distance output.
- KO/TKO and submission probabilities are conditional on the fight first being projected to finish.
- The combined method output improved over majority baseline on accuracy, but balanced method metrics remain modest, so it is not production-ready.

## Split
- Train: 29347 rows, {'min': '1993-11-12', 'max': '2021-07-10'}
- Validation: 6134 rows, {'min': '2021-07-10', 'max': '2023-11-18'}
- Final test: 5537 rows, {'min': '2023-11-18', 'max': '2026-05-16'}
- Fight-group leakage check: True

## Source Contributions
- All rows by dataset: {'mdabbert_ultimate': 7190, 'ufc_1994_2025': 16674, 'ufc_1994_2026': 8551, 'ufc_fight_forecast': 8231, 'ufc_stats_complete': 8709}
- Train rows by dataset: {'mdabbert_ultimate': 4771, 'ufc_1994_2025': 6176, 'ufc_1994_2026': 6154, 'ufc_fight_forecast': 6062, 'ufc_stats_complete': 6184}
- Validation rows by dataset: {'mdabbert_ultimate': 1209, 'ufc_1994_2025': 1239, 'ufc_1994_2026': 1233, 'ufc_fight_forecast': 1214, 'ufc_stats_complete': 1239}
- Final test rows by dataset: {'mdabbert_ultimate': 1210, 'ufc_1994_2025': 922, 'ufc_1994_2026': 1164, 'ufc_fight_forecast': 955, 'ufc_stats_complete': 1286}

## Model Ranking
| Model | Status | Test Rows | Main Metric | Baseline | Improvement | Beats Baseline | Notes |
|---|---|---:|---:|---:|---:|---|---|
| winner_model | evaluated | 3327 | 0.9621 | 0.52 | 0.4421 | True |  |
| fight_duration_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True |  |
| finish_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True | Compatibility output: internally backed by fight_duration_model. |
| goes_distance_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True | Compatibility output: goes_distance_probability is derived as 1 - finish_probability. |
| method_umbrella_model | evaluated | 3696 | 0.7538 | 0.5141 | 0.2397 | True | Umbrella method output combines duration probability with conditional finish type probabilities. |
| method_model | evaluated | 3696 | 0.7538 | 0.5141 | 0.2397 | True | Umbrella method output combines duration probability with conditional finish type probabilities.; Compatibility alias backed by method_umbrella_model. |
| over_2_5_model | evaluated | 3683 | 0.7993 | 0.5599 | 0.2394 | True |  |
| round_phase_model | evaluated | 3683 | 0.7993 | 0.5599 | 0.2394 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels. |
| round_model | evaluated | 3683 | 0.7993 | 0.5599 | 0.2394 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Compatibility alias backed by round_phase_model. |
| strike_volume_model | evaluated | 1322 | 0.5749 | 0.3623 | 0.2126 | True |  |
| ends_before_round_3_model | evaluated | 3683 | 0.7763 | 0.6066 | 0.1697 | True |  |
| finish_type_model | evaluated | 1796 | 0.7728 | 0.632 | 0.1408 | True | Conditional model: trained and scored only on fights that actually finished. |
| takedown_control_model | evaluated | 2486 | 0.7285 | 0.5897 | 0.1388 | True |  |
| over_1_5_model | evaluated | 3683 | 0.7869 | 0.6964 | 0.0905 | True |  |
| finish_in_round_1_model | evaluated | 3683 | 0.8306 | 0.7613 | 0.0693 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Source-Holdout Transfer Summary
| Model | Normal Metric | Worst Source Metric | Drop | Worst Source | Rows | Source-Holdout Status | Production Status |
|---|---:|---:|---:|---|---:|---|---|
| winner_model | 0.9621 | 0.8222 | 0.1399 | ufc_1994_2026 | 1164 | needs_review | high_confidence_only |
| fight_duration_model | 0.8287 | 0.5762 | 0.2525 | ufc_stats_complete | 361 | unstable | experimental |
| over_1_5_model | 0.7869 | 0.6399 | 0.147 | ufc_stats_complete | 361 | needs_review | experimental |
| over_2_5_model | 0.7993 | 0.5873 | 0.212 | ufc_stats_complete | 361 | unstable | experimental |
| ends_before_round_3_model | 0.7763 | 0.5873 | 0.189 | ufc_stats_complete | 361 | unstable | experimental |
| finish_in_round_1_model | 0.8306 | 0.7175 | 0.1131 | ufc_stats_complete | 361 | needs_review | experimental |
| finish_type_model | 0.7728 | 0.4813 | 0.2915 | ufc_stats_complete | 187 | unstable | experimental |
| method_umbrella_model | 0.7538 | 0.4183 | 0.3355 | ufc_stats_complete | 361 | unstable | experimental |
| strike_volume_model | 0.5749 | 0.4155 | 0.1594 | ufc_stats_complete | 361 | unstable | experimental |
| takedown_control_model | 0.7285 | 0.6343 | 0.0942 | ufc_stats_complete | 361 | needs_review | experimental |
| finish_model | 0.8287 | 0.5762 | 0.2525 | ufc_stats_complete | 361 | unstable | experimental |
| goes_distance_model | 0.8287 | 0.5762 | 0.2525 | ufc_stats_complete | 361 | unstable | experimental |
| method_model | 0.7538 | 0.4183 | 0.3355 | ufc_stats_complete | 361 | unstable | experimental |
| round_phase_model | 0.7993 | 0.5873 | 0.212 | ufc_stats_complete | 361 | unstable | experimental |
| round_model | 0.7993 | 0.5873 | 0.212 | ufc_stats_complete | 361 | unstable | experimental |
| strike_volume_regression | 52.6679 |  |  |  |  | not_run | weak_or_failed_baseline |
| odds_calibration_model |  |  |  |  |  | not_run | blocked |

## Segment Performance
### winner_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.9634}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.9635}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.9511}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.9352}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.9777}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.9702}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.9594}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.9765}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.963}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9816}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9624}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.969}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8839}
### fight_duration_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8629}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8084}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.8328}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8261}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8327}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8409}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8207}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.82}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8068}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8541}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8292}
- low_fighter_history: {'rows': 341, 'accuracy': 0.824}
### over_1_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8744}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7676}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7842}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7222}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.7}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7963}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.704}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7566}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7584}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8971}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.9052}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7862}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7929}
### over_2_5_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8791}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7746}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7877}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.8294}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.76}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7817}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.8161}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7279}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7651}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.7943}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8578}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7958}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8343}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.8365}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7324}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.7432}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7738}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.764}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.7277}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7653}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7566}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.7651}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.8514}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.8664}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7743}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7959}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 422, 'accuracy': 0.9194}
- weight_class:featherweight: {'rows': 426, 'accuracy': 0.7911}
- weight_class:flyweight: {'rows': 292, 'accuracy': 0.8699}
- weight_class:heavyweight: {'rows': 252, 'accuracy': 0.7778}
- weight_class:light_heavyweight: {'rows': 250, 'accuracy': 0.704}
- weight_class:lightweight: {'rows': 481, 'accuracy': 0.8191}
- weight_class:middleweight: {'rows': 473, 'accuracy': 0.7653}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995}
- weight_class:women's_bantamweight: {'rows': 149, 'accuracy': 0.8993}
- weight_class:women's_flyweight: {'rows': 175, 'accuracy': 0.9086}
- weight_class:women's_strawweight: {'rows': 232, 'accuracy': 0.9612}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8284}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8521}
### finish_type_model
- weight_class:bantamweight: {'rows': 133, 'accuracy': 0.6992}
- weight_class:featherweight: {'rows': 235, 'accuracy': 0.8596}
- weight_class:flyweight: {'rows': 139, 'accuracy': 0.8201}
- weight_class:heavyweight: {'rows': 128, 'accuracy': 0.7656}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8012}
- weight_class:lightweight: {'rows': 249, 'accuracy': 0.7108}
- weight_class:middleweight: {'rows': 280, 'accuracy': 0.7429}
- weight_class:welterweight: {'rows': 235, 'accuracy': 0.8085}
- weight_class:women's_bantamweight: {'rows': 60, 'accuracy': 0.7333}
- weight_class:women's_strawweight: {'rows': 73, 'accuracy': 0.6164}
- enough_fighter_history: {'rows': 1599, 'accuracy': 0.7867}
- low_fighter_history: {'rows': 197, 'accuracy': 0.6599}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8298}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.743}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.7747}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7233}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7291}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7417}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7068}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7303}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.76}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.7898}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7897}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7589}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7038}
### strike_volume_model
- weight_class:bantamweight: {'rows': 150, 'accuracy': 0.6}
- weight_class:featherweight: {'rows': 154, 'accuracy': 0.5909}
- weight_class:flyweight: {'rows': 103, 'accuracy': 0.6019}
- weight_class:heavyweight: {'rows': 99, 'accuracy': 0.5859}
- weight_class:light_heavyweight: {'rows': 90, 'accuracy': 0.6778}
- weight_class:lightweight: {'rows': 175, 'accuracy': 0.5314}
- weight_class:middleweight: {'rows': 175, 'accuracy': 0.5429}
- weight_class:welterweight: {'rows': 148, 'accuracy': 0.5135}
- weight_class:women's_bantamweight: {'rows': 55, 'accuracy': 0.6364}
- weight_class:women's_flyweight: {'rows': 62, 'accuracy': 0.5968}
- weight_class:women's_strawweight: {'rows': 83, 'accuracy': 0.5542}
- enough_fighter_history: {'rows': 1227, 'accuracy': 0.5868}
- low_fighter_history: {'rows': 95, 'accuracy': 0.4211}
### takedown_control_model
- weight_class:bantamweight: {'rows': 281, 'accuracy': 0.6975}
- weight_class:featherweight: {'rows': 283, 'accuracy': 0.7208}
- weight_class:flyweight: {'rows': 194, 'accuracy': 0.732}
- weight_class:heavyweight: {'rows': 172, 'accuracy': 0.7384}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8855}
- weight_class:lightweight: {'rows': 323, 'accuracy': 0.6873}
- weight_class:middleweight: {'rows': 320, 'accuracy': 0.7469}
- weight_class:welterweight: {'rows': 280, 'accuracy': 0.7357}
- weight_class:women's_bantamweight: {'rows': 100, 'accuracy': 0.68}
- weight_class:women's_flyweight: {'rows': 116, 'accuracy': 0.7759}
- weight_class:women's_strawweight: {'rows': 154, 'accuracy': 0.6688}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7121}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8522}
### finish_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8629}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8084}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.8328}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8261}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8327}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8409}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8207}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.82}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8068}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8541}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8292}
- low_fighter_history: {'rows': 341, 'accuracy': 0.824}
### goes_distance_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8629}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.8084}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.8328}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.8261}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.8327}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.8409}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.8207}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7995}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.82}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.8068}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.8541}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.8292}
- low_fighter_history: {'rows': 341, 'accuracy': 0.824}
### method_model
- weight_class:bantamweight: {'rows': 423, 'accuracy': 0.8298}
- weight_class:featherweight: {'rows': 428, 'accuracy': 0.743}
- weight_class:flyweight: {'rows': 293, 'accuracy': 0.7747}
- weight_class:heavyweight: {'rows': 253, 'accuracy': 0.7233}
- weight_class:light_heavyweight: {'rows': 251, 'accuracy': 0.7291}
- weight_class:lightweight: {'rows': 484, 'accuracy': 0.7417}
- weight_class:middleweight: {'rows': 474, 'accuracy': 0.7068}
- weight_class:welterweight: {'rows': 419, 'accuracy': 0.7303}
- weight_class:women's_bantamweight: {'rows': 150, 'accuracy': 0.76}
- weight_class:women's_flyweight: {'rows': 176, 'accuracy': 0.7898}
- weight_class:women's_strawweight: {'rows': 233, 'accuracy': 0.7897}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7589}
- low_fighter_history: {'rows': 341, 'accuracy': 0.7038}

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 3119 | 93.75 | 0.9891 | 0.9891 | 0.9861 | -0.003 | True | True |
| fight_duration_model | >=80% | 2128 | 57.58 | 0.9234 | 0.9233 | 0.9287 | 0.0053 | True | False |
| over_1_5_model | >=80% | 1946 | 52.84 | 0.9147 | 0.8162 | 0.9008 | -0.0139 | True | False |
| over_2_5_model | >=80% | 1822 | 49.47 | 0.9226 | 0.9143 | 0.9066 | -0.016 | True | False |
| ends_before_round_3_model | >=80% | 1691 | 45.91 | 0.916 | 0.8862 | 0.9026 | -0.0134 | True | False |
| finish_in_round_1_model | >=80% | 2463 | 66.87 | 0.9229 | 0.7879 | 0.9212 | -0.0017 | True | False |
| finish_type_model | >=80% | 1174 | 65.37 | 0.8995 | 0.7564 | 0.9524 | 0.0529 | True | False |
| method_umbrella_model | >=80% | 1707 | 46.19 | 0.9233 | 0.7049 | 0.9219 | -0.0014 | True | False |
| strike_volume_model | >=80% | 399 | 30.18 | 0.7644 | 0.7088 | 0.9101 | 0.1457 | False | False |
| takedown_control_model | >=80% | 982 | 39.5 | 0.8697 | 0.7397 | 0.8891 | 0.0194 | True | False |
| finish_model | >=80% | 2128 | 57.58 | 0.9234 | 0.9233 | 0.9287 | 0.0053 | True | False |
| goes_distance_model | >=80% | 2128 | 57.58 | 0.9234 | 0.9233 | 0.9287 | 0.0053 | True | False |
| method_model | >=80% | 1707 | 46.19 | 0.9233 | 0.7049 | 0.9219 | -0.0014 | True | False |
| round_phase_model | >=80% | 1822 | 49.47 | 0.9226 | 0.9143 | 0.9066 | -0.016 | True | False |
| round_model | >=80% | 1822 | 49.47 | 0.9226 | 0.9143 | 0.9066 | -0.016 | True | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |

## Interaction Discovery Summary
| Model | Candidates | Accepted | Selected | Selection Status |
|---|---:|---:|---:|---|
| winner_model | 240 | 80 | 0 | base_features_kept |
| fight_duration_model | 240 | 80 | 5 | selected |
| over_1_5_model | 240 | 80 | 0 | base_features_kept |
| over_2_5_model | 240 | 80 | 0 | base_features_kept |
| ends_before_round_3_model | 240 | 80 | 10 | selected |
| finish_in_round_1_model | 240 | 80 | 0 | base_features_kept |
| finish_type_model | 240 | 80 | 5 | selected |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model |
| strike_volume_model | 240 | 80 | 10 | selected |
| takedown_control_model | 240 | 80 | 0 | base_features_kept |
| finish_model | 240 | 80 | 5 | selected |
| goes_distance_model | 240 | 80 | 5 | selected |
| method_model | 0 | 0 | 0 | not_run_composite_model |
| round_phase_model | 0 | 0 | 0 | not_run_composite_summary |
| round_model | 0 | 0 | 0 | not_run_composite_summary |
| strike_volume_regression | 0 | 0 | 0 | not_run |
| odds_calibration_model | 0 | 0 | 0 | not_run |

## Production Readiness Gates
| Model | Production Status | Passed Gates | Failed Gates | Recommended Use |
|---|---|---|---|---|
| winner_model | high_confidence_only | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, cold_start_low_history_not_dangerously_poor, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, runtime_parity_passes | source_holdout_stable, winner_leakage_audit_passes | research/high-confidence selective predictions only |
| fight_duration_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| over_1_5_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| over_2_5_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| ends_before_round_3_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| finish_in_round_1_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| finish_type_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| method_umbrella_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| takedown_control_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| finish_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| goes_distance_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| method_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| round_phase_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| round_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| strike_volume_regression | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| odds_calibration_model | blocked |  | model_blocked | not available |
