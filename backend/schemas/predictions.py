from typing import List, Optional

from pydantic import BaseModel


class PredictionResponse(BaseModel):
    symbol: Optional[str] = None
    bullish_probability: float
    bearish_probability: float
    neutral_probability: float
    confidence: float
    prediction: str
    risk_score: float
    model_version: str


class TrainingRequest(BaseModel):
    epochs: int = 50
    symbols: Optional[List[str]] = None


class TrainingStatus(BaseModel):
    is_training: bool
    current_epoch: int
    max_epochs: int
