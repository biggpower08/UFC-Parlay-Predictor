# Odds Snapshot Normalization Plan

## Plain-English Summary
The downloaded UFC daily odds file is promising as a research input because it includes event dates, an `adding_date` timestamp, bookmaker/source fields, regions, moneyline odds, and method-prop odds. It is not safe for production odds modeling yet because some rows are missing timestamps and many archived snapshots were collected after the event date.

## Current Decision
- Dataset: `data/imports/kaggle/ufc_betting_odds_daily/UFC_betting_odds.csv`.
- Current audit status: `blocked_missing_snapshot_timestamps`.
- Research path: normalize only rows with trusted timestamps and clear event dates.
- Production path: blocked until timestamp filtering, fighter/fight mapping, prediction-cutoff simulation, and modeling review pass.
- `odds_calibration_model`: remains blocked.

## Proposed odds_snapshots Schema
| Field | Source / Rule |
|---|---|
| `fight_key` | Derived from `fight_url` when available, otherwise deterministic event/fighter hash. |
| `event_name` | Not present in this file; fill only if mapped from fight database. |
| `event_date` | `event_date`. |
| `fighter_a` | `fighter_1`. |
| `fighter_b` | `fighter_2`. |
| `selection` | Fighter-specific selection generated from fighter and market column. |
| `market_type` | `moneyline`, `ko_tko`, `submission`, or `decision`. |
| `bookmaker` | `source`. |
| `region` | `region`. |
| `american_odds` | Convert from decimal odds if American odds are needed. |
| `decimal_odds` | `odds_1`, `odds_2`, `f1_ko_odds`, `f2_ko_odds`, `f1_sub_odds`, `f2_sub_odds`, `f1_dec_odds`, `f2_dec_odds`. |
| `implied_probability` | Derived from decimal odds during normalization. |
| `snapshot_timestamp` | `adding_date`. |
| `source_dataset` | `ufc_betting_odds_daily`. |
| `source_file` | Local CSV path. |
| `source_row_hash` | Hash of source file, row index, fight URL, market, selection, bookmaker, odds, and timestamp. |
| `timestamp_audit_status` | Row-level timestamp decision. |
| `prediction_modes_allowed` | Derived from timestamp cutoff rules. |

## Prediction Modes
| Mode | Current Status | Requirement |
|---|---|---|
| `research_only` | allowed for timestamp-filtered rows | Event date, snapshot timestamp, selection, market, and odds must parse. |
| `opening_odds_model` | blocked | Need trusted opening snapshot definition and cutoff. |
| `24h_prefight_model` | blocked | Need snapshot timestamp within the selected pre-fight cutoff window. |
| `closing_line_model` | research only | Need explicit closing-line labeling or last trusted pre-event snapshot rule. |
| `production_odds_model` | blocked | Requires full timestamp audit, mapping audit, calibration, and modeling review. |

## Row-Level Filters Before Import
- Drop or quarantine rows with missing `adding_date`.
- Drop or quarantine rows with missing `event_date`.
- Mark rows where `adding_date > event_date` as post-event/archive snapshots.
- Keep post-event/archive rows out of early prediction modes.
- Require fighter selection and market type to be explicit.
- Preserve multiple snapshots per fight/bookmaker/market as append-only history.

## Next Implementation Step
Build a dry-run normalizer that expands the wide CSV into long-form `odds_snapshots` rows, reports row-level timestamp status counts, and writes only a local processed preview until the mapping audit is reviewed.
