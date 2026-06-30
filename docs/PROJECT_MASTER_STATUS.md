# UFC/MMA AI Predictor Master Project Status

_Generated: 2026-06-30T03:17:22.341788+00:00_

## 1. Plain-English Project Summary
The app has working winner predictions, Elo support, analysis pages, betting-read scaffolding, and a growing model audit system. The current priority is production readiness: source eligibility, label quality, source-transfer stability, calibration, and safe runtime output. No model is currently marked production-ready, and no model artifacts are packaged yet.

## 2. Current Production Readiness Status
- `winner_model` is `high_confidence_only`, not `production_ready`.
- Duration and round binary models are `production_candidate`, not `production_ready`.
- `method_umbrella_model` and `method_model` are `weak_or_failed_baseline`.
- `finish_type_model`, `strike_volume_model`, and `takedown_control_model` are experimental/context-only.
- `odds_calibration_model` is blocked until trusted pre-fight odds timestamps exist.
- Current downloaded odds audit status: `blocked_missing_snapshot_timestamps` for `UFC_betting_odds.csv`.
- No model artifacts are packaged yet.

## 3. Current Model Status Table
| Model | Production Status | Main Metric | Baseline | Source Holdout | Public Use |
|---|---|---:|---:|---|---|
| winner_model | high_confidence_only | 0.9606 | 0.52 | needs_review | research/high-confidence selective predictions only |
| fight_duration_model | production_candidate | 0.8596 | 0.5191 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_model | production_candidate | 0.8596 | 0.5191 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| goes_distance_model | production_candidate | 0.8596 | 0.5191 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| over_1_5_model | production_candidate | 0.8064 | 0.6976 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| over_2_5_model | production_candidate | 0.813 | 0.5621 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| ends_before_round_3_model | production_candidate | 0.7911 | 0.609 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_in_round_1_model | production_candidate | 0.8467 | 0.7628 | stable | candidate for limited internal validation; artifact packaging still requires explicit review |
| finish_type_model | experimental | 0.7956 | 0.6412 | needs_review | research only until source-holdout stabilizes |
| method_umbrella_model | weak_or_failed_baseline | 0.5191 | 0.5191 | unstable | research only |
| method_model | weak_or_failed_baseline | 0.5191 | 0.5191 | unstable | research only |
| strike_volume_model | experimental | 0.5908 | 0.3623 | unstable | research only until source-holdout stabilizes |
| takedown_control_model | experimental | 0.7349 | 0.5897 | needs_review | research only until source-holdout stabilizes |
| odds_calibration_model | blocked | not available yet | not available yet | not available yet | not available |

## 4. Current Dataset / Source Status
| Source | Rows | Date Range | Final-Test Rows | Drift Grade |
|---|---:|---|---:|---|
| mdabbert_ultimate | 7190 | 2010-03-21 to 2026-04-04 | 1210 | medium drift |
| ufc_1994_2025 | 16674 | 1994-03-11 to 2025-09-06 | 922 | high drift |
| ufc_1994_2026 | 8551 | 1994-03-11 to 2026-03-07 | 1164 | high drift |
| ufc_fight_forecast | 8231 | 1994-03-11 to 2025-10-04 | 955 | medium drift |
| ufc_stats_complete | 8709 | 1993-11-12 to 2026-05-16 | 1286 | high drift |

## 5. Current Source-Eligibility Rules
- `ufc_stats_complete` should be treated primarily as a stat-rich source, not a universal result-label source.
- No-contest, draw, unknown, or missing-result rows must not create fake winner, finish, method, or round labels.
- Result models require safe winner/result labels.
- Round models require safe finish round/time and scheduled-round parsing.
- Strike/takedown models require reliable stat coverage.
| Source | Safe Uses | Unsafe Uses |
|---|---|---|
| ufc_stats_complete | strike labels, takedown/control labels, stat coverage cross-checks | universal winner labels, universal duration labels, universal method labels, universal round labels |
| mdabbert_ultimate | broad result history, winner/duration/method labels where present, odds-aware research review | primary strike/takedown/control labels when detailed stats are missing |
| ufc_1994_2025 | broad fight history, result/method/round labels, stat labels with drift review | unreviewed production stat modeling |
| ufc_1994_2026 | broad fight history, result/method/round labels | unreviewed production use where holdout drift is high |
| ufc_fight_forecast | broad result history, result/method/round labels, some stat labels | winner production claims until transfer stabilizes |

