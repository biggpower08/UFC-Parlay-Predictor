# Neural Network Experiment Plan

## Plain-English Summary
Do not move the main production modeling path to neural networks yet. The current bottlenecks are source-transfer stability, source eligibility, label quality, calibration, and runtime parity. A neural network will not fix noisy labels or mismatched sources.

## Recommendation
- Keep tree/boosting/tabular models as the primary production path for now.
- Treat neural networks as future benchmark research only.
- Do not package neural-network artifacts.
- Do not grant production status to neural-network outputs until they pass the same source-holdout, leakage, calibration, and runtime gates.

## Allowed Future Experiment
- Tabular MLP benchmark using the same train/validation/final split.
- No final-test tuning.
- Same leakage rules and forbidden-column scan.
- Same source-holdout gates.
- Compare against current best tabular models.
- Report whether it improves source transfer or only overfits the combined dataset.

## Possible Future Uses
- Fighter-history sequence model.
- Fighter-style embeddings.
- Expert-summary/text embeddings if clean text data exists.
- Ensemble member only after source/data quality improves.
