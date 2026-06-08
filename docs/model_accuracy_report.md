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
| fight_duration_model | evaluated | 3696 | 0.8287 | 0.8297 | 0.8994 | 0.1288 | 0.5141 | 0.3146 |
| over_1_5_model | evaluated | 3683 | 0.7385 | 0.6758 | 0.7862 | 0.1689 | 0.6964 | 0.0421 |
| over_2_5_model | evaluated | 3683 | 0.7942 | 0.79 | 0.8717 | 0.1454 | 0.5599 | 0.2343 |
| ends_before_round_3_model | evaluated | 3683 | 0.7719 | 0.7611 | 0.8429 | 0.1579 | 0.6066 | 0.1653 |
| finish_in_round_1_model | weak_or_failed_baseline | 3683 | 0.6554 | 0.6242 | 0.6853 | 0.2176 | 0.7613 | -0.1059 |
| finish_type_model | weak_or_failed_baseline | 1796 | 0.5651 | 0.4422 | None | None | 0.632 | -0.0669 |
| method_umbrella_model | evaluated | 3696 | 0.6545 | 0.4621 | None | None | 0.5141 | 0.1404 |

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
| winner_model | evaluated | 3327 | 0.9095 | 0.52 | 0.3895 | True |  |
| fight_duration_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True |  |
| finish_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True | Compatibility output: internally backed by fight_duration_model. |
| goes_distance_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True | Compatibility output: goes_distance_probability is derived as 1 - finish_probability. |
| over_2_5_model | evaluated | 3683 | 0.7942 | 0.5599 | 0.2343 | True |  |
| round_phase_model | evaluated | 3683 | 0.7942 | 0.5599 | 0.2343 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Weak members: finish_in_round_1_model |
| round_model | evaluated | 3683 | 0.7942 | 0.5599 | 0.2343 | True | Legacy round_phase_model is replaced by separate binary round-phase submodels.; Weak members: finish_in_round_1_model; Compatibility alias backed by round_phase_model. |
| ends_before_round_3_model | evaluated | 3683 | 0.7719 | 0.6066 | 0.1653 | True |  |
| method_umbrella_model | evaluated | 3696 | 0.6545 | 0.5141 | 0.1404 | True | Umbrella method output combines duration probability with conditional finish type probabilities. |
| method_model | evaluated | 3696 | 0.6545 | 0.5141 | 0.1404 | True | Umbrella method output combines duration probability with conditional finish type probabilities.; Compatibility alias backed by method_umbrella_model. |
| strike_volume_model | evaluated | 1322 | 0.4357 | 0.3623 | 0.0734 | True | Balanced accuracy is weak; keep as experimental context. |
| over_1_5_model | evaluated | 3683 | 0.7385 | 0.6964 | 0.0421 | True |  |
| takedown_control_model | evaluated | 2486 | 0.5973 | 0.5897 | 0.0076 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| finish_type_model | weak_or_failed_baseline | 1796 | 0.5651 | 0.632 | -0.0669 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context.; Conditional model: trained and scored only on fights that actually finished. |
| finish_in_round_1_model | weak_or_failed_baseline | 3683 | 0.6554 | 0.7613 | -0.1059 | False | Does not beat majority-class baseline on final chronological test set. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Segment Performance
### winner_model
- weight_class:Bantamweight: {'rows': 146, 'accuracy': 0.9041}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8931}
- weight_class:Featherweight: {'rows': 147, 'accuracy': 0.9184}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527}
- weight_class:Flyweight: {'rows': 102, 'accuracy': 0.9608}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8352}
- weight_class:Heavyweight: {'rows': 88, 'accuracy': 0.8864}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493}
- weight_class:Light Heavyweight: {'rows': 85, 'accuracy': 0.9294}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684}
- weight_class:Lightweight: {'rows': 163, 'accuracy': 0.8896}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8919}
- weight_class:Middleweight: {'rows': 161, 'accuracy': 0.9317}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8621}
- weight_class:Welterweight: {'rows': 143, 'accuracy': 0.9371}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.8712}
- weight_class:Women's Bantamweight: {'rows': 53, 'accuracy': 0.9245}
- weight_class:Women's Flyweight: {'rows': 60, 'accuracy': 0.9333}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9444}
- weight_class:Women's Strawweight: {'rows': 81, 'accuracy': 0.963}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- weight_class:bantamweight: {'rows': 106, 'accuracy': 0.9245}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.963}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.9726}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9455}
- weight_class:light heavyweight: {'rows': 63, 'accuracy': 0.9524}
- weight_class:lightweight: {'rows': 125, 'accuracy': 0.952}
- weight_class:middleweight: {'rows': 113, 'accuracy': 0.9558}
- weight_class:welterweight: {'rows': 108, 'accuracy': 0.9537}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9508}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9144}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8539}
### fight_duration_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.839}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8451}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8515}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7371}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7534}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.84}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8179}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8204}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8759}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.784}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9143}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8443}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7901}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8223}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8721}
### over_1_5_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.811}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8092}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.7017}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6744}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.7413}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7363}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.7069}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6986}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.6494}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6579}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.7259}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7432}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.6832}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6759}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7352}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7197}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.7981}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.8099}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8148}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8323}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.7351}
- low_fighter_history: {'rows': 474, 'accuracy': 0.7616}
### over_2_5_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.8419}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.7898}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8062}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.806}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.7586}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.726}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.7529}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8026}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.7801}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7905}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.7578}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8138}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7282}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.697}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.8846}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.843}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8889}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8075}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8732}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.785}
- low_fighter_history: {'rows': 474, 'accuracy': 0.8565}
### ends_before_round_3_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.8385}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8397}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.7661}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.7752}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.7463}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.7582}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.7011}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7123}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.7356}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.7632}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.7711}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7703}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.736}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7655}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7352}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7273}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.8558}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.8099}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8148}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8075}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.831}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.7666}
- low_fighter_history: {'rows': 474, 'accuracy': 0.808}
### finish_in_round_1_model
- weight_class:Bantamweight: {'rows': 291, 'accuracy': 0.756}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7252}
- weight_class:Featherweight: {'rows': 295, 'accuracy': 0.5898}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.5271}
- weight_class:Flyweight: {'rows': 201, 'accuracy': 0.6816}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6374}
- weight_class:Heavyweight: {'rows': 174, 'accuracy': 0.6264}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6301}
- weight_class:Light Heavyweight: {'rows': 174, 'accuracy': 0.592}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.5526}
- weight_class:Lightweight: {'rows': 332, 'accuracy': 0.6747}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.6216}
- weight_class:Middleweight: {'rows': 322, 'accuracy': 0.5466}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.5448}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6272}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5985}
- weight_class:Women's Bantamweight: {'rows': 104, 'accuracy': 0.7404}
- weight_class:Women's Flyweight: {'rows': 121, 'accuracy': 0.7521}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7593}
- weight_class:Women's Strawweight: {'rows': 161, 'accuracy': 0.8634}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8592}
- enough_fighter_history: {'rows': 3209, 'accuracy': 0.6553}
- low_fighter_history: {'rows': 474, 'accuracy': 0.6561}
### finish_type_model
- weight_class:Bantamweight: {'rows': 91, 'accuracy': 0.4066}
- weight_class:Featherweight: {'rows': 164, 'accuracy': 0.5549}
- weight_class:Featherweight Bout: {'rows': 71, 'accuracy': 0.5915}
- weight_class:Flyweight: {'rows': 97, 'accuracy': 0.5464}
- weight_class:Heavyweight: {'rows': 90, 'accuracy': 0.6}
- weight_class:Light Heavyweight: {'rows': 117, 'accuracy': 0.6923}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.5517}
- weight_class:Lightweight Bout: {'rows': 75, 'accuracy': 0.6}
- weight_class:Middleweight: {'rows': 189, 'accuracy': 0.5397}
- weight_class:Middleweight Bout: {'rows': 87, 'accuracy': 0.6092}
- weight_class:Welterweight: {'rows': 159, 'accuracy': 0.6415}
- weight_class:Welterweight Bout: {'rows': 76, 'accuracy': 0.6053}
- weight_class:Women's Strawweight: {'rows': 51, 'accuracy': 0.3725}
- enough_fighter_history: {'rows': 1524, 'accuracy': 0.5728}
- low_fighter_history: {'rows': 272, 'accuracy': 0.5221}
### method_umbrella_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.7021}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7405}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.6364}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6434}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.6535}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6374}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.5657}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5479}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.68}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.7368}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.6149}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7095}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.5882}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6552}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6202}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.6136}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.7333}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.7213}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7222}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.6605}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6761}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.657}
- low_fighter_history: {'rows': 477, 'accuracy': 0.6373}
### strike_volume_model
- weight_class:Bantamweight: {'rows': 150, 'accuracy': 0.48}
- weight_class:Featherweight: {'rows': 152, 'accuracy': 0.4934}
- weight_class:Flyweight: {'rows': 103, 'accuracy': 0.4078}
- weight_class:Heavyweight: {'rows': 94, 'accuracy': 0.3723}
- weight_class:Light Heavyweight: {'rows': 90, 'accuracy': 0.4778}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.4023}
- weight_class:Middleweight: {'rows': 169, 'accuracy': 0.4142}
- weight_class:Welterweight: {'rows': 148, 'accuracy': 0.4392}
- weight_class:Women's Bantamweight: {'rows': 55, 'accuracy': 0.4182}
- weight_class:Women's Flyweight: {'rows': 62, 'accuracy': 0.4839}
- weight_class:Women's Strawweight: {'rows': 83, 'accuracy': 0.4458}
- enough_fighter_history: {'rows': 1091, 'accuracy': 0.4244}
- low_fighter_history: {'rows': 231, 'accuracy': 0.4892}
### takedown_control_model
- weight_class:Bantamweight: {'rows': 150, 'accuracy': 0.56}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.5649}
- weight_class:Featherweight: {'rows': 152, 'accuracy': 0.5592}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.5659}
- weight_class:Flyweight: {'rows': 103, 'accuracy': 0.5631}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6154}
- weight_class:Heavyweight: {'rows': 94, 'accuracy': 0.6702}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6849}
- weight_class:Light Heavyweight: {'rows': 90, 'accuracy': 0.8}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8158}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.523}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5946}
- weight_class:Middleweight: {'rows': 169, 'accuracy': 0.6154}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.7034}
- weight_class:Welterweight: {'rows': 148, 'accuracy': 0.6149}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.697}
- weight_class:Women's Bantamweight: {'rows': 55, 'accuracy': 0.4909}
- weight_class:Women's Flyweight: {'rows': 62, 'accuracy': 0.4355}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.5926}
- weight_class:Women's Strawweight: {'rows': 83, 'accuracy': 0.3855}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.5352}
- enough_fighter_history: {'rows': 2059, 'accuracy': 0.5925}
- low_fighter_history: {'rows': 427, 'accuracy': 0.6206}
### finish_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.839}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8451}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8515}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7371}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7534}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.84}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8179}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8204}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8759}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.784}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9143}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8443}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7901}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8223}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8721}
### goes_distance_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.839}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8451}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8515}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8132}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7371}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7534}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.84}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8179}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8446}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8204}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8759}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.784}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7955}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9143}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8443}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7901}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8223}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8721}
### method_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.7021}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7405}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.6364}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6434}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.6535}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6374}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.5657}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5479}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.68}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.7368}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.6149}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.7095}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.5882}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6552}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6202}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.6136}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.7333}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.7213}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7222}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.6605}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6761}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.657}
- low_fighter_history: {'rows': 477, 'accuracy': 0.6373}

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 2536 | 76.22 | 0.9716 | 0.9716 | 0.9436 | -0.028 | True | True |
| fight_duration_model | >=80% | 1961 | 53.06 | 0.9301 | 0.9297 | 0.9221 | -0.008 | True | False |
| over_1_5_model | >=80% | 1352 | 36.71 | 0.9246 | 0.5649 | 0.9089 | -0.0157 | True | False |
| over_2_5_model | >=80% | 1612 | 43.77 | 0.9225 | 0.9214 | 0.9055 | -0.017 | True | False |
| ends_before_round_3_model | >=80% | 1566 | 42.52 | 0.9087 | 0.899 | 0.8949 | -0.0138 | True | False |
| finish_in_round_1_model | >=80% | 325 | 8.82 | 0.8277 | 0.7775 | 0.8489 | 0.0212 | True | False |
| finish_type_model | >=80% | 425 | 23.66 | 0.5906 | 0.5333 | 0.8852 | 0.2946 | False | False |
| method_umbrella_model | >=80% | 996 | 26.95 | 0.9137 | 0.4305 | 0.9165 | 0.0028 | True | False |
| strike_volume_model | >=80% | 60 | 4.54 | 0.6833 | 0.4103 | 0.8418 | 0.1585 | False | False |
| takedown_control_model | >=80% | 217 | 8.73 | 0.7742 | 0.5178 | 0.8442 | 0.07 | False | False |
| finish_model | >=80% | 1961 | 53.06 | 0.9301 | 0.9297 | 0.9221 | -0.008 | True | False |
| goes_distance_model | >=80% | 1961 | 53.06 | 0.9301 | 0.9297 | 0.9221 | -0.008 | True | False |
| method_model | >=80% | 996 | 26.95 | 0.9137 | 0.4305 | 0.9165 | 0.0028 | True | False |
| round_phase_model | >=80% | 1612 | 43.77 | 0.9225 | 0.9214 | 0.9055 | -0.017 | True | False |
| round_model | >=80% | 1612 | 43.77 | 0.9225 | 0.9214 | 0.9055 | -0.017 | True | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |

