"""Manifest for supported local UFC/MMA training data sources."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class DatasetManifestEntry:
    dataset_key: str
    source_type: str
    source_slug_or_repo: str
    local_path: str
    intended_uses: list[str]
    known_risks: list[str]
    priority: int
    normalized_outputs_expected: list[str]
    raw_files_detected: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


DATASET_MANIFEST: dict[str, DatasetManifestEntry] = {
    "ufc_fight_forecast": DatasetManifestEntry(
        dataset_key="ufc_fight_forecast",
        source_type="kaggle",
        source_slug_or_repo="jerzyszocik/ufc-fight-forecast-complete-gold-modeling-dataset",
        local_path="data/imports/kaggle/ufc_fight_forecast",
        intended_uses=["winner modeling", "odds-aware winner modeling", "ranking/odds features", "modeling benchmark"],
        known_risks=["contains many engineered columns; use leakage scanner before training", "odds timing must be verified"],
        priority=10,
        normalized_outputs_expected=["fight results", "method labels", "round labels", "odds/research columns"],
    ),
    "ufc_stats_complete": DatasetManifestEntry(
        dataset_key="ufc_stats_complete",
        source_type="kaggle",
        source_slug_or_repo="leandroiber/ufc-stats-complete-dataset",
        local_path="data/imports/kaggle/ufc_stats_complete",
        intended_uses=["fight results", "method/round labels", "significant strikes", "takedowns", "control time", "fighter/fight stats"],
        known_risks=["column names vary by file", "current-fight stats are labels, not pre-fight features"],
        priority=20,
        normalized_outputs_expected=["fight results", "fight stats", "fighter profiles"],
    ),
    "ufc_1994_2026": DatasetManifestEntry(
        dataset_key="ufc_1994_2026",
        source_type="kaggle",
        source_slug_or_repo="jossilva3110/ufc-dataset-1994-2026",
        local_path="data/imports/kaggle/ufc_1994_2026",
        intended_uses=["broad historical coverage", "fighter profiles", "fight stats", "round/strike/control cross-checks"],
        known_risks=["future-dated or projected rows require review", "source ordering must not replace event dates"],
        priority=30,
        normalized_outputs_expected=["historical fights", "profile fields", "stats labels"],
    ),
    "ufc_1994_2025": DatasetManifestEntry(
        dataset_key="ufc_1994_2025",
        source_type="kaggle",
        source_slug_or_repo="neelagiriaditya/ufc-datasets-1994-2025",
        local_path="data/imports/kaggle/ufc_1994_2025",
        intended_uses=["newer UFCStats scrape cross-check", "results/method/round", "event/fight validation"],
        known_risks=["may duplicate other UFCStats-derived datasets", "fight identifiers may be source-specific"],
        priority=40,
        normalized_outputs_expected=["result cross-check rows"],
    ),
    "mdabbert_ultimate": DatasetManifestEntry(
        dataset_key="mdabbert_ultimate",
        source_type="kaggle",
        source_slug_or_repo="mdabbert/ultimate-ufc-dataset",
        local_path="data/imports/kaggle/mdabbert_ultimate",
        intended_uses=["odds-aware modeling", "betting market baseline", "winner modeling after leakage audit"],
        known_risks=["odds timestamps may be unclear", "market data must not be shown as live sportsbook odds"],
        priority=50,
        normalized_outputs_expected=["winner rows", "odds research fields"],
    ),
    "mdabbert_2010_2020_odds": DatasetManifestEntry(
        dataset_key="mdabbert_2010_2020_odds",
        source_type="kaggle",
        source_slug_or_repo="mdabbert/ufc-fights-2010-2020-with-betting-odds",
        local_path="data/imports/kaggle/mdabbert_2010_2020_odds",
        intended_uses=["historical odds comparison", "odds baseline", "calibration experiments"],
        known_risks=["timestamp quality must be reviewed before headline odds metrics", "coverage limited to 2010-2020"],
        priority=60,
        normalized_outputs_expected=["historical odds research rows"],
    ),
    "ufc_datalab": DatasetManifestEntry(
        dataset_key="ufc_datalab",
        source_type="github",
        source_slug_or_repo="komaksym/UFC-DataLab",
        local_path="data/imports/github/UFC-DataLab",
        intended_uses=["scorecards", "official-stat cross-checks", "round/decision research", "future advanced evaluation"],
        known_risks=["scorecards are post-fight labels/analysis only", "do not run scraping/OCR scripts in this workflow"],
        priority=70,
        normalized_outputs_expected=["scorecards", "round/decision supplemental data"],
    ),
}


def manifest_entries() -> list[DatasetManifestEntry]:
    return [DATASET_MANIFEST[key] for key in sorted(DATASET_MANIFEST, key=lambda key: DATASET_MANIFEST[key].priority)]


def manifest_as_dict(input_root: str | Path = "data/imports") -> dict[str, dict[str, Any]]:
    root = Path(input_root)
    output = {}
    for entry in manifest_entries():
        local = root / Path(entry.local_path).relative_to("data/imports")
        files = [str(path) for path in sorted(local.rglob("*")) if path.is_file()] if local.exists() else []
        item = entry.to_dict()
        item["local_path"] = str(local)
        item["raw_files_detected"] = files
        output[entry.dataset_key] = item
    return output


def dataset_keys() -> list[str]:
    return [entry.dataset_key for entry in manifest_entries()]
