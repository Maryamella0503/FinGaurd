from pathlib import Path
import json

from xgboost import XGBClassifier

from src.features.build_features import build_features


PROJECT_ROOT = Path(__file__).resolve().parents[2]

MODEL_PATH = PROJECT_ROOT / "artifacts" / "finguard_xgb.json"
METADATA_PATH = PROJECT_ROOT / "artifacts" / "model_metadata.json"


class FinGuardPredictor:
    def __init__(self):
        self.model = XGBClassifier()
        self.model.load_model(MODEL_PATH)

        with open(METADATA_PATH, "r") as f:
            self.metadata = json.load(f)

        self.default_threshold = self.metadata[
            "default_policy_threshold"
        ]

    def predict(
        self,
        transaction: dict,
        threshold: float | None = None
    ) -> dict:

        if threshold is None:
            threshold = self.default_threshold

        if not 0 <= threshold <= 1:
            raise ValueError(
                "Threshold must be between 0 and 1."
            )

        features = build_features(transaction)

        fraud_probability = float(
            self.model.predict_proba(features)[0, 1]
        )

        if fraud_probability >= threshold:
            decision = "REVIEW"
        else:
            decision = "ALLOW"

        if fraud_probability < 0.30:
            risk_level = "LOW"
        elif fraud_probability < threshold:
            risk_level = "MEDIUM"
        else:
            risk_level = "HIGH"

        return {
            "fraud_probability": round(
                fraud_probability,
                6
            ),
            "risk_level": risk_level,
            "decision": decision,
            "threshold": threshold
        }