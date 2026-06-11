# Source Normalization Rules

## Plain-English Summary
Imported fight data can come from several datasets with different labels and formats. The app normalizes only safe, equivalent meanings, and it does not rewrite labels just to improve model scores.

## Current Rules
- Fighter names are normalized for matching by lowercasing and stripping punctuation-like spacing differences.
- Fight orientation is deterministic: fighters are sorted into a stable `fighter_a` / `fighter_b` matchup before labels are assigned.
- Method labels are canonicalized to `Decision`, `KO/TKO`, `Submission`, or `Other`.
- Decision-like strings such as `U-DEC`, `S-DEC`, `M-DEC`, and `Decision - Unanimous` map to `Decision`.
- Submission-like strings map to `Submission`.
- KO/TKO-like strings map to `KO/TKO`.
- DQ and unusual finishes map to `Other`.
- No-contest, overturned, draw, unknown, or missing outcomes do not create finish, distance, method, round, or prop-model labels.
- Round/time labels are parsed only when round and midpoint time are available. The builder does not guess missing over/under midpoint labels.
- Weight-class display/reporting strips obvious `Bout` suffix variants for grouping, but source values remain available for audit.
- Duplicate and mirrored fight rows are grouped by stable event/date/fighter-pair keys for split and leakage checks.

## Not Allowed
- Do not change labels only to improve metrics.
- Do not silently drop hard rows.
- Do not use current-fight outcome/stat columns as pre-fight features.
- Do not add source-specific hacks that cannot generalize.

## Current Safe Fixes
- CSV loading now uses `low_memory=False` consistently to avoid mixed-type chunk inference during model/report builds.
- Non-win outcomes now remain in audit context but have null model labels, preventing no-contest/draw/unknown rows from becoming fake finish or round targets.
