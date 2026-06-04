from ufc_predictor.config import settings
from ufc_predictor.credits.service import credit_status, evaluate_prediction_credit, payment_required_response, record_prediction_usage


def test_credit_gate_defaults_disabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_CREDIT_GATE", False)
    monkeypatch.setattr(settings, "FREE_PREDICTION_LIMIT", 3)
    monkeypatch.setattr(settings, "CREDIT_PACK_OPTIONS", [5, 10, 15, 20])

    status = credit_status()
    decision = evaluate_prediction_credit()
    usage = record_prediction_usage("prediction-id", decision)

    assert status["enabled"] is False
    assert status["free_prediction_limit"] == 3
    assert status["free_predictions_remaining"] == 3
    assert status["credit_packs"] == [5, 10, 15, 20]
    assert decision.allowed is True
    assert decision.usage_source == "gate_disabled"
    assert usage["credits_used"] == 0
    assert usage["decremented"] is False


def test_payment_required_shape_when_gate_enabled(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_CREDIT_GATE", True)
    monkeypatch.setattr(settings, "FREE_PREDICTION_LIMIT", 3)
    monkeypatch.setattr(settings, "CREDIT_PACK_OPTIONS", [5, 10, 15, 20])

    decision = evaluate_prediction_credit(free_predictions_used=3, credits_remaining=0)
    response = payment_required_response()

    assert decision.allowed is False
    assert decision.status["status"] == "payment_required"
    assert response == {
        "status": "payment_required",
        "message": "You have used your free predictions. Buy prediction credits to continue.",
        "credit_packs": [5, 10, 15, 20],
    }


def test_enabled_gate_allows_free_or_paid_prediction(monkeypatch):
    monkeypatch.setattr(settings, "ENABLE_CREDIT_GATE", True)
    monkeypatch.setattr(settings, "FREE_PREDICTION_LIMIT", 3)
    monkeypatch.setattr(settings, "CREDIT_PACK_OPTIONS", [5, 10, 15, 20])

    free_decision = evaluate_prediction_credit(free_predictions_used=2, credits_remaining=0)
    paid_decision = evaluate_prediction_credit(free_predictions_used=3, credits_remaining=5)

    assert free_decision.allowed is True
    assert free_decision.usage_source == "free"
    assert paid_decision.allowed is True
    assert paid_decision.usage_source == "paid"
