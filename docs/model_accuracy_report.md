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
| fight_duration_model | evaluated | 3327 | 0.8596 | 0.8586 | 0.9325 | 0.1052 | 0.5191 | 0.3405 |
| over_1_5_model | evaluated | 3327 | 0.7947 | 0.7005 | 0.8441 | 0.1387 | 0.6976 | 0.0971 |
| over_2_5_model | evaluated | 3327 | 0.8197 | 0.8082 | 0.897 | 0.1299 | 0.5621 | 0.2576 |
| ends_before_round_3_model | evaluated | 3327 | 0.7926 | 0.7698 | 0.8726 | 0.1401 | 0.609 | 0.1836 |
| finish_in_round_1_model | evaluated | 3327 | 0.8437 | 0.7041 | 0.8747 | 0.1118 | 0.7628 | 0.0809 |
| finish_type_model | evaluated | 1600 | 0.7956 | 0.7032 | None | None | 0.6412 | 0.1544 |
| method_umbrella_model | weak_or_failed_baseline | 3327 | 0.5191 | 0.25 | None | None | 0.5191 | 0.0 |

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
| fight_duration_model | evaluated | 3327 | 0.8596 | 0.5191 | 0.3405 | True |  |
| finish_model | evaluated | 3327 | 0.8596 | 0.5191 | 0.3405 | True | Compatibility output: internally backed by fight_duration_model. |
| goes_distance_model | evaluated | 3327 | 0.8596 | 0.5191 | 0.3405 | True | Compatibility output: goes_distance_probability is derived as 1 - finish_probability. |
| over_2_5_model | evaluated | 3327 | 0.8197 | 0.5621 | 0.2576 | True |  |
| round_phase_model | evaluated | 3327 | 0.8197 | 0.5621 | 0.2576 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels. |
| round_model | evaluated | 3327 | 0.8197 | 0.5621 | 0.2576 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Compatibility alias backed by round_phase_model. |
| strike_volume_model | evaluated | 1322 | 0.5749 | 0.3623 | 0.2126 | True |  |
| ends_before_round_3_model | evaluated | 3327 | 0.7926 | 0.609 | 0.1836 | True |  |
| finish_type_model | evaluated | 1600 | 0.7956 | 0.6412 | 0.1544 | True | Conditional model: trained and scored only on fights that actually finished. |
| takedown_control_model | evaluated | 2486 | 0.7285 | 0.5897 | 0.1388 | True |  |
| over_1_5_model | evaluated | 3327 | 0.7947 | 0.6976 | 0.0971 | True |  |
| finish_in_round_1_model | evaluated | 3327 | 0.8437 | 0.7628 | 0.0809 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| method_umbrella_model | weak_or_failed_baseline | 3327 | 0.5191 | 0.5191 | 0.0 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context.; Umbrella method output combines duration probability with conditional finish type probabilities. |
| method_model | weak_or_failed_baseline | 3327 | 0.5191 | 0.5191 | 0.0 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context.; Umbrella method output combines duration probability with conditional finish type probabilities.; Compatibility alias backed by method_umbrella_model. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Source-Holdout Transfer Summary
| Model | Normal Metric | Worst Source Metric | Drop | Worst Source | Rows | Source-Holdout Status | Production Status |
|---|---:|---:|---:|---|---:|---|---|
| winner_model | 0.9621 | 0.8222 | 0.1399 | ufc_1994_2026 | 1164 | needs_review | high_confidence_only |
| fight_duration_model | 0.8596 | 0.7826 | 0.077 | ufc_1994_2026 | 1164 | stable | production_candidate |
| over_1_5_model | 0.7947 | 0.7715 | 0.0232 | ufc_1994_2026 | 1164 | stable | production_candidate |
| over_2_5_model | 0.8197 | 0.7534 | 0.0663 | ufc_1994_2026 | 1164 | stable | production_candidate |
| ends_before_round_3_model | 0.7926 | 0.7552 | 0.0374 | ufc_1994_2026 | 1164 | stable | production_candidate |
| finish_in_round_1_model | 0.8437 | 0.817 | 0.0267 | ufc_1994_2026 | 1164 | stable | production_candidate |
| finish_type_model | 0.7956 | 0.8512 | -0.0556 | ufc_1994_2025 | 430 | needs_review | experimental |
| method_umbrella_model | 0.5191 | 0.5155 | 0.0036 | ufc_1994_2026 | 1164 | unstable | weak_or_failed_baseline |
| strike_volume_model | 0.5749 | 0.4155 | 0.1594 | ufc_stats_complete | 361 | unstable | experimental |
| takedown_control_model | 0.7285 | 0.6343 | 0.0942 | ufc_stats_complete | 361 | needs_review | experimental |
| finish_model | 0.8596 | 0.7826 | 0.077 | ufc_1994_2026 | 1164 | stable | production_candidate |
| goes_distance_model | 0.8596 | 0.7826 | 0.077 | ufc_1994_2026 | 1164 | stable | production_candidate |
| method_model | 0.5191 | 0.5155 | 0.0036 | ufc_1994_2026 | 1164 | unstable | weak_or_failed_baseline |
| round_phase_model | 0.8197 | 0.7534 | 0.0663 | ufc_1994_2026 | 1164 | stable | experimental |
| round_model | 0.8197 | 0.7534 | 0.0663 | ufc_1994_2026 | 1164 | stable | experimental |
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
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.906}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8438}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8684}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8657}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8527}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8532}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8473}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.846}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8296}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8528}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8779}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.8585}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8727}
### over_1_5_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.8799}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.7604}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8045}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.7454}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7098}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8005}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7422}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7441}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7926}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9018}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8873}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.7928}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8165}
### over_2_5_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.8982}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8047}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8271}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8426}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8259}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.7844}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8138}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7363}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7926}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8405}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8826}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.816}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8614}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.846}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.75}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.782}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.7917}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7768}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.7752}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7947}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7415}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7704}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8466}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8545}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.7905}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8165}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.9217}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8203}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.891}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8148}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7232}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8257}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7685}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.8068}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.9037}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9387}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9577}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.8392}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8951}
### finish_type_model
- weight_class:bantamweight: {'rows': 120, 'accuracy': 0.775}
- weight_class:featherweight: {'rows': 211, 'accuracy': 0.8341}
- weight_class:flyweight: {'rows': 124, 'accuracy': 0.8387}
- weight_class:heavyweight: {'rows': 111, 'accuracy': 0.7928}
- weight_class:light_heavyweight: {'rows': 146, 'accuracy': 0.8425}
- weight_class:lightweight: {'rows': 217, 'accuracy': 0.7373}
- weight_class:middleweight: {'rows': 245, 'accuracy': 0.7796}
- weight_class:welterweight: {'rows': 217, 'accuracy': 0.8203}
- weight_class:women's_bantamweight: {'rows': 54, 'accuracy': 0.7778}
- weight_class:women's_strawweight: {'rows': 65, 'accuracy': 0.5846}
- enough_fighter_history: {'rows': 1446, 'accuracy': 0.8057}
- low_fighter_history: {'rows': 154, 'accuracy': 0.7013}
### method_umbrella_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.6867}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.4505}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.5338}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.4861}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.3482}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.5023}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.4153}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.4334}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.6}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.7485}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.6948}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.5275}
- low_fighter_history: {'rows': 267, 'accuracy': 0.4232}
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
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.906}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8438}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8684}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8657}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8527}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8532}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8473}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.846}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8296}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8528}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8779}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.8585}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8727}
### goes_distance_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.906}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8438}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8684}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8657}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8527}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8532}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8473}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.846}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8296}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8528}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8779}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.8585}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8727}
### method_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.6867}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.4505}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.5338}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.4861}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.3482}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.5023}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.4153}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.4334}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.6}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.7485}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.6948}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.5275}
- low_fighter_history: {'rows': 267, 'accuracy': 0.4232}

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 3119 | 93.75 | 0.9891 | 0.9891 | 0.9861 | -0.003 | True | True |
| fight_duration_model | >=80% | 1877 | 56.42 | 0.9659 | 0.9659 | 0.9341 | -0.0318 | True | True |
| over_1_5_model | >=80% | 1837 | 55.21 | 0.9178 | 0.8061 | 0.9027 | -0.0151 | True | False |
| over_2_5_model | >=80% | 1636 | 49.17 | 0.9444 | 0.9357 | 0.9075 | -0.0369 | True | False |
| ends_before_round_3_model | >=80% | 1575 | 47.34 | 0.9384 | 0.9163 | 0.9046 | -0.0338 | True | False |
| finish_in_round_1_model | >=80% | 2293 | 68.92 | 0.9311 | 0.7936 | 0.9239 | -0.0072 | True | False |
| finish_type_model | >=80% | 1089 | 68.06 | 0.9348 | 0.9368 | 0.9573 | 0.0225 | True | False |
| method_umbrella_model | >=55% | 3327 | 100.0 | 0.5191 | 0.25 | 1.0 | 0.4809 | False | False |
| strike_volume_model | >=80% | 399 | 30.18 | 0.7644 | 0.7088 | 0.9101 | 0.1457 | False | False |
| takedown_control_model | >=80% | 982 | 39.5 | 0.8697 | 0.7397 | 0.8891 | 0.0194 | True | False |
| finish_model | >=80% | 1877 | 56.42 | 0.9659 | 0.9659 | 0.9341 | -0.0318 | True | True |
| goes_distance_model | >=80% | 1877 | 56.42 | 0.9659 | 0.9659 | 0.9341 | -0.0318 | True | True |
| method_model | >=55% | 3327 | 100.0 | 0.5191 | 0.25 | 1.0 | 0.4809 | False | False |
| round_phase_model | >=80% | 1636 | 49.17 | 0.9444 | 0.9357 | 0.9075 | -0.0369 | True | False |
| round_model | >=80% | 1636 | 49.17 | 0.9444 | 0.9357 | 0.9075 | -0.0369 | True | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |

