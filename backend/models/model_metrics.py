from db.database import Base
from sqlalchemy import JSON, Boolean, Column, DateTime, Float, Integer, String
from sqlalchemy.sql import func


class ModelMetrics(Base):
    __tablename__ = "model_metrics"

    id = Column(Integer, primary_key=True, index=True)

    # Model identification
    model_version = Column(String, nullable=False, index=True)
    model_name = Column(String, nullable=False)

    # Training metrics
    epoch = Column(Integer, nullable=False)
    mse = Column(Float, nullable=False)
    mae = Column(Float, nullable=False)
    r2_score = Column(Float, nullable=False)
    learning_rate = Column(Float, nullable=False)
    gradient_norm = Column(Float, nullable=True)

    # Training metadata
    training_samples = Column(Integer, nullable=False)
    validation_samples = Column(Integer, nullable=True)
    training_duration_seconds = Column(Float, nullable=True)

    # Additional metrics as JSON
    additional_metrics = Column(JSON, nullable=True)

    # Status
    is_production = Column(Boolean, default=False, nullable=False)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<ModelMetrics(id={self.id}, version={self.model_version}, r2={self.r2_score})>"


class PredictionLog(Base):
    __tablename__ = "prediction_logs"

    id = Column(Integer, primary_key=True, index=True)

    # Prediction details
    model_version = Column(String, nullable=False, index=True)
    symbol = Column(String, nullable=False, index=True)

    # Prediction values
    bullish_probability = Column(Float, nullable=False)
    bearish_probability = Column(Float, nullable=False)
    neutral_probability = Column(Float, nullable=False)
    confidence = Column(Float, nullable=False)
    prediction = Column(String, nullable=False)  # BULL, BEAR, NEUTRAL
    risk_score = Column(Float, nullable=False)

    # Input features
    input_features = Column(JSON, nullable=True)

    # Actual outcome (for accuracy tracking)
    actual_outcome = Column(String, nullable=True)
    outcome_recorded_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    predicted_at = Column(DateTime(timezone=True), server_default=func.now())

    def __repr__(self):
        return f"<PredictionLog(id={self.id}, symbol={self.symbol}, prediction={self.prediction})>"
