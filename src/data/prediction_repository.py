from sqlalchemy import func

from src.data.database import SessionLocal, PredictionLog


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

def get_prediction_metrics() -> dict:
    db = SessionLocal()

    try:
        total_predictions = db.query(func.count(PredictionLog.id)).scalar() or 0

        review_count = (
            db.query(func.count(PredictionLog.id))
            .filter(PredictionLog.decision == "REVIEW")
            .scalar()
            or 0
        )

        average_fraud_probability = (
            db.query(func.avg(PredictionLog.fraud_probability)).scalar()
            or 0.0
        )

        review_rate = (
            review_count / total_predictions
            if total_predictions > 0
            else 0.0
        )

        return {
            "total_predictions": total_predictions,
            "review_count": review_count,
            "review_rate": round(review_rate, 4),
            "average_fraud_probability": round(
                float(average_fraud_probability),
                6,
            ),
        }

    finally:
        db.close()