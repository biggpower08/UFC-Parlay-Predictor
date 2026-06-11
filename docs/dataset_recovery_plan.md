# Dataset Recovery Plan

## Plain-English Summary
The next data work is not just adding more rows. It is making sure each model trains only on sources that safely support its target labels.

## Winner Model
- Needs source-transfer stability.
- Needs alias/name normalization review.
- Needs source-stable features.

## Duration And Round Models
- Need clean finish/goes-distance labels.
- Need reliable finish round/time.
- Need scheduled-round parsing.
- Need no-contest, draw, DQ, overturned, unknown, and missing results excluded from target labels.

## Method And Finish-Type Models
- Need clean method labels.
- Need stable KO/TKO, submission, decision, and other mapping.
- Need doctor/corner stoppage handling.
- Need DQ/no-contest filtering.

## Strike-Volume Model
- Needs significant strikes landed/attempted.
- Needs absorbed strikes.
- Needs round-level stats if exact thresholds are added.
- Needs expected-duration context.
- `ufc_stats_complete` is likely useful here as a stat-rich source.

## Takedown/Control Model
- Needs takedowns landed/attempted.
- Needs takedowns absorbed.
- Needs control time.
- Needs submission attempts.
- Needs grappling exposure.
- `ufc_stats_complete` is likely useful here as a stat-rich source.

## Odds Calibration
- Needs trusted pre-fight timestamp.
- Needs opening line, current/closing line, sportsbook/source, fighter mapping, and implied probability.
- Remains blocked until timestamp quality is solved.
