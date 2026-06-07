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
| finish_model | evaluated | 5537 | 0.6101 | 0.5183 | 0.0918 | True |  |
| goes_distance_model | evaluated | 5537 | 0.6101 | 0.5183 | 0.0918 | True |  |
| strike_volume_model | evaluated | 3163 | 0.4006 | 0.3721 | 0.0285 | True | Balanced accuracy is weak; keep as experimental context. |
| strike_volume_regression | baseline_only | 3163 | 53.2381 | 51.1448 | -0.0409 | False | Regression model is currently a simple baseline harness; add trained regressors before public use. |
| takedown_control_model | weak_or_failed_baseline | 4327 | 0.5193 | 0.5653 | -0.046 | False | Does not beat majority-class baseline on final chronological test set. |
| method_model | weak_or_failed_baseline | 5537 | 0.3235 | 0.5183 | -0.1948 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context. |
| round_phase_model | weak_or_failed_baseline | 5537 | 0.1663 | 0.5183 | -0.352 | False | Does not beat majority-class baseline on final chronological test set.; Balanced accuracy is weak; keep as experimental context. |
| winner_model | blocked | 0 |  |  |  | False | Winner labels exist in imported data, but known-winner sources are currently winner-oriented after normalization. A runtime winner model needs a safe fighter_1/fighter_2 orientation with mirrored rows kept together before it can be honestly evaluated. |
| odds_calibration_model | blocked | 0 |  |  |  | False | Pre-fight odds snapshots are not yet safely matched to outcomes and timestamps. |