## 6. Current Source-Holdout / Source-Transfer Status
- Stable source-holdout can restore `production_candidate` status.
- Severe source-holdout regression blocks candidate/ready status.
- `ufc_stats_complete` remains the main stat-source risk for strike/takedown models.
- `ufc_1994_2026` is currently the weakest holdout source for several duration/round candidates.

## 7. Current Interaction Discovery Status
- Interaction selection uses validation only; final test is not used for selection.
- Selected interactions must be runtime-computable and cannot include target/current-fight columns.
| Model | Candidates | Selected | Selection Status | MMA Family Coverage |
|---|---:|---:|---|---|
| winner_model | 240 | 0 | base_features_kept | limited/zero |
| fight_duration_model | 240 | 5 | selected | limited/zero |
| over_1_5_model | 240 | 20 | selected | limited/zero |
| over_2_5_model | 240 | 0 | base_features_kept | limited/zero |
| ends_before_round_3_model | 240 | 20 | selected | limited/zero |
| finish_in_round_1_model | 240 | 0 | base_features_kept | limited/zero |
| finish_type_model | 240 | 0 | base_features_kept | limited/zero |
| method_umbrella_model | 0 | 0 | not_run_composite_model | limited/zero |
| strike_volume_model | 240 | 5 | selected | limited/zero |
| takedown_control_model | 240 | 10 | selected | limited/zero |
| finish_model | 240 | 5 | selected | limited/zero |
| goes_distance_model | 240 | 5 | selected | limited/zero |
| method_model | 0 | 0 | not_run_composite_model | limited/zero |
| round_phase_model | 0 | 0 | not_run_composite_summary | limited/zero |
| round_model | 0 | 0 | not_run_composite_summary | limited/zero |
| strike_volume_regression | 0 | 0 | not_run | limited/zero |
| odds_calibration_model | 0 | 0 | not_run | limited/zero |

## 8. Current Calibration Status
- Current `--calibrate` behavior is basic probability scoring/reporting, not a full validation-only calibration refactor.
- First calibration targets: winner high-confidence output, fight duration, over 2.5, and ends-before-round-3.
- Weak method models, blocked odds, and unstable experimental models are not worth calibrating yet.

## 9. Current UI / Product Status
- Home, Analysis, Stats, and Odds pages exist as product surfaces.
- Odds page remains model-informed/read-only; no fake sportsbook odds or bet placement.
- Public output should show model status badges and source/data-quality warnings before strong claims.

## 10. Current Backend/API Status
- FastAPI serves the static Next.js frontend.
- Prediction endpoints should include model statuses, unavailable models, unstable models, public warning text, and data-quality fields as this moves toward release.
- App startup must not require local Kaggle/import files.

## 11. Current Deployment / Render Status
- Single Render-hosted FastAPI app remains the deployment target.
- Do not split frontend/backend deployment.
- Render config should keep `/health` available.

## 12. Current Supabase / Database Status
- Supabase remains the production database.
- Kaggle/local CSVs are raw training inputs only and are not required at runtime.
- Normalized production data should live in Supabase/backend when needed by the deployed app.

## 13. Current Repo Hygiene Status
- `fighters.db`, raw imports, normalized combined CSVs, backtest predictions, `.env`, `kaggle.json`, virtual environments, frontend build output, and pytest temp/cache folders must not be committed.
- Recent hygiene checks confirmed generated database files are ignored and not tracked.