## Interaction Discovery Summary
| Model | Candidates | Accepted | Selected | Selection Status |
|---|---:|---:|---:|---|
| winner_model | 240 | 80 | 0 | base_features_kept |
| fight_duration_model | 240 | 80 | 20 | selected |
| over_1_5_model | 240 | 80 | 10 | selected |
| over_2_5_model | 240 | 80 | 5 | selected |
| ends_before_round_3_model | 240 | 80 | 0 | base_features_kept |
| finish_in_round_1_model | 240 | 80 | 5 | selected |
| finish_type_model | 240 | 80 | 0 | base_features_kept |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model |
| strike_volume_model | 240 | 80 | 10 | selected |
| takedown_control_model | 240 | 80 | 0 | base_features_kept |
| finish_model | 240 | 80 | 20 | selected |
| goes_distance_model | 240 | 80 | 20 | selected |
| method_model | 0 | 0 | 0 | not_run_composite_model |
| round_phase_model | 0 | 0 | 0 | not_run_composite_summary |
| round_model | 0 | 0 | 0 | not_run_composite_summary |
| strike_volume_regression | 0 | 0 | 0 | not_run |
| odds_calibration_model | 0 | 0 | 0 | not_run |

## Production Readiness Gates
| Model | Production Status | Passed Gates | Failed Gates | Recommended Use |
|---|---|---|---|---|
| winner_model | high_confidence_only | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, cold_start_low_history_not_dangerously_poor, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, runtime_parity_passes | source_holdout_stable, winner_leakage_audit_passes | research/high-confidence selective predictions only |
| fight_duration_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| over_1_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| over_2_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| ends_before_round_3_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_in_round_1_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_type_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| method_umbrella_model | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_regression, source_holdout_unstable | research only |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| takedown_control_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| finish_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| goes_distance_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| method_model | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_regression, source_holdout_unstable | research only |
| round_phase_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists, source_holdout_stable | balanced_accuracy_not_dangerously_low, calibration_acceptable | research only |
| round_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists, source_holdout_stable | balanced_accuracy_not_dangerously_low, calibration_acceptable | research only |
| strike_volume_regression | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| odds_calibration_model | blocked |  | model_blocked | not available |
