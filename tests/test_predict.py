import pytest

from src.models.predict import FinGuardPredictor


@pytest.fixture
def predictor():
    return FinGuardPredictor()


def test_prediction_structure(predictor):
    transaction = {
        "step": 650,
        "type": "TRANSFER",
        "amount": 12500,
        "oldbalanceOrg": 16000,
        "oldbalanceDest": 500,
    }

    result = predictor.predict(transaction)

    assert "fraud_probability" in result
    assert "risk_level" in result
    assert "decision" in result
    assert "threshold" in result


def test_probability_range(predictor):
    transaction = {
        "step": 650,
        "type": "PAYMENT",
        "amount": 100,
        "oldbalanceOrg": 5000,
        "oldbalanceDest": 1000,
    }

    result = predictor.predict(transaction)

    assert 0 <= result["fraud_probability"] <= 1


def test_invalid_threshold(predictor):
    transaction = {
        "step": 650,
        "type": "TRANSFER",
        "amount": 12500,
        "oldbalanceOrg": 16000,
        "oldbalanceDest": 500,
    }

    with pytest.raises(ValueError):
        predictor.predict(
            transaction,
            threshold=1.5
        )