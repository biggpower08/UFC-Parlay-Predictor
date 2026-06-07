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
        slug="leandroiber/ufc-stats-complete-dataset",
        name="UFC Stats Complete Dataset",
        source_type="kaggle",
        best_use="Complete UFCStats-style fight and fighter statistics.",
        helps_models=("finish_model", "goes_distance_model", "method_model", "round_model", "strike_volume_model", "takedown_control_model"),
        notes="Preferred Kaggle source for strike/takedown/control labels if available.",
    ),
    TrainingDatasetSource(
        slug="jossilva3110/ufc-dataset-1994-2026",
        name="UFC Dataset 1994-2026",
        source_type="kaggle",
        best_use="Long historical fight/stat coverage with result labels.",
        helps_models=("finish_model", "goes_distance_model", "method_model", "round_model", "strike_volume_model", "takedown_control_model"),
        notes="Use only fields that are known before the fight as model inputs; fight stats are labels.",
    ),
    TrainingDatasetSource(
        slug="leandroiber/mmastats",
        name="MMAStats Complete Database",
        source_type="kaggle",
        best_use="Granular MMA technical stats.",
        helps_models=("strike_volume_model", "takedown_control_model", "finish_model", "method_model"),
        notes="Importer will report whether UFC-only filtering and label coverage are sufficient.",
    ),
    TrainingDatasetSource(
        slug="alexmagnus24/ufc-fight-statistics-july-2016-nov-2024",
        name="UFC Fight Statistics July 2016-Nov 2024",
        source_type="kaggle",
        best_use="Round/fight-level statistics with strike and round labels.",
        helps_models=("strike_volume_model", "round_model", "finish_model", "method_model"),
        notes="Useful for strike-volume labels if significant-strike columns are present.",
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
        slug="mdabbert/ufc-fights-2010-2020-with-betting-odds",
        name="UFC Fights 2010-2020 with Betting Odds",
        source_type="kaggle",
        best_use="Historical moneyline odds matched to fights.",
        helps_models=("odds_calibration_model",),
        notes="Use for odds calibration only if fight outcomes can be matched without leakage.",
    ),
)


def curated_training_sources() -> list[dict]:
    return [source.to_dict() for source in CURATED_KAGGLE_DATASETS]
