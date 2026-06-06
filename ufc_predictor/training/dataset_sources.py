"""Curated external dataset catalog for manual/downloadable training refreshes."""

from __future__ import annotations

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class TrainingDatasetSource:
    slug: str
    name: str
    source_type: str
    best_use: str
    helps_models: tuple[str, ...]
    notes: str

    def to_dict(self) -> dict:
        payload = asdict(self)
        payload["helps_models"] = list(self.helps_models)
        return payload


CURATED_KAGGLE_DATASETS: tuple[TrainingDatasetSource, ...] = (
    TrainingDatasetSource(
        slug="jerzyszocik/ufc-fight-forecast-complete-gold-modeling-dataset",
        name="UFC Fight Forecast Complete Gold Modeling Dataset",
        source_type="kaggle",
        best_use="Leakage-aware pre-fight modeling rows, fighter features, and outcome labels.",
        helps_models=("winner_model", "finish_model", "goes_distance_model", "method_model", "round_model"),
        notes="Verify license before commercial use. Prefer pre-fight feature columns over current-fight stat columns.",
    ),
    TrainingDatasetSource(
        slug="mdabbert/ultimate-ufc-dataset",
        name="Ultimate UFC Dataset",
        source_type="kaggle",
        best_use="Broad UFC fight/fighter history with event and result labels.",
        helps_models=("finish_model", "goes_distance_model", "method_model", "round_model"),
        notes="Useful for chronological labels when event dates are present.",
    ),
    TrainingDatasetSource(
        slug="jerzyszocik/ufc-betting-odds-daily-dataset",
        name="UFC Betting Odds Daily Dataset",
        source_type="kaggle",
        best_use="Historical odds snapshots and future calibration research.",
        helps_models=("odds_calibration_model",),
        notes="Do not expose fake odds. Train odds calibration only after odds rows are matched to fight outcomes.",
    ),
    TrainingDatasetSource(
        slug="cadelueker/ufc-fighter-and-fight-stats-as-of-04-9-2025",
        name="UFC Fighter and Fight Stats as of 04-09-2025",
        source_type="kaggle",
        best_use="Fight and fighter statistics, including possible strike/takedown labels.",
        helps_models=("strike_volume_model", "takedown_control_model", "finish_model", "method_model"),
        notes="Current-fight stats may be labels only, not pre-fight features.",
    ),
    TrainingDatasetSource(
        slug="rajaisrarkiani/ufc-fights-and-fighter-stats-dataset",
        name="UFC Fights and Fighter Stats Dataset",
        source_type="kaggle",
        best_use="Fight-level outcomes and fighter statistics.",
        helps_models=("finish_model", "goes_distance_model", "method_model", "round_model", "strike_volume_model", "takedown_control_model"),
        notes="Column coverage varies; importer will report missing labels.",
    ),
)

CURATED_GITHUB_SOURCES: tuple[TrainingDatasetSource, ...] = (
    TrainingDatasetSource(
        slug="https://github.com/komaksym/UFC-DataLab",
        name="UFC DataLab",
        source_type="github",
        best_use="UFCStats-style CSV research source if the repo license and files fit the app.",
        helps_models=("finish_model", "goes_distance_model", "method_model", "round_model", "strike_volume_model", "takedown_control_model"),
        notes="Review license and CSV structure before commercial use.",
    ),
)


def curated_training_sources() -> list[dict]:
    return [source.to_dict() for source in (*CURATED_KAGGLE_DATASETS, *CURATED_GITHUB_SOURCES)]
