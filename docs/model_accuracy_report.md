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
| fight_duration_model | evaluated | 3696 | 0.8285 | 0.8278 | 0.9139 | 0.1197 | 0.5141 | 0.3144 |
| over_1_5_model | evaluated | 3683 | 0.7907 | 0.7183 | 0.8494 | 0.139 | 0.6964 | 0.0943 |
| over_2_5_model | evaluated | 3683 | 0.8086 | 0.8008 | 0.891 | 0.1331 | 0.5599 | 0.2487 |
| ends_before_round_3_model | evaluated | 3683 | 0.7934 | 0.7769 | 0.875 | 0.1399 | 0.6066 | 0.1868 |
| finish_in_round_1_model | evaluated | 3683 | 0.8298 | 0.7086 | 0.871 | 0.1169 | 0.7613 | 0.0685 |
| finish_type_model | evaluated | 1796 | 0.7812 | 0.6454 | None | None | 0.632 | 0.1492 |
| method_umbrella_model | evaluated | 3696 | 0.7484 | 0.5836 | None | None | 0.5141 | 0.2343 |

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
| winner_model | evaluated | 3327 | 0.9585 | 0.52 | 0.4385 | True |  |
| fight_duration_model | evaluated | 3696 | 0.8285 | 0.5141 | 0.3144 | True |  |
| finish_model | evaluated | 3696 | 0.8285 | 0.5141 | 0.3144 | True | Compatibility output: internally backed by fight_duration_model. |
| goes_distance_model | evaluated | 3696 | 0.8285 | 0.5141 | 0.3144 | True | Compatibility output: goes_distance_probability is derived as 1 - finish_probability. |
| over_2_5_model | evaluated | 3683 | 0.8086 | 0.5599 | 0.2487 | True |  |
| round_phase_model | evaluated | 3683 | 0.8086 | 0.5599 | 0.2487 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels. |
| round_model | evaluated | 3683 | 0.8086 | 0.5599 | 0.2487 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Compatibility alias backed by round_phase_model. |
| method_umbrella_model | evaluated | 3696 | 0.7484 | 0.5141 | 0.2343 | True | Umbrella method output combines duration probability with conditional finish type probabilities. |
| method_model | evaluated | 3696 | 0.7484 | 0.5141 | 0.2343 | True | Umbrella method output combines duration probability with conditional finish type probabilities.; Compatibility alias backed by method_umbrella_model. |
| strike_volume_model | evaluated | 1322 | 0.5825 | 0.3623 | 0.2202 | True |  |
| ends_before_round_3_model | evaluated | 3683 | 0.7934 | 0.6066 | 0.1868 | True |  |
| finish_type_model | evaluated | 1796 | 0.7812 | 0.632 | 0.1492 | True | Conditional model: trained and scored only on fights that actually finished. |
| takedown_control_model | evaluated | 2486 | 0.7385 | 0.5897 | 0.1488 | True |  |
| over_1_5_model | evaluated | 3683 | 0.7907 | 0.6964 | 0.0943 | True |  |
| finish_in_round_1_model | evaluated | 3683 | 0.8298 | 0.7613 | 0.0685 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Segment Performance
### winner_model
- weight_class:Bantamweight: {'rows': 146, 'accuracy': 0.9589}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.916}
- weight_class:Featherweight: {'rows': 147, 'accuracy': 0.966}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.9225}
- weight_class:Flyweight: {'rows': 102, 'accuracy': 0.9608}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.9011}
- weight_class:Heavyweight: {'rows': 88, 'accuracy': 0.9659}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863}
- weight_class:Light Heavyweight: {'rows': 85, 'accuracy': 0.9882}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.9474}
- weight_class:Lightweight: {'rows': 163, 'accuracy': 0.9632}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.9257}
- weight_class:Middleweight: {'rows': 161, 'accuracy': 0.9565}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.9172}
- weight_class:Welterweight: {'rows': 143, 'accuracy': 0.979}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.9394}
- weight_class:Women's Bantamweight: {'rows': 53, 'accuracy': 0.9245}
- weight_class:Women's Flyweight: {'rows': 60, 'accuracy': 0.9833}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.963}
- weight_class:Women's Strawweight: {'rows': 81, 'accuracy': 0.963}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9296}
- weight_class:bantamweight: {'rows': 106, 'accuracy': 1.0}
- weight_class:featherweight: {'rows': 108, 'accuracy': 1.0}
- weight_class:flyweight: {'rows': 73, 'accuracy': 1.0}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 1.0}
- weight_class:light heavyweight: {'rows': 63, 'accuracy': 1.0}
- weight_class:lightweight: {'rows': 125, 'accuracy': 1.0}
- weight_class:middleweight: {'rows': 113, 'accuracy': 1.0}
- weight_class:welterweight: {'rows': 108, 'accuracy': 1.0}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 1.0}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9654}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8801}
### fight_duration_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.8054}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.8063}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7907}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7984}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.744}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.8545}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.7571}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8378}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.7887}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7584}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7879}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.8235}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.8218}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8981}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8615}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8968}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8707}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8349}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.828}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328}
### over_1_5_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.8533}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.855}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7249}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7674}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.7422}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7016}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7671}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.6697}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6974}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.7633}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8041}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.684}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7172}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7978}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7652}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.791}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.8472}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9259}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.92}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9155}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8785}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8519}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8219}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.8}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7538}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.7937}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7414}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8073}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7904}
- low_fighter_history: {'rows': 338, 'accuracy': 0.7929}
### over_2_5_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.837}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7566}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7597}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.7188}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7582}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7823}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8219}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.7706}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8421}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.7343}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7568}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.8019}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8276}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7528}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7197}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.791}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.8056}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.86}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8873}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8519}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9091}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8308}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8175}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8621}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7982}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.918}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8033}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8609}
### ends_before_round_3_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.8315}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8473}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7037}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7364}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.6797}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7143}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7903}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.7431}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.7343}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7568}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.7689}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8276}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7528}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7576}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.7463}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.7639}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.86}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8873}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8692}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8056}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8493}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8333}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8017}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8073}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.8689}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.7895}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8314}
### finish_in_round_1_model
- weight_class:Bantamweight: {'rows': 184, 'accuracy': 0.8913}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.9237}
- weight_class:Featherweight: {'rows': 189, 'accuracy': 0.7937}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8217}
- weight_class:Flyweight: {'rows': 128, 'accuracy': 0.8125}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242}
- weight_class:Heavyweight: {'rows': 124, 'accuracy': 0.7581}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8082}
- weight_class:Light Heavyweight: {'rows': 109, 'accuracy': 0.6881}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6711}
- weight_class:Lightweight: {'rows': 207, 'accuracy': 0.8116}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446}
- weight_class:Middleweight: {'rows': 212, 'accuracy': 0.7642}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7379}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7865}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955}
- weight_class:Women's Bantamweight: {'rows': 67, 'accuracy': 0.8955}
- weight_class:Women's Flyweight: {'rows': 72, 'accuracy': 0.8472}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9259}
- weight_class:Women's Strawweight: {'rows': 100, 'accuracy': 0.97}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.9577}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9252}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8611}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.8182}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7385}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8333}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7931}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8073}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9508}
- enough_fighter_history: {'rows': 3345, 'accuracy': 0.8284}
- low_fighter_history: {'rows': 338, 'accuracy': 0.8432}
### finish_type_model
- weight_class:Bantamweight: {'rows': 56, 'accuracy': 0.625}
- weight_class:Featherweight: {'rows': 106, 'accuracy': 0.7925}
- weight_class:Featherweight Bout: {'rows': 71, 'accuracy': 0.7746}
- weight_class:Flyweight: {'rows': 64, 'accuracy': 0.8125}
- weight_class:Heavyweight: {'rows': 63, 'accuracy': 0.8095}
- weight_class:Light Heavyweight: {'rows': 77, 'accuracy': 0.7662}
- weight_class:Lightweight: {'rows': 114, 'accuracy': 0.7193}
- weight_class:Lightweight Bout: {'rows': 75, 'accuracy': 0.7333}
- weight_class:Middleweight: {'rows': 126, 'accuracy': 0.7381}
- weight_class:Middleweight Bout: {'rows': 87, 'accuracy': 0.7931}
- weight_class:Welterweight: {'rows': 97, 'accuracy': 0.8247}
- weight_class:Welterweight Bout: {'rows': 76, 'accuracy': 0.7763}
- weight_class:featherweight: {'rows': 58, 'accuracy': 0.8793}
- weight_class:lightweight: {'rows': 60, 'accuracy': 0.75}
- weight_class:middleweight: {'rows': 67, 'accuracy': 0.8507}
- weight_class:welterweight: {'rows': 62, 'accuracy': 0.871}
- enough_fighter_history: {'rows': 1599, 'accuracy': 0.7942}
- low_fighter_history: {'rows': 197, 'accuracy': 0.6751}
### method_umbrella_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.7676}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.712}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7364}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7132}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7912}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.616}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.726}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.7182}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.75}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.6714}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7162}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.6385}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7241}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.6573}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7045}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.75}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.7624}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8028}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8692}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8241}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8493}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7818}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7692}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8016}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7672}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7798}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.8361}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7547}
- low_fighter_history: {'rows': 341, 'accuracy': 0.6862}
### strike_volume_model
- weight_class:Middleweight: {'rows': 59, 'accuracy': 0.5085}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.7196}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.6296}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.6575}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7091}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7077}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6429}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.6121}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5872}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6066}
- enough_fighter_history: {'rows': 1227, 'accuracy': 0.5974}
- low_fighter_history: {'rows': 95, 'accuracy': 0.3895}
### takedown_control_model
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7634}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7287}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7692}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.9079}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7703}
- weight_class:Middleweight: {'rows': 59, 'accuracy': 0.6102}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7793}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7576}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7963}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6761}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8131}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.7315}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.7945}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7455}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8923}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6746}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7414}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7339}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6885}
- enough_fighter_history: {'rows': 2195, 'accuracy': 0.7262}
- low_fighter_history: {'rows': 291, 'accuracy': 0.8316}
### finish_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.8054}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.8063}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7907}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7984}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.744}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.8545}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.7571}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8378}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.7887}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7584}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7879}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.8235}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.8218}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8981}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8615}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8968}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8707}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8349}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.828}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328}
### goes_distance_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.8054}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8779}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.8063}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7907}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7984}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8242}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.744}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.863}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.8545}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8289}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.7571}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8378}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.7887}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.7584}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7879}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.8235}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.8218}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.9159}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8981}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8767}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9273}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.8615}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8968}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.8707}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.8349}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9016}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.828}
- low_fighter_history: {'rows': 341, 'accuracy': 0.8328}
### method_model
- weight_class:Bantamweight: {'rows': 185, 'accuracy': 0.7676}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626}
- weight_class:Featherweight: {'rows': 191, 'accuracy': 0.712}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7364}
- weight_class:Flyweight: {'rows': 129, 'accuracy': 0.7132}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7912}
- weight_class:Heavyweight: {'rows': 125, 'accuracy': 0.616}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.726}
- weight_class:Light Heavyweight: {'rows': 110, 'accuracy': 0.7182}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.75}
- weight_class:Lightweight: {'rows': 210, 'accuracy': 0.6714}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7162}
- weight_class:Middleweight: {'rows': 213, 'accuracy': 0.6385}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7241}
- weight_class:Welterweight: {'rows': 178, 'accuracy': 0.6573}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7045}
- weight_class:Women's Bantamweight: {'rows': 68, 'accuracy': 0.75}
- weight_class:Women's Flyweight: {'rows': 73, 'accuracy': 0.7671}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8704}
- weight_class:Women's Strawweight: {'rows': 101, 'accuracy': 0.7624}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8028}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.8692}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.8241}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.8493}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.7818}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.7692}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.8016}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7672}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.7798}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.8361}
- enough_fighter_history: {'rows': 3355, 'accuracy': 0.7547}
- low_fighter_history: {'rows': 341, 'accuracy': 0.6862}

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 3114 | 93.6 | 0.9894 | 0.9894 | 0.9874 | -0.002 | True | True |
| fight_duration_model | >=80% | 2430 | 65.75 | 0.9251 | 0.9252 | 0.9474 | 0.0223 | True | False |
| over_1_5_model | >=80% | 2228 | 60.49 | 0.9093 | 0.8234 | 0.9265 | 0.0172 | True | False |
| over_2_5_model | >=80% | 2170 | 58.92 | 0.9184 | 0.911 | 0.9274 | 0.009 | True | False |
| ends_before_round_3_model | >=80% | 2140 | 58.1 | 0.9178 | 0.8984 | 0.9216 | 0.0039 | True | False |
| finish_in_round_1_model | >=80% | 2644 | 71.79 | 0.9172 | 0.7978 | 0.9421 | 0.025 | True | False |
| finish_type_model | >=80% | 1280 | 71.27 | 0.8867 | 0.7269 | 0.9613 | 0.0746 | True | False |
| method_umbrella_model | >=80% | 2072 | 56.06 | 0.9126 | 0.7303 | 0.9405 | 0.0279 | True | False |
| strike_volume_model | >=80% | 492 | 37.22 | 0.75 | 0.7065 | 0.9203 | 0.1703 | False | False |
| takedown_control_model | >=80% | 1121 | 45.09 | 0.8662 | 0.7678 | 0.9068 | 0.0406 | True | False |
| finish_model | >=80% | 2430 | 65.75 | 0.9251 | 0.9252 | 0.9474 | 0.0223 | True | False |
| goes_distance_model | >=80% | 2430 | 65.75 | 0.9251 | 0.9252 | 0.9474 | 0.0223 | True | False |
| method_model | >=80% | 2072 | 56.06 | 0.9126 | 0.7303 | 0.9405 | 0.0279 | True | False |
| round_phase_model | >=80% | 2170 | 58.92 | 0.9184 | 0.911 | 0.9274 | 0.009 | True | False |
| round_model | >=80% | 2170 | 58.92 | 0.9184 | 0.911 | 0.9274 | 0.009 | True | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |

