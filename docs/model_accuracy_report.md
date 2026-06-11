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
| fight_duration_model | evaluated | 3327 | 0.8596 | 0.8585 | 0.9309 | 0.106 | 0.5191 | 0.3405 |
| over_1_5_model | evaluated | 3327 | 0.8064 | 0.725 | 0.85 | 0.1364 | 0.6976 | 0.1088 |
| over_2_5_model | evaluated | 3327 | 0.813 | 0.8036 | 0.8917 | 0.1324 | 0.5621 | 0.2509 |
| ends_before_round_3_model | evaluated | 3327 | 0.7911 | 0.7651 | 0.8695 | 0.142 | 0.609 | 0.1821 |
| finish_in_round_1_model | evaluated | 3327 | 0.8467 | 0.72 | 0.8813 | 0.1085 | 0.7628 | 0.0839 |
| finish_type_model | evaluated | 1600 | 0.7956 | 0.704 | None | None | 0.6412 | 0.1544 |
| method_umbrella_model | weak_or_failed_baseline | 3327 | 0.5191 | 0.25 | None | None | 0.5191 | 0.0 |

## Method Probability Logic
- Decision probability comes from the duration model's goes-distance output.
- KO/TKO and submission probabilities are conditional on the fight first being projected to finish.
- The combined method output improved over majority baseline on accuracy, but balanced method metrics remain modest, so it is not production-ready.

## Elo Leakage Audit
- Status: passed
- Feature mode: strict_pre_event_prefight
- Same-event policy: all same-event rows use pre-event Elo by default
- Runtime policy: live predictions may use current computed Elo only for future user-selected fights
- Failed models: None

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
| winner_model | evaluated | 3327 | 0.9606 | 0.52 | 0.4406 | True |  |
| fight_duration_model | evaluated | 3327 | 0.8596 | 0.5191 | 0.3405 | True |  |
| finish_model | evaluated | 3327 | 0.8596 | 0.5191 | 0.3405 | True | Compatibility output: internally backed by fight_duration_model. |
| goes_distance_model | evaluated | 3327 | 0.8596 | 0.5191 | 0.3405 | True | Compatibility output: goes_distance_probability is derived as 1 - finish_probability. |
| over_2_5_model | evaluated | 3327 | 0.813 | 0.5621 | 0.2509 | True |  |
| round_phase_model | evaluated | 3327 | 0.813 | 0.5621 | 0.2509 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels. |
| round_model | evaluated | 3327 | 0.813 | 0.5621 | 0.2509 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Compatibility alias backed by round_phase_model. |
| strike_volume_model | evaluated | 1322 | 0.5908 | 0.3623 | 0.2285 | True |  |
| ends_before_round_3_model | evaluated | 3327 | 0.7911 | 0.609 | 0.1821 | True |  |
| finish_type_model | evaluated | 1600 | 0.7956 | 0.6412 | 0.1544 | True | Conditional model: trained and scored only on fights that actually finished. |
| takedown_control_model | evaluated | 2486 | 0.7349 | 0.5897 | 0.1452 | True |  |
| over_1_5_model | evaluated | 3327 | 0.8064 | 0.6976 | 0.1088 | True |  |
| finish_in_round_1_model | evaluated | 3327 | 0.8467 | 0.7628 | 0.0839 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| method_umbrella_model | weak_or_failed_baseline | 3327 | 0.5191 | 0.5191 | 0.0 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context.; Umbrella method output combines duration probability with conditional finish type probabilities. |
| method_model | weak_or_failed_baseline | 3327 | 0.5191 | 0.5191 | 0.0 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context.; Umbrella method output combines duration probability with conditional finish type probabilities.; Compatibility alias backed by method_umbrella_model. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Source-Holdout Transfer Summary
| Model | Normal Metric | Worst Source Metric | Drop | Worst Source | Rows | Source-Holdout Status | Production Status |
|---|---:|---:|---:|---|---:|---|---|
| winner_model | 0.9606 | 0.8764 | 0.0842 | ufc_1994_2025 | 914 | needs_review | high_confidence_only |
| fight_duration_model | 0.8596 | 0.8234 | 0.0362 | mdabbert_ultimate | 1189 | stable | production_candidate |
| over_1_5_model | 0.8064 | 0.7912 | 0.0152 | ufc_1994_2026 | 1164 | stable | production_candidate |
| over_2_5_model | 0.813 | 0.7954 | 0.0176 | ufc_1994_2025 | 914 | stable | production_candidate |
| ends_before_round_3_model | 0.7911 | 0.7801 | 0.011 | ufc_1994_2025 | 914 | stable | production_candidate |
| finish_in_round_1_model | 0.8467 | 0.8256 | 0.0211 | ufc_1994_2026 | 1164 | stable | production_candidate |
| finish_type_model | 0.7956 | 0.7855 | 0.0101 | ufc_1994_2026 | 564 | needs_review | experimental |
| method_umbrella_model | 0.5191 | 0.5155 | 0.0036 | ufc_1994_2026 | 1164 | unstable | weak_or_failed_baseline |
| strike_volume_model | 0.5908 | 0.4321 | 0.1587 | ufc_stats_complete | 361 | unstable | experimental |
| takedown_control_model | 0.7349 | 0.6343 | 0.1006 | ufc_stats_complete | 361 | needs_review | experimental |
| finish_model | 0.8596 | 0.8234 | 0.0362 | mdabbert_ultimate | 1189 | stable | production_candidate |
| goes_distance_model | 0.8596 | 0.8234 | 0.0362 | mdabbert_ultimate | 1189 | stable | production_candidate |
| method_model | 0.5191 | 0.5155 | 0.0036 | ufc_1994_2026 | 1164 | unstable | weak_or_failed_baseline |
| round_phase_model | 0.813 | 0.7954 | 0.0176 | ufc_1994_2025 | 914 | stable | experimental |
| round_model | 0.813 | 0.7954 | 0.0176 | ufc_1994_2025 | 914 | stable | experimental |
| strike_volume_regression | 52.6679 |  |  |  |  | not_run | weak_or_failed_baseline |
| odds_calibration_model |  |  |  |  |  | not_run | blocked |

