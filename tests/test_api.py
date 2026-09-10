import os

os.environ["DATABASE_URL"] = "sqlite:///./test_finguard.db"

from fastapi.testclient import TestClient
from api.main import app

client = TestClient(app)


def test_health_endpoint():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {
        "status": "healthy",
        "model_loaded": True,
    }


def test_predict_endpoint():
    transaction = {
        "step": 650,
        "type": "TRANSFER",
        "amount": 12500,
        "oldbalanceOrg": 16000,
        "oldbalanceDest": 500,
    }

    response = client.post(
        "/predict",
        json=transaction,
    )

    assert response.status_code == 200

    data = response.json()

    assert "prediction_id" in data
    assert isinstance(data["prediction_id"], int)
    assert data["prediction_id"] > 0

    assert "fraud_probability" in data
    assert "risk_level" in data
    assert "decision" in data
    assert "threshold" in data

    assert 0 <= data["fraud_probability"] <= 1
    assert data["risk_level"] in [
        "LOW",
        "MEDIUM",
        "HIGH",
    ]
    assert data["decision"] in [
        "ALLOW",
        "REVIEW",
    ]


def test_invalid_transaction_type():
    transaction = {
        "step": 650,
        "type": "CRYPTO",
        "amount": 12500,
        "oldbalanceOrg": 16000,
        "oldbalanceDest": 500,
    }

    response = client.post(
        "/predict",
        json=transaction,
    )

    assert response.status_code == 422


def test_negative_amount_rejected():
    transaction = {
        "step": 650,
        "type": "TRANSFER",
        "amount": -500,
        "oldbalanceOrg": 16000,
        "oldbalanceDest": 500,
    }

    response = client.post(
        "/predict",
        json=transaction,
    )

    assert response.status_code == 422


def test_predictions_endpoint():
    response = client.get("/predictions")

    assert response.status_code == 200

    data = response.json()

    assert "count" in data
    assert "predictions" in data
    assert isinstance(data["predictions"], list)


def test_predictions_limit():
    response = client.get("/predictions?limit=5")

    assert response.status_code == 200

    data = response.json()

    assert data["count"] <= 5


def test_predictions_invalid_limit_too_low():
    response = client.get("/predictions?limit=0")

    assert response.status_code == 400


def test_predictions_invalid_limit_too_high():
    response = client.get("/predictions?limit=101")

    assert response.status_code == 400

def test_monitoring_endpoint():
    response = client.get("/monitoring")

    assert response.status_code == 200

    data = response.json()

    assert "total_predictions" in data
    assert "review_count" in data
    assert "review_rate" in data
    assert "average_fraud_probability" in data

    assert data["total_predictions"] >= 0
    assert data["review_count"] >= 0
    assert 0 <= data["review_rate"] <= 1
    assert 0 <= data["average_fraud_probability"] <= 1