## Segment Performance
### finish_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.646}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.6031}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.6357}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6357}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.5448}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5385}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.6078}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5753}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.5641}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.5658}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.5634}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5676}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.6697}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6414}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.5489}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.6458}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.6512}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.6111}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.6681}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6338}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.6542}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.6667}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.5753}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.6182}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.5692}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6032}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7069}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5596}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6393}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.6113}
- low_fighter_history: {'rows': 631, 'accuracy': 0.6006}
### goes_distance_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.646}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.6031}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.6357}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.6357}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.5448}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5385}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.6078}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5753}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.5641}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.5658}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.5634}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5676}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.6697}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.6414}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.5489}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.6458}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.6512}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.6111}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.6681}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.6338}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.6542}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.6667}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.5753}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.6182}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.5692}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.6032}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.7069}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5596}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.6393}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.6113}
- low_fighter_history: {'rows': 631, 'accuracy': 0.6006}
### method_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.2797}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.2443}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.3423}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.3411}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.2652}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.2747}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.1595}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.137}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.3974}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.4079}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.3226}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.3311}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.2828}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.3034}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.3133}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.3106}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.4931}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.4419}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.4074}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.4071}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.3803}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.2897}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.3519}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.2466}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.1818}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.3846}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.3175}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.2845}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.3119}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.4426}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.3437}
- low_fighter_history: {'rows': 631, 'accuracy': 0.1664}
### round_phase_model
- weight_class:Bantamweight: {'rows': 404, 'accuracy': 0.1535}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.1679}
- weight_class:Featherweight: {'rows': 409, 'accuracy': 0.1711}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.1628}
- weight_class:Flyweight: {'rows': 279, 'accuracy': 0.19}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.1868}
- weight_class:Heavyweight: {'rows': 232, 'accuracy': 0.1422}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.1507}
- weight_class:Light Heavyweight: {'rows': 234, 'accuracy': 0.094}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.0789}
- weight_class:Lightweight: {'rows': 465, 'accuracy': 0.1763}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.1622}
- weight_class:Middleweight: {'rows': 442, 'accuracy': 0.1561}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.1448}
- weight_class:Welterweight: {'rows': 399, 'accuracy': 0.1328}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.1136}
- weight_class:Women's Bantamweight: {'rows': 144, 'accuracy': 0.2153}
- weight_class:Women's Flyweight: {'rows': 172, 'accuracy': 0.1977}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.1852}
- weight_class:Women's Strawweight: {'rows': 226, 'accuracy': 0.2743}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.2958}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.1963}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.1667}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.2192}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.1818}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.0769}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.2063}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.1638}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.1284}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.2951}
- enough_fighter_history: {'rows': 4906, 'accuracy': 0.171}
- low_fighter_history: {'rows': 631, 'accuracy': 0.13}
### strike_volume_model
- weight_class:Bantamweight: {'rows': 262, 'accuracy': 0.4122}
- weight_class:Featherweight: {'rows': 264, 'accuracy': 0.4129}
- weight_class:Flyweight: {'rows': 180, 'accuracy': 0.4056}
- weight_class:Heavyweight: {'rows': 151, 'accuracy': 0.3775}
- weight_class:Light Heavyweight: {'rows': 149, 'accuracy': 0.4698}
- weight_class:Lightweight: {'rows': 304, 'accuracy': 0.352}
- weight_class:Middleweight: {'rows': 288, 'accuracy': 0.4757}
- weight_class:Welterweight: {'rows': 260, 'accuracy': 0.3538}
- weight_class:Women's Bantamweight: {'rows': 94, 'accuracy': 0.3404}
- weight_class:Women's Flyweight: {'rows': 112, 'accuracy': 0.4375}
- weight_class:Women's Strawweight: {'rows': 147, 'accuracy': 0.3265}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.4206}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.4167}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.4247}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.3818}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.4462}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.3571}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.4828}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.3578}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.3115}
- enough_fighter_history: {'rows': 2778, 'accuracy': 0.3974}
- low_fighter_history: {'rows': 385, 'accuracy': 0.4234}
### takedown_control_model
- weight_class:Bantamweight: {'rows': 262, 'accuracy': 0.542}
- weight_class:Bantamweight Bout: {'rows': 131, 'accuracy': 0.5573}
- weight_class:Featherweight: {'rows': 264, 'accuracy': 0.4659}
- weight_class:Featherweight Bout: {'rows': 129, 'accuracy': 0.4651}
- weight_class:Flyweight: {'rows': 180, 'accuracy': 0.5056}
- weight_class:Flyweight Bout: {'rows': 91, 'accuracy': 0.5714}
- weight_class:Heavyweight: {'rows': 151, 'accuracy': 0.5298}
- weight_class:Heavyweight Bout: {'rows': 73, 'accuracy': 0.5205}
- weight_class:Light Heavyweight: {'rows': 149, 'accuracy': 0.6577}
- weight_class:Light Heavyweight Bout: {'rows': 76, 'accuracy': 0.6842}
- weight_class:Lightweight: {'rows': 304, 'accuracy': 0.5362}
- weight_class:Lightweight Bout: {'rows': 148, 'accuracy': 0.5405}
- weight_class:Middleweight: {'rows': 288, 'accuracy': 0.5382}
- weight_class:Middleweight Bout: {'rows': 145, 'accuracy': 0.5931}
- weight_class:Welterweight: {'rows': 260, 'accuracy': 0.4923}
- weight_class:Welterweight Bout: {'rows': 132, 'accuracy': 0.5606}
- weight_class:Women's Bantamweight: {'rows': 94, 'accuracy': 0.5745}
- weight_class:Women's Flyweight: {'rows': 112, 'accuracy': 0.4018}
- weight_class:Women's Flyweight Bout: {'rows': 54, 'accuracy': 0.463}
- weight_class:Women's Strawweight: {'rows': 147, 'accuracy': 0.3605}
- weight_class:Women's Strawweight Bout: {'rows': 71, 'accuracy': 0.4225}
- weight_class:bantamweight: {'rows': 107, 'accuracy': 0.5327}
- weight_class:featherweight: {'rows': 108, 'accuracy': 0.4815}
- weight_class:flyweight: {'rows': 73, 'accuracy': 0.5342}
- weight_class:heavyweight: {'rows': 55, 'accuracy': 0.5273}
- weight_class:light heavyweight: {'rows': 65, 'accuracy': 0.6923}
- weight_class:lightweight: {'rows': 126, 'accuracy': 0.5317}
- weight_class:middleweight: {'rows': 116, 'accuracy': 0.5431}
- weight_class:welterweight: {'rows': 109, 'accuracy': 0.5138}
- weight_class:women's strawweight: {'rows': 61, 'accuracy': 0.377}
- enough_fighter_history: {'rows': 3746, 'accuracy': 0.5376}
- low_fighter_history: {'rows': 581, 'accuracy': 0.401}