## 14. What Is Safe To Show Publicly
- Winner model evidence only in high-confidence/selective mode.
- Candidate duration/round reads as cautious model-candidate context after runtime review.
- Elo, peak Elo, fights counted, status labels, and simple data-quality warnings.
- Informational prop-style reads only, not guaranteed outcomes or sportsbook lines.

## 15. What Must Stay Experimental
- `finish_type_model`.
- `strike_volume_model`.
- `takedown_control_model`.
- Any source-transfer unstable or weak model.
- Any model using source ID as a production shortcut.

## 16. What Is Blocked
- `odds_calibration_model` until trusted pre-fight odds timestamps exist.
- Production-ready model claims.
- Artifact packaging without manual review and gate confirmation.
- Public method-model confidence until method models beat baseline.

## 17. Biggest Technical Risks
- Runtime feature parity for candidate artifacts.
- Probability calibration is not yet full validation-only calibration.
- Backtest/evaluation scripts are still computationally heavy.
- Model statuses can drift if reports are not regenerated together.

## 18. Biggest Data Risks
- Source label definitions differ across datasets.
- `ufc_stats_complete` is stat-rich but not a universal result-label source.
- Method labels and finish-type classes remain noisy.
- Odds data is not trusted without pre-fight timestamps.

## 19. Biggest Product Risks
- Overstating experimental prop reads.
- Showing probability-style outputs without calibration/source-transfer support.
- Making betting-help language sound like guaranteed financial advice.
- Shipping a paywall before trust/warnings/status handling is ready.

## 20. Next 2-Week Build Plan
1. Keep this master status and index current.
2. Enforce source eligibility in model/retraining workflows.
3. Add model-status and data-quality fields to API responses.
4. Add public-safe model/status badges in the UI.
5. Draft validation-only calibration implementation for strongest candidates.
6. Keep odds blocked until trusted timestamps exist.

## 21. Next 4-Week Production Plan
1. Review candidate winner/duration/round artifacts manually.
2. Implement true validation-only calibration for stable candidate models.
3. Integrate `ensemble_breakdown` into API/UI with unavailable/unstable model lists.
4. Add limited-release/high-confidence research mode.
5. Keep method/stat models context-only until source transfer improves.
6. Consider neural-network benchmark only after source/data issues improve.

## 22. Exact Next Tasks For Codex
- Add model registry health endpoint and prediction response model-status fields.
- Add source eligibility filtering to the next training/evaluation pass.
- Implement validation-only calibration report for candidate models.
- Add UI badges for model status and data quality.
- Keep reports synchronized with this master status.

## 23. Commands To Run
```powershell
cd C:\dev\mma-ai
$env:MMA_AI_PYTHON="C:\venvs\mma-ai\Scripts\python.exe"
& $env:MMA_AI_PYTHON scripts\build_master_project_status.py
& $env:MMA_AI_PYTHON scripts\source_transfer_diagnostics.py
$TempTestDir = "$env:TEMP\mma_ai_pytest_$([guid]::NewGuid().ToString())"
& $env:MMA_AI_PYTHON -m pytest ufc_predictor\tests -q --basetemp $TempTestDir
```

## 24. Files/Folders Not To Commit
- `data/imports/`
- `ufc_predictor/data/processed/fighters.db`
- `ufc_predictor/data/processed/imports/normalized_fights_combined.csv`
- `ufc_predictor/data/processed/backtest_predictions.json`
- `ufc_predictor/data/processed/training_imports/`
- `.env`, `kaggle.json`, `.venv`, `C:\venvs`, `node_modules`, `.next`, pytest temp/cache folders

## Source Report Pointers
- Model accuracy: `docs/model_accuracy_report.md`
- Backtest: `docs/backtest_report.md`
- Source transfer diagnostics: `docs/source_transfer_diagnostics.md`
- Drift report: `docs/source_feature_label_drift_report.md`
- Source strategy ablation: `docs/source_strategy_ablation_report.md`
- Source normalization rules: `docs/source_normalization_rules.md`
- Artifact packaging plan: `docs/model_artifact_packaging_plan.md`