## Interaction Discovery Summary
| Model | Candidates | Accepted | Selected | Selection Status |
|---|---:|---:|---:|---|
| winner_model | 240 | 80 | 0 | base_features_kept |
| fight_duration_model | 240 | 80 | 0 | base_features_kept |
| over_1_5_model | 240 | 80 | 0 | base_features_kept |
| over_2_5_model | 240 | 80 | 0 | base_features_kept |
| ends_before_round_3_model | 240 | 80 | 0 | base_features_kept |
| finish_in_round_1_model | 240 | 80 | 0 | base_features_kept |
| finish_type_model | 240 | 80 | 10 | selected |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model |
| strike_volume_model | 240 | 80 | 20 | selected |
| takedown_control_model | 240 | 80 | 0 | base_features_kept |
| finish_model | 240 | 80 | 0 | base_features_kept |
| goes_distance_model | 240 | 80 | 0 | base_features_kept |
| method_model | 0 | 0 | 0 | not_run_composite_model |
| round_phase_model | 0 | 0 | 0 | not_run_composite_summary |
| round_model | 0 | 0 | 0 | not_run_composite_summary |
| strike_volume_regression | 0 | 0 | 0 | not_run |
| odds_calibration_model | 0 | 0 | 0 | not_run |

## Production Readiness Gates
| Model | Production Status | Passed Gates | Failed Gates | Recommended Use |
|---|---|---|---|---|
| winner_model | high_confidence_only | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, cold_start_low_history_not_dangerously_poor, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists, runtime_parity_passes | source_holdout_stable, winner_leakage_audit_passes | research/high-confidence selective predictions only |
| fight_duration_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| over_1_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| over_2_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| ends_before_round_3_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_in_round_1_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_type_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | source_holdout_not_run | research only |
| method_umbrella_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| strike_volume_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, interaction_runtime_parity_passes, runtime_feature_schema_exists | calibration_acceptable, source_holdout_not_run | research only |
| takedown_control_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| goes_distance_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, interaction_final_test_not_used_for_selection, interaction_leakage_columns_excluded, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| method_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| round_phase_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | research only |
| round_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | research only |
| strike_volume_regression | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| odds_calibration_model | blocked |  | model_blocked | not available |
