"""Metrics helpers for future dedicated prop-model training."""

from __future__ import annotations

from collections import Counter
import math


def majority_class_baseline(labels) -> dict:
    counts = Counter(labels)
    total = sum(counts.values())
    if not total:
        return {"label": None, "accuracy": None, "class_counts": {}}
    label, count = counts.most_common(1)[0]
    return {
        "label": label,
        "accuracy": round(count / total, 4),
        "class_counts": {str(key): int(value) for key, value in counts.items()},
    }


def classification_metrics(y_true, y_pred, probabilities, classes) -> dict:
    total = len(y_true)
    accuracy = sum(1 for actual, pred in zip(y_true, y_pred) if actual == pred) / total if total else 0.0
    per_class = {}
    for cls in classes:
        cls_total = sum(1 for actual in y_true if actual == cls)
        cls_correct = sum(1 for actual, pred in zip(y_true, y_pred) if actual == cls and pred == cls)
        per_class[str(cls)] = round(cls_correct / cls_total, 4) if cls_total else 0.0
    balanced_accuracy = sum(per_class.values()) / len(per_class) if per_class else 0.0
    matrix = {str(actual): {str(pred): 0 for pred in classes} for actual in classes}
    for actual, pred in zip(y_true, y_pred):
        matrix[str(actual)][str(pred)] += 1
    return {
        "accuracy": round(accuracy, 4),
        "balanced_accuracy": round(balanced_accuracy, 4),
        "log_loss": round(log_loss(y_true, probabilities, classes), 4) if probabilities else None,
        "roc_auc": round(binary_roc_auc(y_true, probabilities, classes), 4) if len(classes) == 2 and probabilities else None,
        "confusion_matrix": matrix,
        "per_class_recall": per_class,
    }


def log_loss(y_true, probabilities, classes) -> float:
    class_index = {label: index for index, label in enumerate(classes)}
    eps = 1e-15
    losses = []
    for actual, probs in zip(y_true, probabilities):
        probability = max(eps, min(1 - eps, probs[class_index[actual]]))
        losses.append(-math.log(probability))
    return sum(losses) / len(losses) if losses else 0.0


def binary_roc_auc(y_true, probabilities, classes) -> float | None:
    positive = classes[-1]
    pos_index = len(classes) - 1
    scores = [(probs[pos_index], actual == positive) for actual, probs in zip(y_true, probabilities)]
    positives = sum(1 for _, is_positive in scores if is_positive)
    negatives = len(scores) - positives
    if not positives or not negatives:
        return None
    scores = sorted(scores, key=lambda item: item[0])
    rank_sum = 0.0
    for rank, (_score, is_positive) in enumerate(scores, start=1):
        if is_positive:
            rank_sum += rank
    return (rank_sum - positives * (positives + 1) / 2) / (positives * negatives)