## Interaction Discovery Summary
| Model | Candidates | Accepted | Selected | Selection Status |
|---|---:|---:|---:|---|
| winner_model | 240 | 80 | 5 | selected |
| fight_duration_model | 240 | 80 | 0 | base_features_kept |
| over_1_5_model | 240 | 80 | 0 | base_features_kept |
| over_2_5_model | 240 | 80 | 0 | base_features_kept |
| ends_before_round_3_model | 240 | 80 | 0 | base_features_kept |
| finish_in_round_1_model | 240 | 80 | 5 | selected |
| finish_type_model | 208 | 80 | 10 | selected |
| method_umbrella_model | 0 | 0 | 0 | not_run_composite_model |
| strike_volume_model | 240 | 80 | 5 | selected |
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
| winner_model | high_confidence_only | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, cold_start_low_history_not_dangerously_poor, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists, runtime_parity_passes | source_holdout_stable, winner_leakage_audit_passes | research/high-confidence selective predictions only |
| fight_duration_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| over_1_5_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| over_2_5_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| ends_before_round_3_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| finish_in_round_1_model | weak_or_failed_baseline | balanced_accuracy_not_dangerously_low, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | beats_chronological_baseline, calibration_acceptable, source_holdout_not_run | research only |
| finish_type_model | weak_or_failed_baseline | calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, source_holdout_not_run | research only |
| method_umbrella_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| strike_volume_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| takedown_control_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | calibration_acceptable, source_holdout_not_run | research only |
| finish_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| goes_distance_model | production_candidate | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | candidate for limited internal validation |
| method_model | experimental | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | source_holdout_not_run | research only |
| round_phase_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | research only |
| round_model | experimental | beats_chronological_baseline, duplicate_mirrored_fight_leakage_prevented, high_confidence_not_tiny_sample_noise, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, calibration_acceptable, source_holdout_not_run | research only |
| strike_volume_regression | weak_or_failed_baseline | duplicate_mirrored_fight_leakage_prevented, runtime_feature_schema_exists | balanced_accuracy_not_dangerously_low, beats_chronological_baseline, calibration_acceptable, high_confidence_not_tiny_sample_noise, source_holdout_not_run | research only |
| odds_calibration_model | blocked |  | model_blocked | not available |
