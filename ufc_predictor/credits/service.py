"""Disabled-by-default prediction-credit gate scaffolding."""

from __future__ import annotations

from dataclasses import dataclass

from ufc_predictor.config import settings


@dataclass(frozen=True)
class CreditDecision:
    allowed: bool
    status: dict
    usage_source: str


def credit_status(free_predictions_used: int = 0, credits_remaining: int = 0) -> dict:
    """Return the public credit status shape without requiring auth or Stripe."""
    free_limit = max(int(settings.FREE_PREDICTION_LIMIT), 0)
    used = max(int(free_predictions_used or 0), 0)
    credits = max(int(credits_remaining or 0), 0)
    remaining = max(free_limit - used, 0)
    payment_required = bool(settings.ENABLE_CREDIT_GATE and remaining <= 0 and credits <= 0)
    return {
        "enabled": bool(settings.ENABLE_CREDIT_GATE),
        "stripe_enabled": bool(getattr(settings, "ENABLE_STRIPE", False)),
        "free_prediction_limit": free_limit,
        "free_predictions_used": used,
        "free_predictions_remaining": remaining,
        "credits_remaining": credits,
        "credit_packs": list(settings.CREDIT_PACK_OPTIONS),
        "payment_required": payment_required,
        "message": _status_message(payment_required),
    }


def evaluate_prediction_credit(free_predictions_used: int = 0, credits_remaining: int = 0) -> CreditDecision:
    """Decide whether a prediction may run.

    With ENABLE_CREDIT_GATE=false, this is intentionally a no-op so current
    prediction behavior does not change.
    """
    status = credit_status(free_predictions_used=free_predictions_used, credits_remaining=credits_remaining)
    if not status["enabled"]:
        return CreditDecision(allowed=True, status=status, usage_source="gate_disabled")
    if status["free_predictions_remaining"] > 0:
        return CreditDecision(allowed=True, status=status, usage_source="free")
    if status["credits_remaining"] > 0:
        return CreditDecision(allowed=True, status=status, usage_source="paid")
    return CreditDecision(allowed=False, status=payment_required_response(), usage_source="blocked")


def payment_required_response() -> dict:
    return {
        "status": "payment_required",
        "message": "You have used your free predictions. Buy prediction credits to continue.",
        "credit_packs": list(settings.CREDIT_PACK_OPTIONS),
    }


def record_prediction_usage(prediction_id: str | None, decision: CreditDecision) -> dict:
    """Return future usage metadata without mutating state while disabled.

    Real decrement/purchase accounting should be added with auth plus a payment
    provider. Until then this function documents the usage source and prevents
    accidental decrements while the gate is off.
    """
    return {
        "prediction_id": prediction_id,
        "credits_used": 0 if decision.usage_source == "gate_disabled" else 1,
        "source": decision.usage_source,
        "decremented": bool(settings.ENABLE_CREDIT_GATE and decision.usage_source in {"free", "paid"}),
    }


def _status_message(payment_required: bool) -> str:
    if payment_required:
        return "You have used your free predictions. Buy prediction credits to continue."
    if settings.ENABLE_CREDIT_GATE:
        return "Prediction credits are active."
    return "Prediction credits are coming soon. The credit gate is currently disabled."