## Segment Performance
### winner_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.953}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.9635}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.9586}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.9398}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.9777}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.9633}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.9618}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.9791}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.9556}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9816}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9624}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.9674}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8821}
### fight_duration_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.893}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8411}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8722}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8657}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8705}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8784}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8329}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.8355}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8148}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.865}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8685}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.8584}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8745}
### over_1_5_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.893}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.7839}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8346}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.7778}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7321}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.805}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7327}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7546}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7926}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8896}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9061}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.8052}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8213}
### over_2_5_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.8956}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8047}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8271}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8519}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7812}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.7798}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.7995}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7337}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7778}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8282}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8779}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.8084}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8669}
### ends_before_round_3_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.8433}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.7552}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.7669}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8009}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7768}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.7546}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.778}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.7467}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.7926}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.8773}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8545}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.7892}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8137}
### finish_in_round_1_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.9191}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8151}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8722}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8009}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.7321}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8417}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.778}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.8355}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8963}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.9264}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.9577}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.8424}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8973}
### finish_type_model
- weight_class:bantamweight: {'rows': 120, 'accuracy': 0.7417}
- weight_class:featherweight: {'rows': 211, 'accuracy': 0.8578}
- weight_class:flyweight: {'rows': 124, 'accuracy': 0.8226}
- weight_class:heavyweight: {'rows': 111, 'accuracy': 0.7838}
- weight_class:light_heavyweight: {'rows': 146, 'accuracy': 0.8562}
- weight_class:lightweight: {'rows': 217, 'accuracy': 0.7373}
- weight_class:middleweight: {'rows': 245, 'accuracy': 0.7837}
- weight_class:welterweight: {'rows': 217, 'accuracy': 0.8249}
- weight_class:women's_bantamweight: {'rows': 54, 'accuracy': 0.7222}
- weight_class:women's_strawweight: {'rows': 65, 'accuracy': 0.6154}
- enough_fighter_history: {'rows': 1448, 'accuracy': 0.8039}
- low_fighter_history: {'rows': 152, 'accuracy': 0.7171}
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
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.5274}
- low_fighter_history: {'rows': 263, 'accuracy': 0.4221}
### strike_volume_model
- weight_class:bantamweight: {'rows': 150, 'accuracy': 0.62}
- weight_class:featherweight: {'rows': 154, 'accuracy': 0.5909}
- weight_class:flyweight: {'rows': 103, 'accuracy': 0.6117}
- weight_class:heavyweight: {'rows': 99, 'accuracy': 0.6364}
- weight_class:light_heavyweight: {'rows': 90, 'accuracy': 0.6}
- weight_class:lightweight: {'rows': 175, 'accuracy': 0.5714}
- weight_class:middleweight: {'rows': 175, 'accuracy': 0.5486}
- weight_class:welterweight: {'rows': 148, 'accuracy': 0.5676}
- weight_class:women's_bantamweight: {'rows': 55, 'accuracy': 0.6182}
- weight_class:women's_flyweight: {'rows': 62, 'accuracy': 0.5484}
- weight_class:women's_strawweight: {'rows': 83, 'accuracy': 0.6265}
- enough_fighter_history: {'rows': 1084, 'accuracy': 0.5526}
- low_fighter_history: {'rows': 238, 'accuracy': 0.7647}
### takedown_control_model
- weight_class:bantamweight: {'rows': 281, 'accuracy': 0.726}
- weight_class:featherweight: {'rows': 283, 'accuracy': 0.7067}
- weight_class:flyweight: {'rows': 194, 'accuracy': 0.7268}
- weight_class:heavyweight: {'rows': 172, 'accuracy': 0.7384}
- weight_class:light_heavyweight: {'rows': 166, 'accuracy': 0.8916}
- weight_class:lightweight: {'rows': 323, 'accuracy': 0.6997}
- weight_class:middleweight: {'rows': 320, 'accuracy': 0.7438}
- weight_class:welterweight: {'rows': 280, 'accuracy': 0.7536}
- weight_class:women's_bantamweight: {'rows': 100, 'accuracy': 0.7}
- weight_class:women's_flyweight: {'rows': 116, 'accuracy': 0.7931}
- weight_class:women's_strawweight: {'rows': 154, 'accuracy': 0.6494}
- enough_fighter_history: {'rows': 2199, 'accuracy': 0.7244}
- low_fighter_history: {'rows': 287, 'accuracy': 0.8153}
### finish_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.893}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8411}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8722}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8657}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8705}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8784}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8329}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.8355}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8148}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.865}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8685}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.8584}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8745}
### goes_distance_model
- weight_class:bantamweight: {'rows': 383, 'accuracy': 0.893}
- weight_class:featherweight: {'rows': 384, 'accuracy': 0.8411}
- weight_class:flyweight: {'rows': 266, 'accuracy': 0.8722}
- weight_class:heavyweight: {'rows': 216, 'accuracy': 0.8657}
- weight_class:light_heavyweight: {'rows': 224, 'accuracy': 0.8705}
- weight_class:lightweight: {'rows': 436, 'accuracy': 0.8784}
- weight_class:middleweight: {'rows': 419, 'accuracy': 0.8329}
- weight_class:welterweight: {'rows': 383, 'accuracy': 0.8355}
- weight_class:women's_bantamweight: {'rows': 135, 'accuracy': 0.8148}
- weight_class:women's_flyweight: {'rows': 163, 'accuracy': 0.865}
- weight_class:women's_strawweight: {'rows': 213, 'accuracy': 0.8685}
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.8584}
- low_fighter_history: {'rows': 263, 'accuracy': 0.8745}
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
- enough_fighter_history: {'rows': 3064, 'accuracy': 0.5274}
- low_fighter_history: {'rows': 263, 'accuracy': 0.4221}

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 3059 | 91.94 | 0.9889 | 0.9889 | 0.9827 | -0.0062 | True | True |
| fight_duration_model | >=80% | 1912 | 57.47 | 0.9613 | 0.9613 | 0.9337 | -0.0276 | True | True |
| over_1_5_model | >=80% | 1855 | 55.76 | 0.9175 | 0.8099 | 0.9012 | -0.0163 | True | False |
| over_2_5_model | >=80% | 1647 | 49.5 | 0.9405 | 0.9316 | 0.9086 | -0.0319 | True | False |
| ends_before_round_3_model | >=80% | 1626 | 48.87 | 0.9354 | 0.9066 | 0.9059 | -0.0295 | True | False |
| finish_in_round_1_model | >=80% | 2284 | 68.65 | 0.9304 | 0.796 | 0.9209 | -0.0095 | True | False |
| finish_type_model | >=80% | 1075 | 67.19 | 0.947 | 0.9462 | 0.9584 | 0.0114 | True | False |
| method_umbrella_model | >=55% | 3327 | 100.0 | 0.5191 | 0.25 | 1.0 | 0.4809 | False | False |
| strike_volume_model | >=80% | 392 | 29.65 | 0.7832 | 0.7375 | 0.9062 | 0.1231 | False | False |
| takedown_control_model | >=80% | 1006 | 40.47 | 0.8777 | 0.7456 | 0.8876 | 0.0099 | True | False |
| finish_model | >=80% | 1912 | 57.47 | 0.9613 | 0.9613 | 0.9337 | -0.0276 | True | True |
| goes_distance_model | >=80% | 1912 | 57.47 | 0.9613 | 0.9613 | 0.9337 | -0.0276 | True | True |
| method_model | >=55% | 3327 | 100.0 | 0.5191 | 0.25 | 1.0 | 0.4809 | False | False |
| round_phase_model | >=80% | 1647 | 49.5 | 0.9405 | 0.9316 | 0.9086 | -0.0319 | True | False |
| round_model | >=80% | 1647 | 49.5 | 0.9405 | 0.9316 | 0.9086 | -0.0319 | True | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |

