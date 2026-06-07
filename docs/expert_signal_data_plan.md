# Expert Signal Data Plan

Expert picks and written fight summaries can become useful features later, but only if they are proven pre-fight.

## Acceptable Expert Inputs

Each record needs:

- `event_name`
- `event_date`
- `fighter_1`
- `fighter_2`
- `source_name`
- `source_timestamp`
- `source_url_or_id`
- `expert_pick_f1` if a pick exists
- `expert_confidence` if stated before the fight
- optional `summary_style_tags`
- `pre_fight_verified`

## Hard Rule

If `source_timestamp` is missing, after the fight, or impossible to verify, the row is excluded from model features.

Post-fight recaps, articles revealing the winner, method, scorecards, or finish timing are leakage and must not be used.

## Current Status

No expert-signal model is trained. No LLM or text model is required in this pass.

Recommended model status until verified data exists:

```json
{
  "expert_signal_model": "blocked"
}
```

## Import Workflow Later

Place local files under:

```text
data/imports/expert_predictions/
```

Then run the audit pipeline. Raw expert files should not be committed.
