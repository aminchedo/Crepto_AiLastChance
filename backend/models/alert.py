import enum

from db.database import Base
from sqlalchemy import (JSON, Boolean, Column, DateTime, Enum, Float,
                        ForeignKey, Integer, String)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func


class AlertType(str, enum.Enum):
    PRICE_ABOVE = "price_above"
    PRICE_BELOW = "price_below"
    PRICE_CHANGE = "price_change"
    AI_SIGNAL = "ai_signal"
    TECHNICAL_PATTERN = "technical_pattern"
    VOLUME_SPIKE = "volume_spike"


class AlertStatus(str, enum.Enum):
    ACTIVE = "active"
    TRIGGERED = "triggered"
    EXPIRED = "expired"
    DISABLED = "disabled"


class AlertChannel(str, enum.Enum):
    WEBSOCKET = "websocket"
    TELEGRAM = "telegram"
    EMAIL = "email"


class Alert(Base):
    __tablename__ = "alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)

    # Alert configuration
    symbol = Column(String, nullable=False, index=True)
    alert_type = Column(Enum(AlertType), nullable=False)
    status = Column(Enum(AlertStatus), default=AlertStatus.ACTIVE, nullable=False)

    # Conditions
    threshold_value = Column(Float, nullable=True)
    condition_params = Column(JSON, nullable=True)  # Additional parameters as JSON

    # Delivery channels
    channels = Column(JSON, nullable=False)  # List of AlertChannel values

    # Message
    message = Column(String, nullable=True)
    custom_message = Column(String, nullable=True)

    # Metadata
    trigger_count = Column(Integer, default=0, nullable=False)
    last_triggered_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)

    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    # Relationships
    user = relationship("User", back_populates="alerts")
    history = relationship(
        "AlertHistory", back_populates="alert", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"<Alert(id={self.id}, symbol={self.symbol}, type={self.alert_type})>"


class AlertHistory(Base):
    __tablename__ = "alert_history"

    id = Column(Integer, primary_key=True, index=True)
    alert_id = Column(Integer, ForeignKey("alerts.id"), nullable=False)

    # Trigger details
    triggered_value = Column(Float, nullable=True)
    message = Column(String, nullable=False)
    channels_sent = Column(JSON, nullable=False)

    # Delivery status
    delivery_status = Column(JSON, nullable=False)  # Status per channel

    # Timestamps
    triggered_at = Column(DateTime(timezone=True), server_default=func.now())

    # Relationships
    alert = relationship("Alert", back_populates="history")

    def __repr__(self):
        return f"<AlertHistory(id={self.id}, alert_id={self.alert_id})>"
