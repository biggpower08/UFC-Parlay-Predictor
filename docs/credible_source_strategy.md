# Credible Source Strategy

Dedicated prop models must not be trained until the source pipeline can prove enough credible, chronological fight data.

## Source Audit

| Source | Status | Useful Data | Training Readiness |
| --- | --- | --- | --- |
| UFCStats | unreliable | Event history, fight results, method, round, time, fighter profiles, significant strikes, takedowns, attempts, and detailed fight stats when pages are accessible. | Primary target, but live requests have returned browser challenge pages. Use source-health first. |
| Sherdog | not_implemented | Event history, fight results, method, round, time, fighter records, and profile pages. | Backup candidate. Needs a polite parser and terms review before use. |
| Tapology | not_implemented | Event pages, fight results, records, fighter profiles, schedules, and broad MMA coverage. | Supplemental candidate. Needs a polite parser and terms review before use. |
| Local CSV/import datasets | partially_usable | Historical fight rows, winner/method/round labels, and fighter profile/stat columns depending on file. | Useful for audits and Elo/model prototyping, but must be checked for dates, source provenance, and leakage before training. |
| Cached/manual UFCStats HTML | partially_usable | Previously saved UFCStats pages can validate parsers and import manually reviewed events. | Good fallback while live source health is challenged. |
| Future paid/official provider | not_implemented | Could provide licensed odds, results, and richer stats. | Best long-term option for odds history and betting intelligence if budget allows. |

## Training Gate

A model can only move from `not_trained` to `trained` after all of these exist:

- credible source or approved imported dataset
- chronological event dates
- labels for the target model
- leakage-safe feature rows using only pre-fight information
- saved artifact
- validation metrics
- metadata with training source, row counts, data cutoff, trained timestamp, and leakage check

If source-health is `challenged`, `blocked`, or `unavailable`, do not train.

## Model Readiness

- Finish model: blocked until credible chronological fight-result rows are ready.
- Goes-distance model: blocked until credible chronological fight-result rows are ready.
- Method model: blocked until credible chronological method labels are ready.
- Round-phase model: blocked until credible chronological round labels are ready.
- Strike-volume model: blocked until per-fight significant strike totals exist.
- Takedown/control model: blocked until per-fight takedown/control labels exist.

## Odds / Betting Intelligence

Odds-edge models are blocked until historical odds snapshots exist. The current odds provider layer should stay disabled by default and return a clear disabled status when no provider is configured.
