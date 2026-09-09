from src.data.database import (
    SessionLocal,
    PredictionLog,
)


def log_prediction(
    transaction: dict,
    prediction: dict,
    model_version: str,
) -> int:

    db = SessionLocal()

    try:
        record = PredictionLog(
            step=transaction["step"],
            transaction_type=transaction["type"],
            amount=transaction["amount"],
            oldbalance_org=transaction[
                "oldbalanceOrg"
            ],
            oldbalance_dest=transaction[
                "oldbalanceDest"
            ],
            fraud_probability=prediction[
                "fraud_probability"
            ],
            risk_level=prediction[
                "risk_level"
            ],
            decision=prediction[
                "decision"
            ],
            threshold=prediction[
                "threshold"
            ],
            model_version=model_version,
        )

        db.add(record)
        db.commit()
        db.refresh(record)

        return record.id

    finally:
        db.close()

def get_recent_predictions(
    limit: int = 20
) -> list[dict]:

    db = SessionLocal()

    try:
        records = (
            db.query(PredictionLog)
            .order_by(PredictionLog.id.desc())
            .limit(limit)
            .all()
        )

        return [
            {
                "id": record.id,
                "timestamp": record.timestamp,
                "transaction_type": record.transaction_type,
                "amount": record.amount,
                "fraud_probability": record.fraud_probability,
                "risk_level": record.risk_level,
                "decision": record.decision,
                "threshold": record.threshold,
                "model_version": record.model_version,
            }
            for record in records
        ]

    finally:
        db.close()