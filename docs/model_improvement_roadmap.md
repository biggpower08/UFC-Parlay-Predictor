# Model Improvement Roadmap

## Plain-English Summary
The model stack is moving from simple historical baselines toward MMA-specific prediction signals: style, opponent weaknesses, matchup context, data-quality gates, and selective public output. The winner model remains the main scoring candidate, while prop-style models stay conservative unless they beat baseline, pass runtime checks, and have enough transfer evidence.

## Current Priorities
- Keep `winner_model` as the primary learned win-probability candidate.
- Use Elo as a major supporting signal when both fighters have computed Elo.
- Use finish, method, round, strike-volume, and takedown/control models as confidence and matchup-context signals unless their gates justify stronger use.
- Keep odds calibration blocked until trusted pre-fight timestamps exist.
- Prefer high-confidence selective predictions over broad claims when source-holdout transfer is unstable.

## MMA-Specific Feature Work
New style and weakness features are generated only from pre-fight history:

- Style: striker, high-volume striker, power finisher, wrestler, grappler, submission threat, control fighter, high pace, durability, decision tendency, early finish threat, low-volume control, volatility.
- Opponent weakness: strike absorption, defensive volume, takedown-defense proxy, control vulnerability, submission-defense proxy, grappling exposure, durability, early-finish vulnerability, low activity, poor recent form, pace breakdown, late-fight/cardio proxy.

Current-fight result, method, strike totals, takedowns, and control values remain labels only.

## Interaction Strategy
Interaction discovery now tests MMA-specific combinations:

- physical x style
- physical x division
- striking x opponent weakness
- grappling x opponent weakness
- finishing x durability
- pace x age/activity
- scheduled rounds x pace/duration
- fighter strength vs opponent weakness

Selection must use validation data only. Final-test data is reserved for scoring and cannot choose interactions.

## Production Readiness Path
Models graduate in this order:

1. `experimental`: useful for research text only.
2. `high_confidence_only`: useful for narrow selective output, with warnings.
3. `production_candidate`: promising but needs more validation.
4. `production_ready`: all automated gates pass and artifact/runtime packaging is reviewed.

Weak or blocked models must not drive public probability claims.

## Next Work
- Improve source-holdout transfer for the winner model.
- Improve method and round submodels before public method/round confidence claims.
- Add trusted pre-fight odds timestamps before odds calibration.
- Package only small, safe artifacts that are needed by the deployed app.
