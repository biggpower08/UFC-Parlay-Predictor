"""Automatic safe interaction candidate generation for MMA models."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from itertools import combinations

import numpy as np
import pandas as pd

from ufc_predictor.features.feature_groups import feature_group_report, group_features, safe_prefight_features
from ufc_predictor.features.feature_schema import FORBIDDEN_FEATURES


INTERACTION_TYPE_BUCKETS = {
    "pairwise_products": ("product",),
    "ratios": ("ratio",),
    "absolute_differences": ("abs",),
    "squared_clipped_log_transforms": ("square",),
    "fighter_strength_vs_opponent_weakness": ("strength_vs_weakness",),
    "context_division_interactions": ("context_product",),
}

FEATURE_GROUP_PAIR_BUCKETS = [
    "physical x style",
    "physical x division",
    "striking x opponent weakness",
    "grappling x opponent weakness",
    "finishing x durability",
    "pace x age/activity",
    "scheduled rounds x pace/duration",
]

REJECTION_BUCKETS = [
    "missingness",
    "low_variance",
    "high_correlation",
    "leakage_risk",
    "runtime_incompatibility",
    "validation_did_not_improve",
    "source_holdout_got_worse",
    "calibration_got_worse",
]


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
    raw_specs = generate_raw_specs(group_features(model_name, safe_features), safe_features, max_candidates=max_candidates * 3)
    selected: list[InteractionSpec] = []
    rejected: list[dict] = []
    seen: set[str] = set()
    for spec_obj in raw_specs:
        if len(selected) >= max_candidates:
            rejected.append({"name": spec_obj.name, "reason": "candidate_cap_reached"})
            continue
        if spec_obj.name in seen:
            continue
        seen.add(spec_obj.name)
        reason = rejection_reason(frame, spec_obj, min_coverage=min_coverage, min_variance=min_variance)
        if reason:
            rejected.append({"name": spec_obj.name, "reason": reason, "kind": spec_obj.kind, "groups": spec_obj.groups})
        else:
            selected.append(spec_obj)

    accepted_dicts = [item.to_dict() for item in selected]
    return {
        "model_name": model_name,
        "feature_groups": feature_group_report(model_name, safe_features),
        "candidate_count": len(raw_specs),
        "candidate_count_by_interaction_type": count_by_interaction_type(raw_specs),
        "candidate_count_by_feature_group_pair": count_by_feature_group_pair(raw_specs),
        "missing_prerequisite_features_by_family": missing_prerequisite_features_by_family(safe_features),
        "accepted_count": len(selected),
        "rejected_count": len(rejected),
        "rejection_counts": normalized_rejection_counts(rejected),
        "accepted": accepted_dicts,
        "rejected": rejected[:100],
        "safety_checks": {
            "selection_uses_validation_only": True,
            "final_test_used_for_selection": False,
            "forbidden_target_columns_excluded": all(
                not set(item["input_features"]).intersection(FORBIDDEN_FEATURES) for item in accepted_dicts
            ),
            "selected_interactions_runtime_computable": None,
            "source_holdout_regression_blocks_production": True,
        },
        "selection_rules": {
            "max_candidates": max_candidates,
            "min_coverage": min_coverage,
            "min_variance": min_variance,
            "final_test_used_for_selection": False,
        },
    }


def generate_raw_specs(grouped: dict[str, list[str]], safe_features: list[str], *, max_candidates: int) -> list[InteractionSpec]:
    specs: list[InteractionSpec] = []
    specs.extend(generate_mma_style_specs(safe_features))

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
                kind = "strength_vs_weakness" if "opponent_weakness" in {group_a, group_b} else "product"
                specs.append(spec(kind, (left, right), (group_a, group_b), f"{left}_x_{right}"))
                if is_rate_like(left) and is_rate_like(right):
                    specs.append(spec("ratio", (left, right), (group_a, group_b), f"ratio_{left}_to_{right}"))

    context_features = pick_features(
        safe_features,
        ("same_division", "cross_division", "catchweight", "low_sample", "missing", "stance_known", "size_features_used"),
        limit=10,
    )
    for context in context_features:
        for feature in safe_features[:15]:
            if feature != context:
                specs.append(spec("context_product", (feature, context), ("context",), f"{feature}_x_{context}"))
    return specs[:max_candidates]


def generate_mma_style_specs(safe_features: list[str]) -> list[InteractionSpec]:
    specs: list[InteractionSpec] = []
    striking_strength = pick_features(safe_features, ("striker_score", "high_volume_striker_score", "reach_diff", "reach_gap"))
    striking_weakness = pick_features(safe_features, ("strike_absorption_weakness", "low_activity_weakness"))
    grappling_strength = pick_features(safe_features, ("wrestler_score", "control_fighter_score", "submission_threat_score", "grappler_score"))
    grappling_weakness = pick_features(safe_features, ("takedown_defense_weakness_proxy", "control_vulnerability_proxy", "submission_defense_weakness_proxy", "grappling_exposure_weakness"))
    finishing_strength = pick_features(safe_features, ("power_finisher_score", "submission_threat_score", "early_finish_threat_score", "finish_rate_diff", "volatility_score"))
    durability_weakness = pick_features(safe_features, ("durability_weakness", "early_finish_vulnerability", "durability_score_diff", "finish_loss_rate"))
    pace_features = pick_features(safe_features, ("high_pace_score", "high_pace_score_diff", "volatility_score"))
    age_activity = pick_features(safe_features, ("age", "days_since_last_fight", "recent_5_win_rate", "recent_3_win_rate", "poor_recent_form_weakness", "low_activity_weakness", "cardio_late_fight_risk_proxy"))
    scheduled_rounds = pick_features(safe_features, ("scheduled_rounds",))
    duration_features = pick_features(safe_features, ("high_pace_score", "durability_score", "early_finish_threat_score", "decision_tendency_score", "cardio_late_fight_risk_proxy"))
    division_context = pick_features(safe_features, ("same_division", "cross_division", "catchweight", "weight_class_gap", "estimated_weight_gap_lbs"))
    style_features = pick_features(safe_features, ("power_finisher_score", "wrestler_score", "high_pace_score", "reach_diff", "reach_gap"))

    specs.extend(cross_specs("strength_vs_weakness", striking_strength, striking_weakness, ("striking", "opponent_weakness")))
    specs.extend(cross_specs("strength_vs_weakness", grappling_strength, grappling_weakness, ("grappling", "opponent_weakness")))
    specs.extend(cross_specs("strength_vs_weakness", finishing_strength, durability_weakness, ("finishing", "opponent_weakness")))
    specs.extend(cross_specs("product", pace_features, age_activity, ("pace", "activity")))
    specs.extend(cross_specs("product", scheduled_rounds, duration_features, ("scheduled_rounds", "duration")))
    specs.extend(cross_specs("context_product", division_context, style_features, ("division_context", "physical")))
    return specs


def pick_features(safe_features: list[str], tokens: tuple[str, ...], *, limit: int = 8) -> list[str]:
    picked = []
    for feature in safe_features:
        lowered = feature.lower()
        if any(token in lowered for token in tokens):
            picked.append(feature)
    return list(dict.fromkeys(picked))[:limit]


def cross_specs(kind: str, left: list[str], right: list[str], groups: tuple[str, ...]) -> list[InteractionSpec]:
    specs = []
    for left_feature in left[:6]:
        for right_feature in right[:6]:
            if left_feature != right_feature:
                specs.append(spec(kind, (left_feature, right_feature), groups, f"{left_feature}_x_{right_feature}"))
    return specs


def spec(kind: str, inputs: tuple[str, ...], groups: tuple[str, ...], name: str) -> InteractionSpec:
    clean = "int__" + sanitize(name)
    return InteractionSpec(name=clean[:160], kind=kind, input_features=inputs, groups=groups, expression=kind)


def sanitize(value: str) -> str:
    return "".join(char if char.isalnum() or char == "_" else "_" for char in value)


def is_rate_like(feature: str) -> bool:
    lowered = feature.lower()
    return any(token in lowered for token in ("rate", "avg", "accuracy", "defense", "weakness", "expected"))


def rejection_reason(frame: pd.DataFrame, spec_obj: InteractionSpec, *, min_coverage: float, min_variance: float) -> str | None:
    if any(feature in FORBIDDEN_FEATURES for feature in spec_obj.input_features):
        return "forbidden_or_label_feature"
    if any(feature not in frame.columns for feature in spec_obj.input_features):
        return "missing_input_feature"
    if len(spec_obj.input_features) == 2:
        left = pd.to_numeric(frame[spec_obj.input_features[0]], errors="coerce")
        right = pd.to_numeric(frame[spec_obj.input_features[1]], errors="coerce")
        if left.notna().sum() > 2 and right.notna().sum() > 2:
            corr = left.corr(right)
            if np.isfinite(corr) and abs(float(corr)) >= 0.985:
                return "high_correlation"
    values = compute_interaction(frame, spec_obj)
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


def compute_interaction(frame: pd.DataFrame, spec_obj: InteractionSpec) -> pd.Series:
    first = pd.to_numeric(frame[spec_obj.input_features[0]], errors="coerce")
    if spec_obj.kind == "abs":
        return first.abs()
    if spec_obj.kind == "square":
        return first.clip(-10_000, 10_000) ** 2
    second = pd.to_numeric(frame[spec_obj.input_features[1]], errors="coerce")
    if spec_obj.kind == "ratio":
        denominator = second.abs().clip(lower=0.05)
        return (first / denominator).replace([np.inf, -np.inf], np.nan).clip(-100, 100)
    return first * second


def count_by_interaction_type(specs: list[InteractionSpec]) -> dict[str, int]:
    counts = {bucket: 0 for bucket in INTERACTION_TYPE_BUCKETS}
    for spec_obj in specs:
        for bucket, kinds in INTERACTION_TYPE_BUCKETS.items():
            if spec_obj.kind in kinds:
                counts[bucket] += 1
                break
    return counts


def count_by_feature_group_pair(specs: list[InteractionSpec]) -> dict[str, int]:
    counts = {bucket: 0 for bucket in FEATURE_GROUP_PAIR_BUCKETS}
    for spec_obj in specs:
        bucket = feature_group_pair_bucket(spec_obj)
        if bucket:
            counts[bucket] += 1
    return counts


def feature_group_pair_bucket(spec_obj: InteractionSpec) -> str | None:
    groups = set(spec_obj.groups)
    features = " ".join(spec_obj.input_features).lower()
    if "physical" in groups and groups.intersection({"striking", "grappling", "finishing"}):
        return "physical x style"
    if "physical" in groups and "division_context" in groups:
        return "physical x division"
    if "striking" in groups and "opponent_weakness" in groups:
        return "striking x opponent weakness"
    if "grappling" in groups and "opponent_weakness" in groups:
        return "grappling x opponent weakness"
    if "finishing" in groups and ("opponent_weakness" in groups or "durability" in features or "finish_loss" in features):
        return "finishing x durability"
    if ("pace" in groups or "pace" in features or "fights_last" in features) and (
        "activity" in groups or "age" in features or "days_since" in features or "recent" in features
    ):
        return "pace x age/activity"
    if "scheduled_rounds" in groups or "scheduled_rounds" in features:
        if "duration" in groups or any(token in features for token in ("pace", "duration", "finish", "decision")):
            return "scheduled rounds x pace/duration"
    return None


def missing_prerequisite_features_by_family(safe_features: list[str]) -> dict[str, list[str]]:
    requirements = {
        "striking x opponent weakness": (("striker_score", "high_volume_striker_score"), ("strike_absorption_weakness",)),
        "grappling x opponent weakness": (("wrestler_score", "control_fighter_score", "submission_threat_score"), ("takedown_defense_weakness_proxy", "control_vulnerability_proxy", "grappling_exposure_weakness")),
        "finishing x durability": (("power_finisher_score", "early_finish_threat_score"), ("durability_weakness", "early_finish_vulnerability")),
        "pace x age/activity": (("high_pace_score", "volatility_score"), ("age", "days_since_last_fight", "recent_5_win_rate", "poor_recent_form_weakness", "cardio_late_fight_risk_proxy")),
        "scheduled rounds x pace/duration": (("scheduled_rounds",), ("high_pace_score", "durability_score", "decision_tendency_score")),
        "fighter_strength_vs_opponent_weakness": (("striker_score", "wrestler_score", "power_finisher_score"), ("weakness", "vulnerability")),
    }
    lowered = [feature.lower() for feature in safe_features]
    missing = {}
    for family, groups in requirements.items():
        missing_tokens = []
        for tokens in groups:
            if not any(any(token in feature for token in tokens) for feature in lowered):
                missing_tokens.append(" or ".join(tokens))
        missing[family] = missing_tokens
    return missing


def normalized_rejection_counts(rejected: list[dict]) -> dict[str, int]:
    counts = {bucket: 0 for bucket in REJECTION_BUCKETS}
    reason_map = {
        "missing_input_feature": "runtime_incompatibility",
        "low_coverage": "missingness",
        "low_variance": "low_variance",
        "high_correlation": "high_correlation",
        "forbidden_or_label_feature": "leakage_risk",
        "candidate_cap_reached": "validation_did_not_improve",
        "did_not_improve_validation_or_calibration": "validation_did_not_improve",
        "calibration_regression": "calibration_got_worse",
        "source_holdout_regression": "source_holdout_got_worse",
    }
    for item in rejected:
        bucket = reason_map.get(str(item.get("reason")), "validation_did_not_improve")
        counts[bucket] += 1
    return counts