## Interaction Discovery Summary
| Model | Candidates | Accepted | Selected | Selection Status |
|---|---:|---:|---:|---|
| winner_model | 240 | 80 | 0 | base_features_kept |
| fight_duration_model | 240 | 80 | 5 | selected |
| over_1_5_model | 240 | 80 | 20 | selected |
| over_2_5_model | 240 | 80 | 0 | base_features_kept |
| ends_before_round_3_model | 240 | 80 | 20 | selected |
| finish_in_round_1_model | 240 | 80 | 0 | base_features_kept |
| finish_type_model | 240 | 80 | 0 | base_features_kept |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model |
| strike_volume_model | 240 | 80 | 5 | selected |
| takedown_control_model | 240 | 80 | 10 | selected |
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
| fight_duration_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| over_1_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| over_2_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| ends_before_round_3_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_in_round_1_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_type_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| method_umbrella_model | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_regression, source_holdout_unstable | research only |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | interaction_source_holdout_regression, source_holdout_regression, source_holdout_unstable | research only until source-holdout stabilizes |
| takedown_control_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_unstable | research only until source-holdout stabilizes |
| finish_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| goes_distance_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists, source_holdout_stable |  | candidate for limited internal validation; artifact packaging still requires explicit review |
| method_model | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, source_holdout_regression, source_holdout_unstable | research only |
| round_phase_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists, source_holdout_stable | balanced_accuracy_not_dangerously_low, calibration_acceptable | research only |
| round_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists, source_holdout_stable | balanced_accuracy_not_dangerously_low, calibration_acceptable | research only |
| strike_volume_regression | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| odds_calibration_model | blocked |  | model_blocked | not available |
