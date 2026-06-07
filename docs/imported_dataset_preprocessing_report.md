# Imported Dataset Preprocessing Report

Raw data remains under `data/imports/` and is not committed.

## Combined Readiness
- `winner_model`: experimental_or_insufficient_dates (1 rows). 
- `finish_model`: experimental_or_insufficient_dates (1 rows). 
- `goes_distance_model`: experimental_or_insufficient_dates (1 rows). 
- `method_model`: experimental_or_insufficient_dates (1 rows). 
- `round_phase_model`: experimental_or_insufficient_dates (1 rows). 
- `strike_volume_model`: insufficient_data (0 rows). 
- `takedown_control_model`: insufficient_data (0 rows). 
- `odds_calibration_model`: review_needed (0 rows). Odds timestamp quality is not confirmed as pre-fight.

## Dataset Summaries
### ufc_stats_complete
- Available: True
- Rows normalized: 1
- Date range: {'min': '2024-01-01', 'max': '2024-01-01'}
- Odds quality: unavailable
- Uses: fight results, method/round labels, significant strikes, takedowns, control time, fighter/fight stats

## Source 7
UFCStats live scraping is intentionally not part of this pass; use it later for refresh/cross-checking after local datasets are stable.
