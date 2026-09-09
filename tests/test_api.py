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