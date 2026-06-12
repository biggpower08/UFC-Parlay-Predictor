# FightScope Model Readiness Report

Last updated: 2026-06-12

## Purpose

This report explains which FightScope model reads are usable today, which ones are only supporting context, and which ones stay off until the data review is stronger. It is written for product review and release safety, not as a public methodology page.

## Current Model Read Shape

Frontend model cards now use one shared read shape:

- `id`
- `title`
- `category`
- `modelType`
- `status`
- `statusLabel`
- `targetFighter`
- `opponentFighter`
- `task`
- `read`
- `explanation`
- `evidence`
- `limitations`
- `confidenceLabel`
- `confidenceScore`
- `isTrained`
- `isHeuristic`
- `isBlocked`
- `isAvailable`
- `dataQuality`
- `missingData`
- `updatedAt`

The product wording is intentionally task-based: each card should answer who is more likely to accomplish that model's task and how, instead of exposing raw internal labels.

## Model Status Summary

| Model | Current Use | Status | Main Metric | Baseline | Product Wording |
| --- | --- | --- | ---: | ---: | --- |
| `winner_model` | Primary win read | high_confidence_only | 0.9606 accuracy | 0.5200 | Use as the main read only with confidence and data-quality caution. |
| `fight_duration_model` | Fight shape | production_candidate | 0.8596 accuracy | 0.5191 | Useful for duration texture, not exact timing. |
| `finish_model` | Finish pressure | production_candidate | 0.8596 accuracy | 0.5191 | Useful for finish-vs-decision texture. |
| `goes_distance_model` | Decision path | production_candidate | 0.8596 accuracy | 0.5191 | Useful as inverse duration/decision context. |
| `round_model` | Timing window | experimental | 0.8130 accuracy | 0.5621 | Use as phase context, not an exact-round claim. |
| `finish_type_model` | KO/TKO vs submission texture | experimental | 0.7956 accuracy | 0.6412 | Use as cautious finish-type context. |
| `method_model` | Broad method detail | weak signal | 0.5191 accuracy | 0.5191 | Show only as under-review context. |
| `method_umbrella_model` | Broad method grouping | weak signal | 0.5191 accuracy | 0.5191 | Do not use as a strong public read. |
| `strike_volume_model` | Standing-volume texture | experimental | 0.5908 accuracy | 0.3623 | Use as style context when runtime stats exist. |
| `takedown_control_model` | Grappling/control texture | experimental | 0.7349 accuracy | 0.5897 | Use as style context; source-holdout stability still matters. |
| `odds_calibration_model` | Market comparison | blocked | n/a | n/a | Keep inactive until timestamp-safe odds mapping passes review. |

## Production Safety Rules

- Do not show fake sportsbook lines, edge, units, ROI, or bet placement.
- Do not present experimental or weak models as strong forecasts.
- Keep market comparison inactive until odds timestamps and fighter mapping are trusted.
- Keep method detail modest because the broad method model is weak against its review baseline.
- Keep winner output labeled as a high-confidence-only research signal until source-holdout and leakage gates are fully clean.
- Use supporting prop models for explanation, confidence, volatility, and style context; do not let them overpower the winner read.

## What Improved In This Pass

- Added a shared frontend model registry for visible signal cards.
- Standardized model-read objects so every card has task, target fighter, evidence, limitations, missing data, confidence, and readiness fields.
- Reworked model narratives to say what the model is trying to answer and who the task favors.
- Kept odds/market comparison visibly inactive instead of implying live market intelligence.
- Updated compact model grids and the full Models page to share one narrative layer.

## Remaining Weak Spots

- The winner model is still not marked production-ready.
- Method modeling remains weak and should not drive public-facing claims.
- Strike-volume and takedown/control reads need stronger runtime feature parity and more segment validation.
- Odds calibration remains blocked until timestamp-safe odds snapshots are normalized and reviewed.
- Some matchup cards may still have limited evidence when fighter stats are missing.

## Next Useful Work

1. Add backend response fields that directly match the standardized frontend model-read shape.
2. Add a lightweight model-read snapshot endpoint so the Models page does not depend only on latest prediction localStorage.
3. Improve runtime feature parity for strike-volume and grappling/control signals.
4. Finish odds snapshot normalization before any market model is considered.
5. Add focused UI tests for model card copy, status badges, and blocked market wording.
