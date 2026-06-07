"""Column-level leakage scanning for pre-fight MMA model training."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Iterable

import pandas as pd


LABEL_ONLY_EXACT = {
    "f1_wins",
    "winner",
    "winner_name",
    "loser",
    "loser_name",
    "result",
    "method",
    "method_group",
    "method_class",
    "finish_binary",
    "fight_finished",
    "went_distance",
    "inside_distance",
    "goes_distance",
    "goes_distance_binary",
    "round_phase_class",
    "finish_round",
    "finish_time",
}

LEAKAGE_TERMS = {
    "winner",
    "loser",
    "outcome",
    "result",
    "method",
    "finish",
    "ending_round",
    "round_result",
    "scorecard",
    "judge",
    "current_fight",
}

CURRENT_FIGHT_STAT_TERMS = {
    "sig_strikes",
    "sig_str",
    "significant_strikes",
    "total_strikes",
    "takedown",
    "takedowns",
    "control_time",
    "ctrl_time",
    "submission_attempt",
    "sub_att",
}

SAFE_PREFIGHT_TERMS = {
    "age",
    "height",
    "reach",
    "stance",
    "weight_class",
    "division",
    "elo",
    "rank",
    "ranking",
    "odds",
    "moneyline",
    "implied_probability",
    "opening_line",
    "closing_line",
    "pre_fight",
    "prior",
    "career",
    "rolling",
}

RUNTIME_AVAILABLE_TERMS = {
    "age",
    "height",
    "reach",
    "stance",
    "weight_class",
    "division",
    "elo",
    "rank",
    "prior",
}


@dataclass(frozen=True)
class ColumnLeakageResult:
    column: str
    classification: str
    reason: str
    runtime_status: str = "unknown"

    def to_dict(self) -> dict:
        return asdict(self)


def scan_columns(columns: Iterable[str], allowlist: Iterable[str] | None = None, denylist: Iterable[str] | None = None) -> list[dict]:
    allow = {_column_key(column) for column in allowlist or []}
    deny = {_column_key(column) for column in denylist or []}
    return [_classify_column(str(column), allow, deny).to_dict() for column in columns]


def scan_dataframe(df: pd.DataFrame, allowlist: Iterable[str] | None = None, denylist: Iterable[str] | None = None) -> dict:
    rows = scan_columns(df.columns, allowlist=allowlist, denylist=denylist)
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["classification"]] = counts.get(row["classification"], 0) + 1
    return {
        "column_count": int(len(df.columns)),
        "columns": rows,
        "summary": counts,
        "blocked_feature_columns": [
            row["column"]
            for row in rows
            if row["classification"] in {"label_only", "leakage_excluded"}
        ],
    }


def safe_feature_columns(df: pd.DataFrame, allowlist: Iterable[str] | None = None, denylist: Iterable[str] | None = None) -> list[str]:
    report = scan_dataframe(df, allowlist=allowlist, denylist=denylist)
    return [
        row["column"]
        for row in report["columns"]
        if row["classification"] in {"safe_prefight_feature", "runtime_available", "derived_possible", "training_only"}
    ]


def _classify_column(column: str, allow: set[str], deny: set[str]) -> ColumnLeakageResult:
    key = _column_key(column)
    if key in deny:
        return ColumnLeakageResult(column, "leakage_excluded", "Explicitly denied by leakage config.")
    if key in allow:
        return ColumnLeakageResult(column, "safe_prefight_feature", "Explicitly allowed by leakage config.", "training_only")
    if key in LABEL_ONLY_EXACT:
        return ColumnLeakageResult(column, "label_only", "Outcome/target column should only be used as a label.")
    if key == "f1_wins" or key.endswith("_wins") and key.startswith("f"):
        return ColumnLeakageResult(column, "label_only", "Target-derived winner column.")
    if _contains_any(key, LEAKAGE_TERMS):
        return ColumnLeakageResult(column, "leakage_excluded", "Column name implies fight outcome or post-fight information.")
    if _contains_any(key, CURRENT_FIGHT_STAT_TERMS):
        return ColumnLeakageResult(column, "leakage_excluded", "Current-fight stats are labels, not pre-fight features.")
    if "expert" in key or "summary" in key:
        return ColumnLeakageResult(column, "unknown_review_needed", "Expert/text signal needs pre-fight timestamp verification.")
    if "odds" in key or "moneyline" in key or "implied_probability" in key:
        if "pre_fight" in key or "opening" in key or "closing" in key:
            return ColumnLeakageResult(column, "safe_prefight_feature", "Clearly pre-fight market signal.", "training_only")
        return ColumnLeakageResult(column, "unknown_review_needed", "Odds timing is unclear; verify pre-fight timestamp before training.")
    if _contains_any(key, RUNTIME_AVAILABLE_TERMS):
        return ColumnLeakageResult(column, "runtime_available", "App can plausibly produce this pre-fight feature.", "runtime_available")
    if "source_timestamp" in key or "source_url" in key or "source_name" in key:
        return ColumnLeakageResult(column, "training_only", "Source metadata is useful for audit but not runtime prediction.")
    if _contains_any(key, SAFE_PREFIGHT_TERMS):
        return ColumnLeakageResult(column, "safe_prefight_feature", "Column appears to be a pre-fight feature.", "training_only")
    return ColumnLeakageResult(column, "unknown_review_needed", "Column needs manual review before entering model features.")


def _column_key(value: str) -> str:
    return str(value).strip().lower().replace(" ", "_").replace(".", "").replace("-", "_").replace("%", "pct")


def _contains_any(value: str, terms: set[str]) -> bool:
    return any(term in value for term in terms)
