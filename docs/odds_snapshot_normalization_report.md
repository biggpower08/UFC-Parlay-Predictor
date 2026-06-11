# Odds Snapshot Normalization Report

## Plain-English Summary
Timestamp-safe UFC daily odds rows were normalized into a research-only odds_snapshots preview. Odds calibration remains blocked because mapping/modeling review is incomplete and the source contains missing/post-event timestamp rows.

## Source File
- File: `data\imports\kaggle\ufc_betting_odds_daily\UFC_betting_odds.csv`
- Raw rows: 181766
- File size bytes: 29620834

## Accepted And Rejected Rows
- Accepted raw rows: 140842
- Rejected raw rows: 40924
- Accepted normalized snapshots: 281608

## Rejections By Reason
- missing_snapshot_timestamp: 684
- missing_event_date: 0
- snapshot_after_event: 40240
- invalid_odds: 845052
- unmapped_selection: 0
- unknown_market_type: 0
- duplicate_snapshot: 76

## Normalized Market Counts
- moneyline: 281608
- ko_tko_prop: 0
- submission_prop: 0
- decision_prop: 0

## Bookmaker / Source Counts
- BetOnline.ag: 21860
- LeoVegas: 17594
- Grosvenor: 17580
- DraftKings: 13790
- FanDuel: 12842
- Paddy Power: 12414
- Unibet (NL): 11702
- Betsson: 11284
- Nordic Bet: 11248
- Unibet (SE): 10992
- LeoVegas (SE): 10992
- BetRivers: 10406
- Pinnacle: 9904
- LiveScore Bet: 9866
- Virgin Bet: 9866
- BetMGM: 9590
- Unibet: 7764
- Betfair: 7536
- Coolbet: 7088
- Betway: 6126

## Region Counts
- eu: 79140
- us: 75086
- uk: 69766
- unknown: 57154
- betonlineag: 44
- draftkings: 32
- paddypower: 30
- fanduel: 28
- betsson: 28
- nordicbet: 28
- betmgm: 26
- leovegas: 24
- virginbet: 24
- betrivers: 24
- unibet_nl: 24
- grosvenor: 24
- livescorebet: 24
- unibet_uk: 24
- betfair_ex_uk: 20
- betfair_ex_eu: 20

## Date Ranges
- Raw event date range: {'min': '2010-03-21T00:00:00+00:00', 'max': '2027-07-02T00:00:00+00:00'}
- Raw snapshot timestamp range: {'min': '2025-07-26T07:05:52.715662+00:00', 'max': '2026-06-10T16:53:27+00:00'}
- Accepted event date range: {'min': '2025-08-02T00:00:00+00:00', 'max': '2027-07-02T00:00:00+00:00'}
- Accepted snapshot timestamp range: {'min': '2025-07-26T07:05:52.715662+00:00', 'max': '2025-09-05T22:00:09.404168+00:00'}

## Days Before Event Distribution
- 0_to_1_days: 21389
- 1_to_7_days: 126108
- 7_to_30_days: 82338
- 30_plus_days: 51773

## Safe Modes Summary
- closing_line_candidate: 21389
- day_before_candidate: 260219
- early_prefight_candidate: 134111
- future_event_candidate: 23462
- research_only: 281608

## Outputs
- Committed preview JSON: `C:\dev\mma-ai\ufc_predictor\data\processed\odds_snapshots_preview.json`
- Full local CSV preview: `C:\dev\mma-ai\ufc_predictor\data\processed\training_imports\odds_snapshots_preview.csv` (ignored by Git)

## Why odds_calibration_model Remains Blocked
- The source contains missing snapshot timestamps and post-event snapshots.
- The normalized subset is research-only until fight mapping and prediction cutoff review are complete.
- No odds-aware model has been trained or audited.