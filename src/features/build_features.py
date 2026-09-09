import pandas as pd


FEATURE_COLUMNS = [
    "step",
    "amount",
    "oldbalanceOrg",
    "oldbalanceDest",
    "orig_balance_zero",
    "hour",
    "day",
    "type_CASH_IN",
    "type_CASH_OUT",
    "type_DEBIT",
    "type_PAYMENT",
    "type_TRANSFER",
]


TRANSACTION_TYPES = [
    "CASH_IN",
    "CASH_OUT",
    "DEBIT",
    "PAYMENT",
    "TRANSFER",
]


def build_features(transaction: dict) -> pd.DataFrame:
    """
    Convert a raw transaction into the feature representation
    expected by the FinGuard fraud detection model.
    """

    transaction_type = transaction["type"]

    if transaction_type not in TRANSACTION_TYPES:
        raise ValueError(
            f"Unsupported transaction type: {transaction_type}"
        )

    step = int(transaction["step"])
    amount = float(transaction["amount"])
    oldbalance_org = float(transaction["oldbalanceOrg"])
    oldbalance_dest = float(transaction["oldbalanceDest"])

    features = {
        "step": step,
        "amount": amount,
        "oldbalanceOrg": oldbalance_org,
        "oldbalanceDest": oldbalance_dest,

        "orig_balance_zero": int(
            oldbalance_org == 0
        ),

        "hour": (step - 1) % 24,
        "day": (step - 1) // 24,

        "type_CASH_IN": int(
            transaction_type == "CASH_IN"
        ),
        "type_CASH_OUT": int(
            transaction_type == "CASH_OUT"
        ),
        "type_DEBIT": int(
            transaction_type == "DEBIT"
        ),
        "type_PAYMENT": int(
            transaction_type == "PAYMENT"
        ),
        "type_TRANSFER": int(
            transaction_type == "TRANSFER"
        ),
    }

    return pd.DataFrame(
        [features],
        columns=FEATURE_COLUMNS
    )