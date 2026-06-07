# Model Accuracy Report

## Plain-English Summary
Models were evaluated on the newest chronological holdout from normalized historical fight data. Metrics are approximate final-test results, not guarantees.

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
| winner_model | evaluated | 3327 | 0.9092 | 0.52 | 0.3892 | True |  |
| finish_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True |  |
| goes_distance_model | evaluated | 3696 | 0.8287 | 0.5141 | 0.3146 | True |  |
| method_model | evaluated | 3696 | 0.6656 | 0.5141 | 0.1515 | True |  |
| strike_volume_model | evaluated | 1322 | 0.438 | 0.3623 | 0.0757 | True | Balanced accuracy is weak; keep as experimental context. |
| takedown_control_model | evaluated | 2486 | 0.5973 | 0.5897 | 0.0076 | True |  |
| strike_volume_regression | baseline_only | 1322 | 52.6679 | 50.6327 | -0.0402 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| round_phase_model | weak_or_failed_baseline | 3696 | 0.3122 | 0.5141 | -0.2019 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Segment Performance
### winner_model
- weight_class:Bantamweight: {'rows': 146, 'accuracy': 0.9041}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8702}
- weight_class:Featherweight: {'rows': 147, 'accuracy': 0.9116}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8527}
- weight_class:Flyweight: {'rows': 102, 'accuracy': 0.9314}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8352}
- weight_class:Heavyweight: {'rows': 88, 'accuracy': 0.875}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.8493}
- weight_class:Light Heavyweight: {'rows': 85, 'accuracy': 0.9176}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684}
- weight_class:Lightweight: {'rows': 163, 'accuracy': 0.9018}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.9122}
- weight_class:Middleweight: {'rows': 161, 'accuracy': 0.9379}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8552}
- weight_class:Welterweight: {'rows': 143, 'accuracy': 0.9091}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.8788}
- weight_class:Women's Bantamweight: {'rows': 53, 'accuracy': 0.9057}
- weight_class:Women's Flyweight: {'rows': 60, 'accuracy': 0.9333}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.9444}
- weight_class:Women's Strawweight: {'rows': 81, 'accuracy': 0.963}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8592}
- weight_class:bantamweight: {'rows': 106, 'accuracy': 0.934}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.9537}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.9726}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.9455}
- weight_class:light heavyweight: {'rows': 63, 'accuracy': 0.9524}
- weight_class:lightweight: {'rows': 125, 'accuracy': 0.976}
- weight_class:middleweight: {'rows': 113, 'accuracy': 0.9558}
- weight_class:welterweight: {'rows': 108, 'accuracy': 0.9537}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.9508}
- enough_fighter_history: {'rows': 3060, 'accuracy': 0.9137}
- low_fighter_history: {'rows': 267, 'accuracy': 0.8577}
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
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.8459}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.8626}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.8485}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.8295}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.8465}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.8462}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.7429}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.7397}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.8457}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.8684}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.8209}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.8784}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.8111}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.8828}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.7805}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.7803}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.9238}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.8279}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.8519}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.7716}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.8451}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.8198}
- low_fighter_history: {'rows': 477, 'accuracy': 0.8889}
### method_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.7089}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.7405}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.633}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6357}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.6485}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.6264}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.64}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.6575}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.6629}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6974}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.6209}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.6892}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.6223}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6621}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.6202}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.6061}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.7714}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.7623}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.7963}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.6852}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.7465}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.6741}
- low_fighter_history: {'rows': 477, 'accuracy': 0.608}
### round_phase_model
- weight_class:Bantamweight: {'rows': 292, 'accuracy': 0.3664}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.3817}
- weight_class:Featherweight: {'rows': 297, 'accuracy': 0.2492}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.2636}
- weight_class:Flyweight: {'rows': 202, 'accuracy': 0.3218}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.3187}
- weight_class:Heavyweight: {'rows': 175, 'accuracy': 0.2343}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.274}
- weight_class:Light Heavyweight: {'rows': 175, 'accuracy': 0.2229}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.2763}
- weight_class:Lightweight: {'rows': 335, 'accuracy': 0.3313}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.3378}
- weight_class:Middleweight: {'rows': 323, 'accuracy': 0.2384}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.2276}
- weight_class:Welterweight: {'rows': 287, 'accuracy': 0.2265}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.2348}
- weight_class:Women's Bantamweight: {'rows': 105, 'accuracy': 0.5524}
- weight_class:Women's Flyweight: {'rows': 122, 'accuracy': 0.4016}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.463}
- weight_class:Women's Strawweight: {'rows': 162, 'accuracy': 0.5617}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.5915}
- enough_fighter_history: {'rows': 3219, 'accuracy': 0.3166}
- low_fighter_history: {'rows': 477, 'accuracy': 0.283}
### strike_volume_model
- weight_class:Bantamweight: {'rows': 150, 'accuracy': 0.52}
- weight_class:Featherweight: {'rows': 152, 'accuracy': 0.5}
- weight_class:Flyweight: {'rows': 103, 'accuracy': 0.4078}
- weight_class:Heavyweight: {'rows': 94, 'accuracy': 0.4149}
- weight_class:Light Heavyweight: {'rows': 90, 'accuracy': 0.4556}
- weight_class:Lightweight: {'rows': 174, 'accuracy': 0.3851}
- weight_class:Middleweight: {'rows': 169, 'accuracy': 0.4142}
- weight_class:Welterweight: {'rows': 148, 'accuracy': 0.4189}
- weight_class:Women's Bantamweight: {'rows': 55, 'accuracy': 0.4364}
- weight_class:Women's Flyweight: {'rows': 62, 'accuracy': 0.4516}
- weight_class:Women's Strawweight: {'rows': 83, 'accuracy': 0.4217}
- enough_fighter_history: {'rows': 1091, 'accuracy': 0.4299}
- low_fighter_history: {'rows': 231, 'accuracy': 0.4762}
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

## Selective Prediction / High-Confidence Performance
| Model | Best Threshold | Rows | Coverage | Accuracy | Balanced Accuracy | Avg Confidence | Calibration Gap | 80%+ Accuracy? | 95%+ Balanced? |
|---|---|---:|---:|---:|---:|---:|---:|---|---|
| winner_model | >=80% | 2517 | 75.65 | 0.9722 | 0.9722 | 0.9441 | -0.028 | True | True |
| finish_model | >=80% | 1961 | 53.06 | 0.9301 | 0.9297 | 0.9221 | -0.008 | True | False |
| goes_distance_model | >=80% | 1991 | 53.87 | 0.9262 | 0.9257 | 0.922 | -0.0042 | True | False |
| method_model | >=80% | 1121 | 30.33 | 0.9063 | 0.4786 | 0.9187 | 0.0124 | True | False |
| round_phase_model | >=55% | 778 | 21.05 | 0.3972 | 0.3157 | 0.6932 | 0.296 | False | False |
| strike_volume_model | >=80% | 55 | 4.16 | 0.6727 | 0.4167 | 0.8465 | 0.1738 | False | False |
| takedown_control_model | >=80% | 217 | 8.73 | 0.7742 | 0.5178 | 0.8442 | 0.07 | False | False |
| strike_volume_regression |  |  |  |  |  |  |  | False | False |
| odds_calibration_model |  |  |  |  |  |  |  | False | False |
