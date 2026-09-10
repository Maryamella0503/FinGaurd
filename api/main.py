from typing import Literal
from datetime import datetime

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from src.models.predict import FinGuardPredictor
from src.data.database import create_tables
from src.data.prediction_repository import (
    log_prediction,
    get_recent_predictions,
)

from src.data.prediction_repository import (
    log_prediction,
    get_recent_predictions,
    get_prediction_metrics,
)

app = FastAPI(
    title="FinGuard API",
    description="Machine-learning fraud risk scoring API for financial transactions.",
    version="1.0.0",
)

predictor = FinGuardPredictor()
create_tables()

class MonitoringResponse(BaseModel):
    total_predictions: int
    review_count: int
    review_rate: float
    average_fraud_probability: float

class TransactionRequest(BaseModel):
    step: int = Field(gt=0)
    type: Literal["CASH_IN", "CASH_OUT", "DEBIT", "PAYMENT", "TRANSFER"]
    amount: float = Field(ge=0)
    oldbalanceOrg: float = Field(ge=0)
    oldbalanceDest: float = Field(ge=0)


class PredictionResponse(BaseModel):
    prediction_id: int
    fraud_probability: float
    risk_level: str
    decision: str
    threshold: float

class PredictionHistoryItem(BaseModel):
    id: int
    timestamp: datetime
    transaction_type: str
    amount: float
    fraud_probability: float
    risk_level: str
    decision: str
    threshold: float
    model_version: str


class PredictionHistoryResponse(BaseModel):
    count: int
    predictions: list[PredictionHistoryItem]

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

@app.get("/monitoring", response_model=MonitoringResponse)
def monitoring():
    return get_prediction_metrics()

@app.get("/predictions", response_model=PredictionHistoryResponse)
def predictions(limit: int = 20):
    if limit < 1 or limit > 100:
        raise HTTPException(
            status_code=400,
            detail="Limit must be between 1 and 100.",
        )

    records = get_recent_predictions(limit=limit)

    return {
        "count": len(records),
        "predictions": records,
    }


@app.post("/predict", response_model=PredictionResponse)
def predict_fraud(transaction: TransactionRequest):
    try:
        transaction_dict = transaction.model_dump()
        prediction = predictor.predict(transaction_dict)

        prediction_id = log_prediction(
            transaction=transaction_dict,
            prediction=prediction,
            model_version=predictor.metadata["model_version"],
        )

        return {
            "prediction_id": prediction_id,
            **prediction,
        }

    except ValueError as exc:
        raise HTTPException(
            status_code=400,
            detail=str(exc),
        ) from exc