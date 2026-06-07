# Imported Dataset Preprocessing Report

Raw data remains under `data/imports/` and is not committed.

## Combined Readiness
- `winner_model`: blocked_orientation_review (32140 rows). Winner labels are present, but normalized sources appear winner-oriented; runtime fighter_1/fighter_2 orientation must be corrected before winner-model training.
- `finish_model`: training_data_ready (49355 rows). 
- `goes_distance_model`: training_data_ready (49355 rows). 
- `method_model`: training_data_ready (49355 rows). 
- `round_phase_model`: training_data_ready (48720 rows). 
- `strike_volume_model`: training_data_ready (33530 rows). 
- `takedown_control_model`: training_data_ready (42081 rows). 
- `odds_calibration_model`: review_needed (13272 rows). Odds timestamp quality is not confirmed as pre-fight.

## Dataset Summaries
### ufc_fight_forecast
- Available: True
- Rows normalized: 8231
- Date range: {'min': '1994-03-11', 'max': '2025-10-04'}
- Odds quality: review_needed
- Uses: winner modeling, odds-aware winner modeling, ranking/odds features, modeling benchmark
### ufc_stats_complete
- Available: True
- Rows normalized: 8709
- Date range: {'min': '1993-11-12', 'max': '2026-05-16'}
- Odds quality: unavailable
- Uses: fight results, method/round labels, significant strikes, takedowns, control time, fighter/fight stats
### ufc_1994_2026
- Available: True
- Rows normalized: 8551
- Date range: {'min': '1994-03-11', 'max': '2026-03-07'}
- Odds quality: unavailable
- Uses: broad historical coverage, fighter profiles, fight stats, round/strike/control cross-checks
### ufc_1994_2025
- Available: True
- Rows normalized: 16674
- Date range: {'min': '1994-03-11', 'max': '2025-09-06'}
- Odds quality: unavailable
- Uses: newer UFCStats scrape cross-check, results/method/round, event/fight validation
### mdabbert_ultimate
- Available: True
- Rows normalized: 7190
- Date range: {'min': '2010-03-21', 'max': '2026-04-04'}
- Odds quality: review_needed
- Uses: odds-aware modeling, betting market baseline, winner modeling after leakage audit
### mdabbert_2010_2020_odds
- Available: True
- Rows normalized: 0
- Zero-row reason: odds-only dataset; retained for odds research until pre-fight timestamp quality is confirmed
- Date range: {'min': None, 'max': None}
- Odds quality: unavailable
- Uses: historical odds comparison, odds baseline, calibration experiments
### ufc_datalab
- Available: False
- Rows normalized: 0
- Zero-row reason: dataset folder missing
- Date range: {'min': None, 'max': None}
- Odds quality: unavailable
- Uses: scorecards, official-stat cross-checks, round/decision research, future advanced evaluation

## Source 7
UFCStats live scraping is intentionally not part of this pass; use it later for refresh/cross-checking after local datasets are stable.
