"""Automatic safe interaction candidate generation for MMA models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations

import numpy as np
import pandas as pd

from ufc_predictor.features.feature_groups import feature_group_report, group_features, safe_prefight_features
from ufc_predictor.features.feature_schema import FORBIDDEN_FEATURES


@dataclass(frozen=True)
class InteractionSpec:
    name: str
    kind: str
    input_features: tuple[str, ...]
    groups: tuple[str, ...]
    expression: str

    def to_dict(self) -> dict:
        return asdict(self)


def discover_candidate_interactions(
    frame: pd.DataFrame,
    model_name: str,
    base_features: list[str],
    *,
    max_candidates: int = 80,
    min_coverage: float = 0.65,
    min_variance: float = 1e-8,
) -> dict:
    safe_features = [feature for feature in safe_prefight_features(model_name, base_features) if feature in frame.columns]
    grouped = group_features(model_name, safe_features)
    raw_specs = generate_raw_specs(grouped, safe_features, max_candidates=max_candidates * 3)
    selected: list[InteractionSpec] = []
    rejected: list[dict] = []
    seen: set[str] = set()
    for spec in raw_specs:
        if len(selected) >= max_candidates:
            rejected.append({"name": spec.name, "reason": "candidate_cap_reached"})
            continue
        if spec.name in seen:
            continue
        seen.add(spec.name)
        reason = rejection_reason(frame, spec, min_coverage=min_coverage, min_variance=min_variance)
        if reason:
            rejected.append({"name": spec.name, "reason": reason, "kind": spec.kind, "groups": spec.groups})
        else:
            selected.append(spec)
    return {
        "model_name": model_name,
        "feature_groups": feature_group_report(model_name, safe_features),
        "candidate_count": len(raw_specs),
        "accepted_count": len(selected),
        "rejected_count": len(rejected),
        "accepted": [spec.to_dict() for spec in selected],
        "rejected": rejected[:100],
        "selection_rules": {
            "max_candidates": max_candidates,
            "min_coverage": min_coverage,
            "min_variance": min_variance,
            "final_test_used_for_selection": False,
        },
    }


def generate_raw_specs(grouped: dict[str, list[str]], safe_features: list[str], *, max_candidates: int) -> list[InteractionSpec]:
    specs: list[InteractionSpec] = []
    diff_features = [feature for feature in safe_features if any(token in feature for token in ("_diff", "_gap", "expected"))]
    for left, right in combinations(diff_features[:12], 2):
        specs.append(spec("product", (left, right), ("difference", "difference"), f"{left}_x_{right}"))
    for feature in diff_features[:18]:
        specs.append(spec("abs", (feature,), ("nonlinear",), f"abs_{feature}"))
        specs.append(spec("square", (feature,), ("nonlinear",), f"sq_{feature}"))

    group_names = sorted(grouped)
    for group_a, group_b in combinations(group_names, 2):
        for left in grouped[group_a][:5]:
            for right in grouped[group_b][:5]:
                specs.append(spec("product", (left, right), (group_a, group_b), f"{left}_x_{right}"))
                if is_rate_like(left) and is_rate_like(right):
                    specs.append(spec("ratio", (left, right), (group_a, group_b), f"ratio_{left}_to_{right}"))

    context_features = [
        feature
        for feature in safe_features
        if any(token in feature for token in ("same_division", "cross_division", "catchweight", "low_sample", "missing", "stance_known", "size_features_used"))
    ]
    for context in context_features[:10]:
        for feature in safe_features[:15]:
            if feature != context:
                specs.append(spec("context_product", (feature, context), ("context",), f"{feature}_x_{context}"))
    return specs[:max_candidates]


def spec(kind: str, inputs: tuple[str, ...], groups: tuple[str, ...], name: str) -> InteractionSpec:
    clean = "int__" + sanitize(name)
    return InteractionSpec(name=clean[:160], kind=kind, input_features=inputs, groups=groups, expression=kind)


def sanitize(value: str) -> str:
    return "".join(char if char.isalnum() or char == "_" else "_" for char in value)


def is_rate_like(feature: str) -> bool:
    lowered = feature.lower()
    return any(token in lowered for token in ("rate", "avg", "accuracy", "defense", "expected"))


def rejection_reason(frame: pd.DataFrame, spec: InteractionSpec, *, min_coverage: float, min_variance: float) -> str | None:
    if any(feature in FORBIDDEN_FEATURES for feature in spec.input_features):
        return "forbidden_or_label_feature"
    if any(feature not in frame.columns for feature in spec.input_features):
        return "missing_input_feature"
    values = compute_interaction(frame, spec)
    coverage = float(values.notna().mean()) if len(values) else 0.0
    if coverage < min_coverage:
        return "low_coverage"
    variance = float(values.dropna().var()) if values.notna().sum() > 1 else 0.0
    if not np.isfinite(variance) or variance <= min_variance:
        return "low_variance"
    return None


def add_interaction_features(frame: pd.DataFrame, specs: list[InteractionSpec] | list[dict]) -> pd.DataFrame:
    out = frame.copy()
    for raw in specs:
        spec_obj = raw if isinstance(raw, InteractionSpec) else InteractionSpec(**raw)
        out[spec_obj.name] = compute_interaction(out, spec_obj)
    return out


def compute_interaction(frame: pd.DataFrame, spec: InteractionSpec) -> pd.Series:
    first = pd.to_numeric(frame[spec.input_features[0]], errors="coerce")
    if spec.kind == "abs":
        return first.abs()
    if spec.kind == "square":
        return first.clip(-10_000, 10_000) ** 2
    second = pd.to_numeric(frame[spec.input_features[1]], errors="coerce")
    if spec.kind == "ratio":
        denominator = second.abs().clip(lower=0.05)
        return (first / denominator).replace([np.inf, -np.inf], np.nan).clip(-100, 100)
    return first * second
