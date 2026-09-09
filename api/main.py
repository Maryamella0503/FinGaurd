from typing import Literal

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.models.predict import FinGuardPredictor
from src.data.database import create_tables
from src.data.prediction_repository import (
    log_prediction,
    get_recent_predictions,
)


app = FastAPI(
    title="FinGuard API",
    description=(
        "Machine-learning fraud risk scoring API "
        "for financial transactions."
    ),
    version="1.0.0",
)


predictor = FinGuardPredictor()

# Create database tables when the API starts
create_tables()


class TransactionRequest(BaseModel):
    step: int = Field(gt=0)

    type: Literal[
        "CASH_IN",
        "CASH_OUT",
        "DEBIT",
        "PAYMENT",
        "TRANSFER",
    ]

    amount: float = Field(ge=0)
    oldbalanceOrg: float = Field(ge=0)
    oldbalanceDest: float = Field(ge=0)


class PredictionResponse(BaseModel):
    fraud_probability: float
    risk_level: str
    decision: str
    threshold: float


@app.get("/")
def root():
    return {
        "service": "FinGuard",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "model_loaded": True,
    }

@app.get("/predictions")
def predictions(
    limit: int = 20
):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    records = get_recent_predictions(
        limit=limit
    )

    return {
        "count": len(records),
        "predictions": records,
    }

@app.post(
    "/predict",
    response_model=PredictionResponse,
)
def predict_fraud(
    transaction: TransactionRequest
):
    try:
        transaction_dict = transaction.model_dump()

        prediction = predictor.predict(
            transaction_dict
        )

        log_prediction(
            transaction=transaction_dict,
            prediction=prediction,
            model_version=predictor.metadata[
                "model_version"
            ],
        )

        return prediction

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc