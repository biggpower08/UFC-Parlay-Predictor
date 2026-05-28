"""Future prop-model training entrypoint.

Real training is intentionally gated behind source-health and dataset-readiness
checks. This module exists so training can be added without changing public
prediction code.
"""

from __future__ import annotations


def training_blocker_message() -> str:
    return (
        "Dedicated prop-model training is blocked until credible source health "
        "and leakage-safe chronological training rows are proven."
    )
