# Odds Feature Schema

## Plain-English Summary
Odds features are not live yet. This schema describes how odds can be normalized later without leaking future market information into historical predictions.

## Normalized Fields
- `fight_key`
- `event_name`
- `event_date`
- `fighter_a`
- `fighter_b`
- `selection`
- `market_type`
- `bookmaker`
- `region`
- `american_odds`
- `decimal_odds`
- `implied_probability`
- `snapshot_timestamp`
- `source_dataset`
- `source_file`
- `source_row_hash`
- `is_closing_candidate`
- `is_live`
- `timestamp_audit_status`

## Feature Families
- Moneyline snapshots.
- Method props: KO/TKO, submission, decision.
- Market availability flags.
- Bookmaker dispersion.
- Movement between trusted pre-fight snapshots.
- Closing-line values only for closing-line mode.

## Excluded Until Proven Safe
- Odds rows without timestamps.
- Post-fight archived odds.
- Closing odds used as early prediction features.
- Any odds source with unclear event date alignment.
- Any odds feature that cannot be reproduced at runtime for the same prediction cutoff.
