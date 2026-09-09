from src.features.build_features import build_features


def test_transfer_feature_encoding():
    transaction = {
        "step": 650,
        "type": "TRANSFER",
        "amount": 12500,
        "oldbalanceOrg": 16000,
        "oldbalanceDest": 500,
    }

    result = build_features(transaction)

    assert result.shape == (1, 12)

    assert result.iloc[0]["type_TRANSFER"] == 1
    assert result.iloc[0]["type_CASH_OUT"] == 0
    assert result.iloc[0]["type_PAYMENT"] == 0

    assert result.iloc[0]["amount"] == 12500
    assert result.iloc[0]["oldbalanceOrg"] == 16000